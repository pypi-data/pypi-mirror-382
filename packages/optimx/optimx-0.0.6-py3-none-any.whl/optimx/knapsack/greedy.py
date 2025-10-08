from .base import KnapsackSolver


class KnapsackGreedy(KnapsackSolver):

    def solve(self):
        # Compute ratio of value/weight for each item
        ratio = [v / w for v, w in zip(self.values, self.weights)]

        # Combine item data for sorting: (index, weight, value, ratio)
        indexed_data = list(enumerate(zip(self.weights, self.values, ratio)))
        # => [(0, (w0, v0, r0)), (1, (w1, v1, r1)), ...]

        # Sort items by descending ratio
        indexed_data.sort(key=lambda x: x[1][2], reverse=True)

        total_value = 0
        best_combination = []
        remaining_capacity = self.capacity

        for idx, (w, val, r) in indexed_data:
            # If this item can fit fully (no fractions in 0-1 knapsack)
            if w <= remaining_capacity:
                best_combination.append(idx)
                total_value += val
                remaining_capacity -= w

        # Sort the combination by item index if you prefer
        best_combination.sort()
        
        return best_combination, total_value
