import numpy as np
from .base import TSPSolver


class TSPBranchBound(TSPSolver):

    def __init__(self, distance_matrix, start_node, cycle = True):
        super().__init__(distance_matrix, start_node, cycle)
        self.best_path = None
        self.best_cost = np.inf
        
    def solve(self):
        # Reset best path and cost for fresh solving
        self.best_path = None
        self.best_cost = np.inf

        # Initialize the stack with the root node
        stack = [(self.start_node, [self.start_node], {self.start_node}, 0)]
        
        while stack:
            current_node, path, visited, current_cost = stack.pop()
            
            # If all nodes have been visited, check if this path is the best
            if len(path) == self.num_nodes:
                if self.cycle:
                    # Complete the cycle by returning to the start node
                    current_cost += self.distance_matrix[path[-1]][self.start_node]
                if current_cost < self.best_cost:
                    self.best_path = path + ([self.start_node] if self.cycle else [])
                    self.best_cost = current_cost
            else:
                # Generate children nodes by considering all unvisited nodes
                unvisited = set(range(self.num_nodes)) - visited
                for next_node in unvisited:
                    new_path = path + [next_node]
                    new_cost = current_cost + self.distance_matrix[current_node][next_node]
                    
                    # Prune paths that exceed the current best cost
                    if new_cost < self.best_cost:
                        stack.append((next_node, new_path, visited | {next_node}, new_cost))
        
        return self.best_path, self.best_cost
