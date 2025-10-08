import numpy as np
from typing import List ,Tuple
from .brute import TSPBrute
from .nearest import TSPNearestNeighbor
from .dynamic import TSPSolverMemoization
from .branch import TSPBranchBound


class TSPFactory:

    def __init__(self):
        self._available_solvers = {
            "brute": TSPBrute,
            "nearest_neighbor": TSPNearestNeighbor,
            "dynamic_programming": TSPSolverMemoization,
            "branch_and_bound": TSPBranchBound
        }

    def apply_solver(
            self, 
            distance_matrix: np.ndarray, 
            algorithm: str, 
            start_node: int, 
            cycle: bool=False
            ) -> Tuple[List[int], float]:
        
        if algorithm not in self._available_solvers:
            raise ValueError(f"Unknown algorithm '{algorithm}'. Available algorithms are: {', '.join(self._available_solvers.keys())}")
        
        solver = self._available_solvers[algorithm](distance_matrix, start_node, cycle)
        return solver.solve()
