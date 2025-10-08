import heapq
import numpy as np
from typing import List, Tuple, Dict, Optional, Union
from .base import ShortestPathSolver


class DijkstraSolver(ShortestPathSolver):

    def solve(self, goal_node: Optional[int] = None) -> Union[Tuple[List[int], float], Tuple[Dict[int, float], List[int]]]:
        n = self.num_nodes

        dist = {i: float("inf") for i in range(n)}
        parent = [-1] * n

        dist[self.start_node] = 0.0
        pq: List[Tuple[float, int]] = [(0.0, self.start_node)]

        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            if goal_node is not None and u == goal_node:
                break

            # Relax all neighbors v of u
            for v in range(n):
                w = self.distance_matrix[u, v]
                if u == v:
                    continue
                if not np.isfinite(w) or w < 0:
                    # skip absent edges and negative weights
                    continue

                nd = d + float(w)
                if nd < dist[v]:
                    dist[v] = nd
                    parent[v] = u
                    heapq.heappush(pq, (nd, v))

        if goal_node is not None:
            if not np.isfinite(dist[goal_node]):
                return [], float("inf")
            path = self._reconstruct_path(parent, goal_node)
            return path, float(dist[goal_node])

        return dist, parent

    def _reconstruct_path(self, parent: List[int], t: int) -> List[int]:
        path = []
        while t != -1:
            path.append(t)
            t = parent[t]
        return path[::-1]
