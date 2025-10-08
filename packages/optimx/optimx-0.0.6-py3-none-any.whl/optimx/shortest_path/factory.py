import numpy as np
from typing import List, Tuple, Optional, Union, Dict
from .dijkstra import DijkstraSolver


class ShortestPathFactory:
    def __init__(self):
        self._available = {
            "dijkstra": DijkstraSolver,
        }

    def apply_solver(
        self,
        distance_matrix: np.ndarray,
        algorithm: str,
        start_node: int,
        goal_node: Optional[int],
        directed: bool = True,
    ) -> Union[
        Tuple[List[int], float],
        Tuple[Dict[int, float], List[int]]
    ]:
        if algorithm not in self._available:
            raise ValueError(
                f"Unknown algorithm '{algorithm}'. "
                f"Available algorithms are: {', '.join(self._available.keys())}"
            )
        solver = self._available[algorithm](
            distance_matrix, start_node, directed)
        return solver.solve(goal_node)
