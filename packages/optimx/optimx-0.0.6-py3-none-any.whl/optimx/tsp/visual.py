import numpy as np
import matplotlib.pyplot as plt
from typing import List, Union, Optional


class TSPVisualizer:

    def __init__(
            self, 
            route: List[Union[str, int]], 
            node_names: Optional[List[str]],
            node_coordinates: Optional[dict],
            start_node: Optional[Union[int, str]], 
            cycle: bool
            ):
        
        if node_names:
            self.route = [node_names.index(node) for node in route]
        else:
            self.route = route
        self.node_names = node_names if node_names is not None else list(range(len(self.route)))
        self.node_coordinates = node_coordinates if node_coordinates is not None else \
                                    self._generate_node_coordinates()
        self.cycle = cycle    
        self.start_node = start_node if start_node is not None else 0

        if len(self.route) != len(self.node_coordinates):
            raise ValueError("route and node_coordinates must have the same length")

        if isinstance(self.start_node, int):
            if self.start_node < 0 or self.start_node >= len(route):
                raise ValueError("start_node must be a valid index")
        elif isinstance(self.start_node, str):
            if self.start_node not in self.node_names:
                raise ValueError("start_node must be a valid node name")
            else:
                self.start_node = node_names.index(self.start_node)
        else:
            raise ValueError("start_node must be an integer or string")

            
    def plot(self) -> None:
        # Extract x and y coordinates for each node in the route
        x_coords = [self.node_coordinates[self.node_names[i]][0] for i in self.route]
        y_coords = [self.node_coordinates[self.node_names[i]][1] for i in self.route]
        
        # If cycle is True, complete the loop bye returning to the starting point
        if self.cycle:
            x_coords.append(x_coords[0])
            y_coords.append(y_coords[0])
        
        plt.figure(figsize=(8, 6))
        
        # Plot each segment with an arrow and label the order
        for i in range(len(self.route) - (0 if self.cycle else 1)):
            plt.plot(
                [x_coords[i], x_coords[i + 1]], 
                [y_coords[i], y_coords[i + 1]], 
                marker='o', 
                color='b', 
                markersize=8
            )
            plt.annotate(
                f'{i+1}', 
                (x_coords[i], y_coords[i]), 
                textcoords="offset points", 
                xytext=(5, 5), 
                ha='center', 
                fontsize=10, 
                color='red'
            )
        
        # Add arrows to show direction between nodes
        for i in range(len(self.route) - (0 if self.cycle else 1)):
            plt.arrow(
                x_coords[i], y_coords[i], 
                x_coords[i + 1] - x_coords[i], y_coords[i + 1] - y_coords[i],
                head_width=0.05, length_includes_head=True, color='blue'
            )

        start_x, start_y = self.node_coordinates[self.node_names[self.start_node]]
        plt.plot(start_x, start_y, marker='o', color='green', markersize=10, label="Start Node")
        plt.annotate(
            'Start', 
            (start_x, start_y), 
            textcoords="offset points", 
            xytext=(5, 5), 
            ha='center', 
            fontsize=12, 
            color='green'
        )
        
        # Label each node with its name
        for i in range(len(self.route)):
            label = self.node_names[self.route[i]]
            plt.text(self.node_coordinates[label][0], self.node_coordinates[label][1], label, fontsize=12, ha='right')
        
        plt.title("TSP Route")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.grid()
        plt.show()
        plt.close()
        return
    
    def _generate_node_coordinates(self) -> dict:
        """Generates coordinates for nodes in a circular layout."""
        num_nodes = len(self.route)
        angle = 2 * np.pi / num_nodes
        return {self.node_names[i]: (np.cos(i * angle), np.sin(i * angle)) for i in range(num_nodes)}

