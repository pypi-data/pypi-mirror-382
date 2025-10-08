from .brute import TSPBrute
from .nearest import TSPNearestNeighbor
from .dynamic import TSPSolverMemoization
from .branch import TSPSolverBranchAndBound

class TspSolver:

    def __init__(self):
        self._available_solvers = {
            "brute": TSPBrute,
            "nearest_neighbor": TSPNearestNeighbor,
            "dynamic_programming": TSPSolverMemoization,
            "branch_and_bound": TSPSolverBranchAndBound
        }

    def solve_problem(self, distance_matrix, algorithm, start_node=None, cycle=False):
        if algorithm not in self._available_solvers:
            raise ValueError(f"Unknown algorithm '{algorithm}'. Available algorithms are: {', '.join(self._available_solvers.keys())}")
        
        solver = self._available_solvers[algorithm](distance_matrix)
        return solver.solve(start_node=start_node, cycle=cycle)
