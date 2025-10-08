from typing import List ,Tuple
from .base import TSPSolver


class TSPSolverMemoization(TSPSolver):

    def __init__(self, distance_matrix, start_node, cycle = True):
        super().__init__(distance_matrix, start_node, cycle)
        self.memo = {}
        
    def solve(self):
        # Initialize the remaining nodes (excluding the start node)
        remaining_nodes = list(range(self.num_nodes))
        remaining_nodes.remove(self.start_node)

        # Reset memoization dictionary
        self.memo = {}

        # Solve the TSP with memoization
        min_distance, min_path = self._tsp_memoization_with_path(self.start_node, remaining_nodes, path=[self.start_node], cycle=self.cycle)

        # If cycle is True, add start node to the end to complete the cycle
        if self.cycle:
            min_path.append(self.start_node)
            
        return min_path, min_distance
    
    def _tsp_memoization_with_path(
            self, 
            current_node: int, 
            remaining_nodes: List[int], 
            path: List[int]=None, 
            cycle: bool=True
            ) -> Tuple[float, List[int]]:
        if path is None:
            path = []

        # Convert remaining_nodes to a tuple for use as a dictionary key
        remaining_nodes = tuple(remaining_nodes)
        
        # Check if this state has already been computed
        if (current_node, remaining_nodes) in self.memo:
            return self.memo[(current_node, remaining_nodes)], path
        
        # Base case: no remaining nodes to visit
        if not remaining_nodes:
            # Return to start node if cycle is True
            final_distance = self.distance_matrix[current_node][path[0]] if cycle else 0
            return final_distance, path

        min_distance = float('inf')
        min_path = None
        
        # Recursive case: try visiting each remaining node
        for i in range(len(remaining_nodes)):
            next_node = remaining_nodes[i]
            new_remaining_nodes = remaining_nodes[:i] + remaining_nodes[i+1:]
            # Recur with the next node
            d, p = self._tsp_memoization_with_path(next_node, new_remaining_nodes, path + [next_node], cycle)
            d += self.distance_matrix[current_node][next_node]
            
            # Update minimum distance and path
            if d < min_distance:
                min_distance = d
                min_path = p

        # Memoize the result
        self.memo[(current_node, remaining_nodes)] = min_distance

        return min_distance, min_path

    
