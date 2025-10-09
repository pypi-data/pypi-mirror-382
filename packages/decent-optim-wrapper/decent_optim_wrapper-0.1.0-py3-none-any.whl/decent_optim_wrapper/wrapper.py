import torch
import torch.distributed as dist
from torch.optim import Optimizer
from torch.distributed import Work
from loguru import logger
from typing import List, cast
from decent_optim_wrapper.topo import TopologyFactory, Topology


class DecentOptimWrapper(Optimizer):
    def __init__(self,
                 optimizer: Optimizer,
                 rank: int,
                 world_size: int,
                 local_world_size: int,
                 topology: str,
                 bucket_cap_mb: int = 25):
        """
        Initialize the DecentOptimWrapper.
        Args:
            optimizer (Optimizer): The optimizer to wrap.
            rank (int): The rank of the current process.
            world_size (int): Total number of processes.
            local_world_size (int): Number of processes in the local group.
            topology (str): Topology of the distributed system.
        """

        super(DecentOptimWrapper, self).__init__(optimizer.param_groups, optimizer.defaults)

        assert dist.is_initialized(), "torch.distributed is not initialized."

        self._optimizer = optimizer
        self._rank = rank
        self._world_size = world_size
        self._local_world_size = local_world_size
        self._topology = topology
        self._bucket_cap_mb = bucket_cap_mb
        self._param_buckets = []
        self._comm_buckets = []
        self._backup_buckets = []
        self._backup_comm_ops = []

        self._params = [param for group in optimizer.param_groups for param in group['params']]
        self._construct_buckets()
        self._synchronize_buckets()
        self._topo: Topology = TopologyFactory.create(self._topology, self._rank, self._world_size, self._local_world_size)
        self._comm_ops: List[Work] = []
        self._step = 0


    @torch.no_grad()
    def _construct_buckets(self):
        size = 0
        params_in_bucket: List[torch.nn.Parameter] = []
        for i, param in enumerate(self._params):
            param_size = self._align(param)
            params_in_bucket.append(param)
            size += param_size
            if (size >= self._bucket_cap_mb * 1024 * 1024 / self._params[0].element_size()) or (i == len(self._params) - 1):
                block = torch.zeros(size, dtype=self._params[0].dtype, device=self._params[0].device)
                comm_block = torch.zeros(size, dtype=self._params[0].dtype, device=self._params[0].device)
                backup_block = torch.zeros(size, dtype=self._params[0].dtype, device=self._params[0].device)
                self._param_buckets.append(block)
                self._comm_buckets.append(comm_block)
                self._backup_buckets.append(backup_block)
                
                offset = 0
                for p in params_in_bucket:
                    block.narrow(0, offset, p.numel()).view_as(p.data).copy_(p.data)
                    p.data = block.narrow(0, offset, p.numel()).view_as(p.data)
                    offset += self._align(p)
                
                size = 0
                params_in_bucket = []
        
        logger.debug(f"Constructed {len(self._param_buckets)} buckets for parameters.")


    @torch.no_grad()
    def _synchronize_buckets(self):
        for bucket in self._param_buckets:
            dist.broadcast(bucket, src=0)
        logger.debug("Synchronized parameter buckets across all processes.")


    @torch.no_grad()
    def step(self, closure=None) -> None:  # type: ignore
        assert closure is None, "Closure is not supported in DecentOptimWrapper."

        if self._comm_ops:
            for i in range(len(self._comm_ops)):
                self._comm_ops[i].wait()
                self._param_buckets[i].copy_(self._comm_buckets[i])

            self._comm_ops = []

        self._optimizer.step()

        group = self._topo.get_group(self._step)
        torch._foreach_copy_(self._comm_buckets, self._param_buckets)
        torch._foreach_mul_(self._comm_buckets, 1.0 / len(group.ranks))
        for i in range(len(self._param_buckets)):
            self._comm_ops.append(
                cast(Work, dist.all_reduce(
                    self._comm_buckets[i],
                    op=dist.ReduceOp.SUM,
                    group=group.process_group,
                    async_op=True
                ))
            )
        self._step += 1


    def _align(self, param: torch.nn.Parameter | torch.Tensor) -> int:
        return ((param.numel() + 31) // 32) * 32


    @torch.no_grad()
    def global_avg(self, may_revert: bool = True):
        if self._comm_ops:
            for op in self._comm_ops:
                op.wait()
            self._backup_comm_ops = self._comm_ops
            self._comm_ops = []
        
        torch._foreach_copy_(self._backup_buckets, self._param_buckets)
        torch._foreach_mul_(self._param_buckets, 1.0 / self._world_size)
        for i in range(len(self._param_buckets)):
            dist.all_reduce(self._param_buckets[i], op=dist.ReduceOp.SUM)
        
    
    @torch.no_grad()
    def revert_global_avg(self):
        self._comm_ops = self._backup_comm_ops
        torch._foreach_copy_(self._param_buckets, self._backup_buckets)
        self._backup_comm_ops = []


    def zero_grad(self, set_to_none: bool = True) -> None:
        self._optimizer.zero_grad(set_to_none=set_to_none)
