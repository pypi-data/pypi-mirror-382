from .brute import KnapsackBrute
from .dynamic import KnapsackDynamicProgram
from .greedy import KnapsackGreedy

class KnapsackSolver:

    def __init__(self):
        self._available_solvers = {
            "brute": KnapsackBrute,
            "greedy": KnapsackGreedy,
            "dynamic_programming": KnapsackDynamicProgram,
        }

    def solve_problem(self, weights, values, capacity, algorithm):
        if algorithm not in self._available_solvers:
            raise ValueError(f"Unknown algorithm '{algorithm}'. Available algorithms are: {', '.join(self._available_solvers.keys())}")
        
        solver = self._available_solvers[algorithm]()
        best_combination, max_value = solver.solve(weights, values, capacity)
        return best_combination, max_value