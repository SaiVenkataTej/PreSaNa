"""
Core Agent Module
Implements the Goal-Based Agent logic.
Focuses on Modularity, Testability, and Code Readability.
"""
import random
import logging
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from .config import settings
from .loader import loader

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
                logger.error(f"Model type '{model_type}' not available.")
                return float('inf')
            
            cost = model.predict(features)[0]
            return round(float(cost), 2)
        except Exception as e:
            logger.error(f"Prediction failed for {start}->{end}: {str(e)}")
            return float('inf')

    def find_best_route(self, start: str, dest: str, model_type: str = 'linear') -> Tuple[Optional[Dict[str, Any]], List[str]]:
        """
        Executes the search strategy to find the optimal path.
        Currently implements a depth-limited search (Direct + 1-Hop).
        
        Returns:
            Tuple containing:
            - Best route object (dict) or None
            - List of execution logs (for XAI)
        """
        logs = []
        possible_paths = []
        
        logs.append(f"Goal: {start} -> {dest} | Strategy: Minimize Cost | Model: {model_type.upper()}")
        
        # 1. Evaluate Direct Path
        cost = self._predict_cost(start, dest, model_type)
        if cost < float('inf'):
            possible_paths.append({'path': [start, dest], 'cost': cost})
            logs.append(f"Evaluated Direct: {start}->{dest} | Cost: {cost}")
        else:
            logs.append(f"Evaluated Direct: {start}->{dest} | Status: BLOCKED/High Cost")

        # 2. Evaluate 1-Stop Paths (Intermediate Nodes)
        for mid in self.nodes:
            if mid in (start, dest):
                continue
            
            c1 = self._predict_cost(start, mid, model_type)
            c2 = self._predict_cost(mid, dest, model_type)
            
            if c1 < float('inf') and c2 < float('inf'):
                total_cost = round(c1 + c2, 2)
                possible_paths.append({'path': [start, mid, dest], 'cost': total_cost})
                logs.append(f"Evaluated Path: {start}->{mid}->{dest} | Cost: {total_cost}")
            else:
                # logs.append(f"Path through {mid} infeasible.") # Reduce noise
                pass

        # 3. Decision Making
        if not possible_paths:
            logs.append("No feasible solution found.")
            return None, logs

        best_route = min(possible_paths, key=lambda x: x['cost'])
        logs.append(f"Optimal Decision: {best_route['path']} with Cost {best_route['cost']}")
        
        return best_route, logs

    def get_network_state(self) -> Dict[str, Any]:
        """Exposes the current environment state."""
        return self.edge_data
