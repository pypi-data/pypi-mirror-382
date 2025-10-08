from itertools import permutations
from typing import Tuple
from .base import TSPSolver


class TSPBrute(TSPSolver):

    def __init__(self, distance_matrix, start_node, cycle = True):
        super().__init__(distance_matrix, start_node, cycle)

    def solve(self):
        nodes = list(range(self.num_nodes))
        nodes.remove(self.start_node)
        
        shortest_distance = float("inf")
        best_route = None

        for route in permutations(nodes):
            # If a starting node is specified, prepend it to the route
            complete_route = (self.start_node,) + route if self.start_node is not None else route
            current_distance = self._calculate_route_distance(complete_route, return_to_start=self.cycle)

            if current_distance < shortest_distance:
                shortest_distance = current_distance
                best_route = complete_route

        if self.cycle:
            best_route = best_route + (best_route[0],)
        
        return list(best_route), shortest_distance
    
    def _calculate_route_distance(self, route: Tuple[int], return_to_start: bool=False) -> float:
        """Calculates the total distance of a given route based on the distance matrix."""
        total_distance = 0
        for i in range(len(route) - 1):
            total_distance += self.distance_matrix[route[i]][route[i + 1]]
        # If returning to the start, add the distance from the last node back to the first
        if return_to_start:
            total_distance += self.distance_matrix[route[-1]][route[0]]
        return total_distance