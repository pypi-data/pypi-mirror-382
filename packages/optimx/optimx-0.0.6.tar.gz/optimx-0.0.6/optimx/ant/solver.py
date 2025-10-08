import numpy as np
from typing import List, Tuple, Optional


class AntColonyOptimization:
    def __init__(
            self, 
            distances: np.ndarray,
            n_ants: int, 
            n_best: int, 
            n_iterations: int, 
            decay: float, 
            alpha: float=1, 
            beta: float=1, 
            Q: float=1
            ):
        self.distances = distances
        self.pheromone = np.ones(self.distances.shape) / len(distances)
        self.all_inds = list(range(len(distances)))
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        self.q = Q

    def solve_problem(self) -> List[Tuple[int, int]]:
        shortest_path = None
        all_time_shortest_path = ("placeholder", np.inf)

        for _ in range(self.n_iterations):
            all_paths = self._construct_colony_paths()

            self._spread_pheromone(all_paths, shortest_path=shortest_path)

            shortest_path = min(all_paths, key=lambda x: x[1])

            if shortest_path[1] < all_time_shortest_path[1]:
                all_time_shortest_path = shortest_path

            self.pheromone *= self.decay
        
        all_time_shortest_path = [(int(a), int(b)) for a, b in all_time_shortest_path[0]]
        return all_time_shortest_path
    
    def _construct_colony_paths(self) -> List[Tuple[List[Tuple[int, int]], int]]:
        all_paths = []
        for _ in range(self.n_ants):
            path = self._construct_path(0)
            all_paths.append((path, self._path_distance(path)))
        return all_paths
    
    def _construct_path(self, start: int) -> List[Tuple[int, int]]:
        path = []
        visited = set()
        visited.add(start)
        prev = start
        for _ in range(len(self.distances) - 1):
            move = self._pick_move(self.pheromone[prev], self.distances[prev], visited)
            path.append((prev, move))
            prev = move
            visited.add(move)
        path.append((prev, start))  # Returning to the start point
        return path
    
    def _path_distance(self, path: List[Tuple[int, int]]) -> float:
        return sum(self.distances[a, b] for a, b in path)

    def _spread_pheromone(
            self, 
            all_paths: List[Tuple[List[Tuple[int, int]], int]], 
            shortest_path: Optional[Tuple[List[Tuple[int, int]], int]] = None
            ) -> None:
        # Sort all paths by distance (ascending order)
        sorted_paths = sorted(all_paths, key=lambda x: x[1])
        
        # Update pheromones based on the top n_best paths
        for path, dist in sorted_paths[:self.n_best]:
            for move in path:
                self.pheromone[move] += self.q / dist

        # Optionally, add extra pheromone to the best path found so far
        if shortest_path:
            for move in shortest_path[0]:  # shortest_path[0] is the path, shortest_path[1] is the distance
                self.pheromone[move] += self.q / shortest_path[1]
        return

    def _pick_move(self, pheromone: np.ndarray, dist: np.ndarray, visited: set) -> int:
        pheromone = np.copy(pheromone)
        pheromone[list(visited)] = 0

        # Adding a small value to prevent division by zero
        dist = np.copy(dist)
        dist[dist == 0] = np.inf  # Use infinity to ensure zero-distance edges are not selected

        row = pheromone ** self.alpha * ((1.0 / dist) ** self.beta)
        if row.sum() == 0:
            row = np.ones_like(row)  # If all probabilities are zero, reset to uniform probabilities
        norm_row = row / row.sum()
        move = self.np_choice(self.all_inds, 1, p=norm_row)[0]
        return move
    
    @staticmethod
    def np_choice(choices: List[int], number: int, p: np.ndarray) -> np.ndarray:
        return np.random.choice(choices, number, p=p)