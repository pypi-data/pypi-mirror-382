from typing import List, Tuple
from ..bases.solver import ASolver


class KnapsackSolver(ASolver):

    def __init__(self, weights: List[float | int], values: List[float | int], capacity: int):
        self.weights = weights
        self.values = values
        self.capacity = capacity

    def solve(self) -> Tuple[List[int], float]:
        raise NotImplementedError("This method must be implemented in a subclass.")