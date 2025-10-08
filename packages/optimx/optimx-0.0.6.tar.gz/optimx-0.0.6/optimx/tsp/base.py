import numpy as np
from typing import List ,Tuple
from ..bases.solver import ASolver


class TSPSolver(ASolver):

    def __init__(self, distance_matrix: np.ndarray, start_node: int, cycle: bool=True):
        self.distance_matrix = distance_matrix
        self.num_nodes = len(distance_matrix)
        self.start_node = start_node
        self.cycle = cycle

    def solve(self) -> Tuple[List[int], float]:
        raise NotImplementedError("This method must be implemented in a subclass.")