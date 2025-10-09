from dataclasses import dataclass
from typing import List
from torch.distributed import ProcessGroup
import torch.distributed as dist


@dataclass
class Group:
    ranks: list[int]
    process_group: ProcessGroup


class Topology:
    def __init__(self,
                 rank: int,
                 world_size: int,
                 local_world_size: int,
                 topology: str):
        """
        Initialize the Topology.
        Args:
            rank (int): The rank of the current process.
            world_size (int): Total number of processes.
            local_world_size (int): Number of processes in the local group.
            topology (str): Topology of the distributed system.
        """
        assert dist.is_initialized(), "torch.distributed is not initialized."

        self._rank = rank
        self._world_size = world_size
        self._local_world_size = local_world_size
        self._topology = topology

        self._groups_in_list: List[List[List[int]]] = self.assign_groups()
        self._groups: List[Group] = self.construct_groups()
    
    def assign_groups(self) -> List[List[List[int]]]:
        raise NotImplementedError("assign_groups method not implemented. Please implement in subclass.")
    
    def construct_groups(self) -> List[Group]:
        constructed = {}
        for rank in range(self._world_size):
            for i in range(len(self._groups_in_list[rank])):
                group_ranks = self._groups_in_list[rank][i]
                key = tuple(group_ranks)
                if key not in constructed:
                    new_group = dist.new_group(ranks=group_ranks)
                    constructed[key] = new_group
        groups = []
        for i in range(len(self._groups_in_list[self._rank])):
            group_ranks = self._groups_in_list[self._rank][i]
            key = tuple(group_ranks)
            groups.append(Group(ranks=group_ranks, process_group=constructed[key]))
        return groups

    def get_group(self, step: int) -> Group:
        return self._groups[step % len(self._groups)]


class RingTopology(Topology):
    def assign_groups(self) -> List[List[List[int]]]:
        assert self._world_size % 2 == 0, "World size must be even for RingTopology."
        groups = [[] for _ in range(self._world_size)]
        for rank in range(self._world_size):
            if rank % 2 == 0:
                groups[rank].append(sorted([rank, (rank + 1) % self._world_size]))
                groups[rank].append(sorted([rank, (rank - 1 + self._world_size) % self._world_size]))
            else:
                groups[rank].append(sorted([rank, (rank - 1 + self._world_size) % self._world_size]))
                groups[rank].append(sorted([rank, (rank + 1) % self._world_size]))
        return groups


class CompleteTopology(Topology):
    def assign_groups(self) -> List[List[List[int]]]:
        assert self._world_size > 1, "World size must be greater than 1 for CompleteTopology."
        groups = [[] for _ in range(self._world_size)]
        for rank in range(self._world_size):
            groups[rank].append(sorted(list(range(self._world_size))))
        return groups


class TopologyFactory:
    registry: dict[str, type[Topology]] = {
        'ring': RingTopology,
        'complete': CompleteTopology,
    }

    @classmethod
    def create(cls,
               topology: str,
               rank: int,
               world_size: int,
               local_world_size: int) -> Topology:
        topology_class = cls.registry.get(topology)
        if topology_class:
            return topology_class(rank, world_size, local_world_size, topology)
        else:
            raise ValueError(f"Topology '{topology}' is not supported.")
    
    @classmethod
    def add_topology(cls, name: str, topology_class: type):
        cls.registry[name] = topology_class

