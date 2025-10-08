import math
import numpy as np
from typing import List ,Tuple
from .base import TSPSolver


class TSPNearestNeighbor(TSPSolver):

    def __init__(self, distance_matrix, start_node, cycle = True):
        super().__init__(distance_matrix, start_node, cycle)

    def solve(self):
        visited = [False] * self.num_nodes
        tour = []
        total_distance = 0

        # Start at the specified node
        current_node = self.start_node
        tour.append(current_node)
        visited[current_node] = True

        # Repeat until all nodes have been visited
        while len(tour) < self.num_nodes:
            nearest_node = None
            nearest_distance = math.inf

            # Find the nearest unvisited node
            for node in range(self.num_nodes):
                if not visited[node]:
                    distance = self.distance_matrix[current_node][node]
                    if distance < nearest_distance:
                        nearest_node = node
                        nearest_distance = distance

            # Move to the nearest node
            current_node = nearest_node
            tour.append(current_node)
            visited[current_node] = True
            total_distance += nearest_distance

        # If cycle is True, complete the tour by returning to the starting node
        if self.cycle:
            tour.append(self.start_node)
            total_distance += self.distance_matrix[current_node][self.start_node]

        return tour, total_distance