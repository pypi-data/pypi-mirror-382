import numpy as np
from numpy import ndarray
from typing import List, Union, Optional, Literal, Dict, Tuple
from .tsp.factory import TSPFactory
from .tsp.visual import TSPVisualizer
from .knapsack.factory import KnapsackFactory
from .ant.solver import AntColonyOptimization
from .shortest_path.factory import ShortestPathFactory


def solve_tsp(
        distance_matrix: Union[List, ndarray],
        algorithm: Literal["brute", "nearest_neighbour",
                           "dynamic_programming", "branch_and_bound"] = "dynamic_programming",
        node_names: Optional[List[str]] = None,
        start_node: Optional[Union[int, str]] = None,
        cycle: bool = False
) -> Tuple[List[Union[int, str]], float]:
    """
    Solve the Travelling Salesman Problem (TSP) using the specified algorithm.

    Args:
        distance_matrix (Union[List, ndarray]): A square matrix representing the distances between nodes.
        algorithm (Literal[brute, nearest_neighbour, dynamic_programming, branch_and_bound], optional): The algorithm to use.
        node_names (Optional[List[str]], optional): The names of the nodes. Defaults to None.
        start_node (Optional[Union[int, str]], optional): The starting node. Defaults to None. If None, the first node is used.
        cycle (bool, optional): Whether to return to the starting node. Defaults to False.

    Returns:
        Tuple[List[Union[int, str]], float]: The best route and the total distance.

    Examples:
        >>> distance_matrix = [
        ...     [0, 10, 15, 20],
        ...     [10, 0, 35, 25],
        ...     [15, 35, 0, 30],
        ...     [20, 25, 30, 0]
        ... ]
        >>> solve_tsp(distance_matrix, algorithm="brute")
        ([0, 1, 3, 2], 65.0

    """

    if not isinstance(distance_matrix, (list, ndarray)):
        raise ValueError("distance_matrix must be a list or numpy array")

    if isinstance(distance_matrix, list):
        distance_matrix = np.array(distance_matrix)

    if distance_matrix.shape[0] != distance_matrix.shape[1]:
        raise ValueError("distance_matrix must be a square matrix")

    if not isinstance(algorithm, str):
        raise ValueError("algorithm must be a string")

    if node_names is not None:
        if not isinstance(node_names, list):
            raise ValueError("node_names must be a list")
        if len(node_names) != distance_matrix.shape[0]:
            raise ValueError(
                "node_names must have the same length as distance_matrix")

    if start_node is not None:
        if isinstance(start_node, int):
            if start_node < 0 or start_node >= distance_matrix.shape[0]:
                raise ValueError("start_node must be a valid index")
        elif isinstance(start_node, str):
            if start_node not in node_names:
                raise ValueError("start_node must be a valid node name")
            else:
                start_node = node_names.index(start_node)
        else:
            raise ValueError("start_node must be an integer or string")
    else:
        start_node = 0

    if not isinstance(cycle, bool):
        raise ValueError("cycle must be a boolean")

    factory = TSPFactory()
    best_route, best_cost = factory.apply_solver(
        distance_matrix, algorithm, start_node, cycle)

    if node_names:
        best_route = [node_names[i] for i in best_route]

    return best_route, float(best_cost)


def plot_tsp_route(
        route: List[Union[str, int]],
        node_names: Optional[List[str]] = None,
        node_coordinates: Optional[dict] = None,
        start_node: Optional[Union[int, str]] = None,
        cycle: bool = False
) -> None:
    """
    Plot a TSP route.

    Args:
        route (List[Union[str, int]]): The route to plot. Example: [0, 1, 2, 3]
        node_names (Optional[List[str]], optional): The names of the nodes. Defaults to None.
        node_coordinates (Optional[dict], optional): The coordinates of the nodes. Defaults to None.
        start_node (Optional[Union[int, str]], optional): The starting node. Defaults to None.
        cycle (bool, optional): Whether the route contains a cycle. Defaults to False.

    Examples:
        >>> route = [0, 1, 3, 2]
        >>> node_names = ["A", "B", "C", "D"]
        >>> node_coordinates = {"A": (0, 0), "B": (1, 1), "C": (2, 0), "D": (1, -1)}
        >>> plot_tsp_route(route, node_names, node_coordinates, start_node="A", cycle=False)
    """

    if not isinstance(cycle, bool):
        raise ValueError("cycle must be a boolean")

    if cycle:
        route = route[:-1]
    if start_node is None:
        if node_names:
            start_node = node_names[0]
        else:
            start_node = 0

    plotter = TSPVisualizer(
        route, node_names, node_coordinates, start_node, cycle)
    plotter.plot()

    return


