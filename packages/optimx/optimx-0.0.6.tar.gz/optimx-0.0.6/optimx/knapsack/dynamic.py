from typing import List, Tuple
from .base import KnapsackSolver


class KnapsackDynamicProgram(KnapsackSolver):

    def solve(self):
        max_value, dp = self._knapsack_max_value()
        best_combination = self._find_included_items(dp)
        return best_combination, max_value
        

    def _knapsack_max_value(self) -> Tuple[float|int, List[List[float|int]]]:
        n = len(self.weights)
        dp = [[0 for _ in range(self.capacity + 1)] for _ in range(n + 1)]

        # Fill the DP table
        for i in range(1, n + 1):
            for w in range(1, self.capacity + 1):
                if self.weights[i - 1] <= w:
                    dp[i][w] = max(dp[i - 1][w], self.values[i - 1] + dp[i - 1][w - self.weights[i - 1]])
                else:
                    dp[i][w] = dp[i - 1][w]

        max_value = dp[n][self.capacity]
        return max_value, dp
                          
    
    def _find_included_items(self, dp: List[List[float|int]]) -> List[int]:
        n = len(self.weights)
        W = len(dp[0]) - 1
        included_items = []
        i, w = n, W

        while i > 0 and w > 0:
            if dp[i][w] != dp[i - 1][w]:
                included_items.append(i)
                w -=self. weights[i - 1]
            i -= 1

        included_items.reverse()
        included_items = [item - 1 for item in included_items]

        return included_items
