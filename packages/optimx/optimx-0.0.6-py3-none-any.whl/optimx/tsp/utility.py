import numpy as np
from typing import List, Union, Optional


def calculate_tsp_distance_by_route(
        route: List[Union[str, int]], 
        distance_matrix: Union[List, np.ndarray],
        node_names: Optional[List[str]]=None
        ) -> float:
    """
    Calculate the total distance of a TSP route.

    Args:
        route (List[Union[str, int]]): The route to calculate the distance of.
        distance_matrix (Union[List, np.ndarray]): The distance matrix.
        node_names (Optional[List[str]], optional): The names of the nodes. Defaults to None.

    Returns:
        float: The total distance of the route.
    """
    
    if node_names:
        indexes = [node_names.index(node) for node in route]
    else:
        indexes = route
    
    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += distance_matrix[indexes[i]][indexes[i + 1]]
    
    return total_distance