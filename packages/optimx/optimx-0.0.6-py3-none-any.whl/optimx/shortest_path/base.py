import numpy as np
from typing import List, Optional, Tuple, Union, Dict
from ..bases.solver import ASolver


class ShortestPathSolver(ASolver):

    def __init__(self, distance_matrix: np.ndarray, start_node: int, directed: bool = True):
        self.distance_matrix = distance_matrix
        self.num_nodes = distance_matrix.shape[0]
        self.start_node = start_node
        self.directed = directed

    def solve(self, goal_node: Optional[int] = None) -> Union[Tuple[List[int], float], Tuple[Dict[int, float], List[int]]]:
        raise NotImplementedError(
            "This method must be implemented in a subclass.")