def solve_knapsack(
        weights: List[float],
        values: List[float],
        capacity: float,
        algorithm: Literal["brute", "greedy",
                           "dynamic_programming"] = "dynamic_programming"
) -> Tuple[List[int], float]:
    """
    Solve the 0-1 Knapsack Problem using the specified algorithm.

    Args:
        weights (List[float]): Weights of the items. Must be the same length as values.
        values (List[float]):  Values of the items. Must be the same length as weights.
        capacity (float): The maximum weight that the knapsack can hold.
        algorithm (Literal[brute, greedy, dynamic_programming], optional): The algorithm to use. Defaults to dynamic_programming.

    Returns:
        Tuple[List[int], float]: The indices of the items to include in the knapsack and the total value.

    Examples:
        >>> weights = [2, 3, 4, 5]
        >>> values = [3, 4, 5, 6]
        >>> capacity = 5
        >>> solve_knapsack(weights, values, capacity, algorithm="greedy")
        ([0, 1], 7)
    """

    if not isinstance(weights, list):
        raise ValueError("weights must be a list")

    if not isinstance(values, list):
        raise ValueError("values must be a list")

    if not isinstance(capacity, (int, float)):
        raise ValueError("capacity must be an integer or float")

    if not isinstance(algorithm, str):
        raise ValueError("algorithm must be a string")

    factory = KnapsackFactory()
    best_combination, max_value = factory.apply_solver(
        weights, values, capacity, algorithm)

    if not isinstance(best_combination, list):
        best_combination = list(best_combination)

    return best_combination, max_value


def solve_ant_colony(
        distance_matrix: ndarray,
        n_ants: int,
        n_best: int,
        n_iterations: int,
        decay: float,
        alpha: float = 1,
        beta: float = 1,
        Q: float = 1
) -> List[Tuple[int, int]]:
    """
    Solve the Travelling Salesman Problem using Ant Colony Optimization.

    Args:
        distance_matrix (ndarray): A square matrix representing the distances between nodes.
        n_ants (int): The number of ants to use.
        n_best (int): The number of best ants to deposit pheromone.
        n_iterations (int): The number of iterations to run.
        decay (float): The pheromone decay rate.
        alpha (float, optional): A parameter for the pheromone influence. Defaults to 1.
        beta (float, optional): A parameter for the distance influence. Defaults to 1.
        Q (float, optional): A parameter for the pheromone update. Defaults to 1.

    Returns:
        List[Tuple[int, int]]: The best route found by the algorithm.
    """

    if not isinstance(distance_matrix, np.ndarray):
        raise TypeError("distances must be a NumPy array.")
    if distance_matrix.shape[0] != distance_matrix.shape[1]:
        raise ValueError("Distance matrix must be square.")
    if np.any(distance_matrix < 0):
        raise ValueError("Distances cannot be negative.")
    if not (0 < decay <= 1):
        raise ValueError("Decay must be in the range (0, 1].")
    if any(param <= 0 for param in [n_ants, n_best, n_iterations]):
        raise ValueError(
            "n_ants, n_best, and n_iterations must be positive integers.")

    solver = AntColonyOptimization(
        distance_matrix, n_ants, n_best, n_iterations, decay, alpha, beta, Q)
    shortest_path = solver.solve_problem()
    return shortest_path


def solve_shortest_path(
    distance_matrix: Union[List, np.ndarray],
    start_node: Union[int, str],
    goal_node: Optional[Union[int, str]] = None,
    node_names: Optional[List[str]] = None,
    algorithm: str = "dijkstra",
    directed: bool = True,
) -> Union[
    # (path, distance) if goal_node provided
    Tuple[List[Union[int, str]], float],
    # (dist_map, parent_list) otherwise
    Tuple[Dict[Union[int, str], float], List[Union[int, str]]]
]:
    """
    Solve single-source shortest paths using Dijkstra.

    - distance_matrix: square matrix; use np.inf for missing edges.
    - start_node, goal_node: index or name (if node_names is provided).
    - directed: if False, treat as undirected by mirroring matrix before solve.
    """

    # validate matrix
    if isinstance(distance_matrix, list):
        distance_matrix = np.array(distance_matrix, dtype=float)
    if distance_matrix.shape[0] != distance_matrix.shape[1]:
        raise ValueError("distance_matrix must be square")

    n = distance_matrix.shape[0]

    # optional undirected conversion
    if not directed:
        distance_matrix = np.minimum(distance_matrix, distance_matrix.T)

    # map names <-> indices
    def to_index(x):
        if isinstance(x, int):
            return x
        if isinstance(x, str):
            if node_names is None:
                raise ValueError(
                    "node_names must be provided when using node names")
            try:
                return node_names.index(x)
            except ValueError:
                raise ValueError(f"Unknown node name: {x}")
        raise ValueError("node must be int or str")

    s = to_index(start_node)
    t = to_index(goal_node) if goal_node is not None else None
    if not (0 <= s < n) or (t is not None and not (0 <= t < n)):
        raise ValueError("start/goal index out of range")

    factory = ShortestPathFactory()
    result = factory.apply_solver(distance_matrix, algorithm, s, t, directed)

    # map back to names if provided
    if node_names is None:
        return result

    if t is not None:
        path, dist = result
        return [node_names[i] for i in path], dist
    else:
        dist_map, parent = result
        named_dist = {node_names[i]: d for i, d in dist_map.items()}
        named_parent = [node_names[p] if p != -1 else None for p in parent]
        return named_dist, named_parent
