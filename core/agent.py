"""
Core Agent Module
Implements the Goal-Based Agent logic.
Focuses on Modularity, Testability, and Code Readability.
"""
import random
import logging
import heapq
from dataclasses import dataclass
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any

try:
    from .config import settings
    from .loader import loader
except ImportError:
    from config import settings
    from loader import loader

logger = logging.getLogger(__name__)

@dataclass
class RouteResult:
    """Standardized result object for route queries."""
    path: List[str]
    cost: float

class GoalBasedAgent:
    """
    Intelligent agent for mesh network navigation.
    Decoupled from Flask to ensure High Cohesion and Low Coupling.
    """
    def __init__(self):
        self.nodes = settings.NODES
        self.connections = settings.CONNECTIONS
        self.edge_data: Dict[str, Dict[str, Any]] = {}
        # Initialize network state
        self.randomize_network()
        # Ensure models are loaded
        loader.load_resources()

    def randomize_network(self) -> None:
        """
        Generates stochastic properties for the network edges.
        Simulates dynamic environment conditions.
        """
        data = {}
        for u, v in self.connections:
            # Simulate environment metrics
            edge_info = {
                'distance': random.randint(10, 100),
                'traffic': random.randint(0, 100),
                'quality': random.randint(1, 10),
                # 10% chance of road blockage
                'blocked': "Yes" if random.random() < 0.1 else "No"
            }
            # Undirected graph: Edges are bidirectional
            data[f"{u}-{v}"] = edge_info
            data[f"{v}-{u}"] = edge_info 
        
        self.edge_data = data
        logger.info("Network environment randomized.")

    def _predict_cost(self, start: str, end: str, model_type: str = 'linear') -> float:
        """
        Internal method to predict traversal cost/utility.
        Uses the loaded ML models via the Loader service.
        """
        key = f"{start}-{end}"
        if key not in self.edge_data:
            return float('inf')
        
        data = self.edge_data[key]
        if data['blocked'] == "Yes":
            return float('inf')
        
        # Prepare feature vector matching training schema
        features = pd.DataFrame([{
            'distance': data['distance'],
            'traffic': data['traffic'],
            'quality_inv': 11 - data['quality']
        }])
        
        try:
            model = loader.get_model(model_type)
            if not model:
                logger.error("Model type '%s' not available.", model_type)
                return float('inf')
            
            cost = max(0.0, model.predict(features)[0])
            return round(float(cost), 2)
        except (ValueError, IndexError, AttributeError) as e:
            logger.error("Prediction failed for %s->%s: %s", start, end, str(e))
            return float('inf')

    def find_best_route(self, start: str, dest: str, model_type: str = 'linear') -> Tuple[Optional[Dict[str, Any]], List[str]]:
        """
        Executes Dijkstra's algorithm to find the optimal path.
        Traverses the graph based on costs predicted by the ML model.
        """
        logs = []
        logs.append(f"Goal: {start} -> {dest} | Strategy: Dijkstra | Model: {model_type.upper()}")
        
        if start not in self.nodes or dest not in self.nodes:
             logs.append(f"Error: Start or Destination node invalid. Valid nodes: {self.nodes}")
             return None, logs

        if start == dest:
             logs.append(f"Start equals Destination. No movement required.")
             return {'path': [start], 'cost': 0.0}, logs

        # Build adjacency graph
        graph = {node: [] for node in self.nodes}
        for u, v in self.connections:
            graph[u].append(v)
            graph[v].append(u)

        # Priority Queue: (current_total_cost, current_node)
        queue = [(0.0, start)]
        
        # Track distances and path reconstruction
        min_dist = {node: float('inf') for node in self.nodes}
        min_dist[start] = 0.0
        predecessors = {node: None for node in self.nodes}
        visited = set()

        while queue:
            current_cost, current_node = heapq.heappop(queue)

            # Optimization: If we reached the destination with shortest path, we can stop
            # specific to Dijkstra (heuristic algorithms like A* would differ)
            if current_node == dest:
                break
            
            # If current path is worse than already found shortest path, skip
            if current_cost > min_dist[current_node]:
                continue
            
            if current_node in visited:
                continue
            visited.add(current_node)

            for neighbor in graph.get(current_node, []):
                if neighbor in visited:
                    continue

                # Calculate dynamic edge cost using the model
                edge_cost = self._predict_cost(current_node, neighbor, model_type)
                
                if edge_cost == float('inf'):
                    # Road Blocked or Invalid
                    continue
                
                new_cost = current_cost + edge_cost
                
                if new_cost < min_dist[neighbor]:
                    min_dist[neighbor] = new_cost
                    predecessors[neighbor] = current_node
                    heapq.heappush(queue, (new_cost, neighbor))
                    logs.append(f"Path update: {current_node}->{neighbor} | New cost to {neighbor}: {new_cost:.2f}")

        # Reconstruct Path
        if min_dist[dest] == float('inf'):
            logs.append("No feasible solution found (Destination unreachable).")
            return None, logs

        path = []
        curr = dest
        while curr is not None:
            path.append(curr)
            curr = predecessors[curr]
        path.reverse()

        # Sanity check
        if path[0] != start:
             logs.append("Critical Error: Path reconstruction failed.")
             return None, logs

        final_cost = round(min_dist[dest], 2)
        logs.append(f"Optimal Decision: Path {path} with Total Cost {final_cost}")
        
        return {'path': path, 'cost': final_cost}, logs

    def get_network_state(self) -> Dict[str, Any]:
        """Exposes the current environment state."""
        return self.edge_data
