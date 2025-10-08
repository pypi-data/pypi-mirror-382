from itertools import combinations
from .base import KnapsackSolver


class KnapsackBrute(KnapsackSolver):

    def solve(self):
        n = len(self.weights)
        max_value = 0
        best_combination = []

        for r in range(1, n + 1):
            for combination in combinations(range(n), r):
                total_weight = sum(self.weights[i] for i in combination)
                total_value = sum(self.values[i] for i in combination)

                if total_weight <= self.capacity and total_value > max_value:
                    max_value = total_value
                    best_combination = combination

        return best_combination, max_value