"""
PreSaNa: Goal-Based Dispatching Agent Backend
Main server script handling the routing logic and web API.
"""
from flask import Flask, render_template, jsonify, request
import json
import random
import os

app = Flask(__name__)

# Load trained weights
WEIGHTS_PATH = 'model_weights.json'
DEFAULT_WEIGHTS = {'w_distance': 0.3, 'w_traffic': 0.5, 'w_quality_inv': 0.2, 'intercept': 0.0}

def load_weights():
    """Reads learned Linear Regression weights from a JSON file."""
    if os.path.exists(WEIGHTS_PATH):
        with open(WEIGHTS_PATH, 'r') as f:
            return json.load(f)
    return DEFAULT_WEIGHTS

class GoalBasedAgent:
    """
    PreSaNa Agent responsible for network management and path optimization.
    Uses learned weights to evaluate route utilities.
    """
    def __init__(self):
        self.weights = load_weights()
        self.nodes = ['A', 'B', 'C', 'D', 'E']
        self.connections = [
            ('A', 'B'), ('A', 'C'), ('A', 'D'),
            ('B', 'C'), ('B', 'D'), ('B', 'E'),
            ('C', 'E'), ('D', 'E'), ('C', 'D')
        ]
        self.edge_data = {}
        self.randomize_network()

    def randomize_network(self):
        """Generates random edge properties for the mesh network."""
        data = {}
        for conn in self.connections:
            # Generate metrics representing distance, traffic, and road quality
            edge_info = {
                'distance': random.randint(10, 100),
                'traffic': random.randint(0, 100),
                'quality': random.randint(1, 10),
                'blocked': "Yes" if random.random() < 0.1 else "No"
            }
            data[f"{conn[0]}-{conn[1]}"] = edge_info
            data[f"{conn[1]}-{conn[0]}"] = edge_info  # Bidirectional network
        self.edge_data = data

    def calculate_cost(self, start, end):
        """
        Calculates the utility-based cost between two nodes using the learned formula:
        Cost = w1*dist + w2*traffic + w3*(11-qual) + intercept
        """
        key = f"{start}-{end}"
        if key not in self.edge_data:
            return 999999
        
        data = self.edge_data[key]
        if data['blocked'] == "Yes":
            return 999999
        
        # learned formula: w1*dist + w2*traffic + w3*(11-qual) + intercept
        cost = (data['distance'] * self.weights['w_distance']) + \
               (data['traffic'] * self.weights['w_traffic']) + \
               ((11 - data['quality']) * self.weights['w_quality_inv']) + \
               self.weights['intercept']
        return round(cost, 2)

    def find_best_route(self, start, dest):
        """
        Search engine for the PreSaNa agent. 
        Evaluates direct and 1-stop paths to find the global minimum cost.
        """
        logs = []
        possible_paths = []
        
        logs.append(f"PreSaNa Goal: Minimize cost from {start} to {dest} using learned weights.")
        
        # Check direct
        direct_cost = self.calculate_cost(start, dest)
        if direct_cost < 999999:
            possible_paths.append({'path': [start, dest], 'cost': direct_cost})
            logs.append(f"Checking direct route: {start} -> {dest} | Cost: {direct_cost}")
        else:
            logs.append(f"Direct route {start} -> {dest} is BLOCKED or unavailable.")

        # Check 1-stop
        for mid in self.nodes:
            if mid == start or mid == dest:
                continue
            
            c1 = self.calculate_cost(start, mid)
            c2 = self.calculate_cost(mid, dest)
            
            if c1 < 999999 and c2 < 999999:
                total = round(c1 + c2, 2)
                possible_paths.append({'path': [start, mid, dest], 'cost': total})
                logs.append(f"Checking 1-stop route: {start} -> {mid} -> {dest} | Cost: {total} ({c1} + {c2})")
            else:
                logs.append(f"Route through {mid} is non-feasible (blocked segment).")

        if not possible_paths:
            return None, logs

        best = min(possible_paths, key=lambda x: x['cost'])
        return best, logs

agent = GoalBasedAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/network')
def get_network():
    return jsonify({
        'connections': agent.edge_data,
        'weights': agent.weights
    })

@app.route('/api/randomize')
def randomize():
    agent.randomize_network()
    return jsonify({'status': 'success'})

@app.route('/api/run', methods=['POST'])
def run_agent():
    data = request.json
    start = data.get('start')
    dest = data.get('dest')
    
    if not start or not dest or start == dest:
        return jsonify({'error': 'Invalid nodes'}), 400
        
    best, logs = agent.find_best_route(start, dest)
    return jsonify({
        'best': best,
        'logs': logs
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
