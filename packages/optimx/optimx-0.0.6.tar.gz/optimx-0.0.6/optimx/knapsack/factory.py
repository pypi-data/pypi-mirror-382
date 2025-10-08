from typing import List, Tuple
from .brute import KnapsackBrute
from .dynamic import KnapsackDynamicProgram
from .greedy import KnapsackGreedy


class KnapsackFactory:

    def __init__(self):
        self._available_solvers = {
            "brute": KnapsackBrute,
            "greedy": KnapsackGreedy,
            "dynamic_programming": KnapsackDynamicProgram,
        }

    def apply_solver(
            self, 
            weights: List[float | int], 
            values: List[float | int], 
            capacity: int,
            algorithm: str
            ) -> Tuple[List[int], float]:
        
        if algorithm not in self._available_solvers:
            raise ValueError(f"Unknown algorithm '{algorithm}'. Available algorithms are: {', '.join(self._available_solvers.keys())}")
        
        solver = self._available_solvers[algorithm](weights, values, capacity)
        
        best_combination, max_value = solver.solve()

        return best_combination, max_value