import string
import numpy as np
from numpy import ndarray
from typing import List, Union


def generate_node_names(distance_matrix: Union[List, ndarray]) -> List[str]:
    """Generates alphabetical node names based on the size of the distance matrix."""
    num_nodes = len(distance_matrix)
    alphabet = string.ascii_uppercase
    node_names = [alphabet[i] for i in range(num_nodes)]
    return node_names


def generate_square_distances(n_cities: int) -> ndarray:
    """Generates random distances between cities."""
    if n_cities < 2:
        raise ValueError("n_cities must be greater than 1")
    if not isinstance(n_cities, int):
        raise ValueError("n_cities must be an integer")
    
    distances = np.random.randint(1, 100, size=(n_cities, n_cities))
    distances = (distances + distances.T) / 2
    np.fill_diagonal(distances, 0)
    return distances