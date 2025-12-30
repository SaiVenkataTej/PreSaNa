"""
PreSaNa: Goal-Based Dispatching Agent Backend
Main server script handling the routing logic and web API.
"""
from flask import Flask, render_template, jsonify, request
import json
import random
import os
import joblib
import pandas as pd

app = Flask(__name__)

# Constants
MODEL_METADATA_PATH = 'model_artifacts/model_metadata.json'
LINEAR_MODEL_PATH = 'model_artifacts/linear_model.pkl'
RF_MODEL_PATH = 'model_artifacts/rf_model.pkl'

# Global storage for models and metadata
models = {}
feature_metadata = {}

def load_resources():
    """Loads trained models and metadata on startup."""
    global models, feature_metadata
    
    # Load Metadata
    if os.path.exists(MODEL_METADATA_PATH):
        with open(MODEL_METADATA_PATH, 'r') as f:
            feature_metadata = json.load(f)
    else:
        print("WARNING: model_metadata.json not found. Models may not work correctly.")

    # Load Models
    try:
        models['linear'] = joblib.load(LINEAR_MODEL_PATH)
        print("Loaded Linear Regression model.")
    except Exception as e:
        print(f"Failed to load Linear model: {e}")

    try:
        models['rf'] = joblib.load(RF_MODEL_PATH)
        print("Loaded Random Forest model.")
    except Exception as e:
        print(f"Failed to load Random Forest model: {e}")

# Load resources immediately
load_resources()

class GoalBasedAgent:
    """
    PreSaNa Agent responsible for network management and path optimization.
    Uses trained models to evaluate route utils.
    """
    def __init__(self):
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

    def calculate_cost(self, start, end, model_type='linear'):
        """
        Calculates the cost between two nodes using the selected model.
        """
        key = f"{start}-{end}"
        if key not in self.edge_data:
            return 999999
        
        data = self.edge_data[key]
        if data['blocked'] == "Yes":
            return 999999
        
        # Prepare features: distance, traffic, quality_inv
        # Input format must matchtraining data: [[distance, traffic, 11-quality]]
        features = pd.DataFrame([{
            'distance': data['distance'],
            'traffic': data['traffic'],
            'quality_inv': 11 - data['quality']
        }])
        
        try:
            model = models.get(model_type)
            if not model:
                return 999999  # Fail safe if model missing
            
            cost = model.predict(features)[0]
            return round(float(cost), 2)
        except Exception as e:
            print(f"Prediction Error: {e}")
            return 999999

    def find_best_route(self, start, dest, model_type):
        """
        Search engine for the PreSaNa agent. 
        Evaluates direct and 1-stop paths to find the global minimum cost.
        """
        logs = []
        possible_paths = []
        
        logs.append(f"PreSaNa Goal: Minimize cost from {start} to {dest} using {model_type} model.")
        
        # Check direct
        direct_cost = self.calculate_cost(start, dest, model_type)
        if direct_cost < 999999:
            possible_paths.append({'path': [start, dest], 'cost': direct_cost})
            logs.append(f"Checking direct route: {start} -> {dest} | Cost: {direct_cost}")
        else:
            logs.append(f"Direct route {start} -> {dest} is BLOCKED or unavailable.")

        # Check 1-stop
        for mid in self.nodes:
            if mid == start or mid == dest:
                continue
            
            c1 = self.calculate_cost(start, mid, model_type)
            c2 = self.calculate_cost(mid, dest, model_type)
            
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
        'metadata': feature_metadata
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
    model_type = data.get('model_type', 'linear')  # Default to linear
    
    if not start or not dest or start == dest:
        return jsonify({'error': 'Invalid nodes'}), 400
        
    best, logs = agent.find_best_route(start, dest, model_type)
    return jsonify({
        'best': best,
        'logs': logs
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
