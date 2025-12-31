"""
PreSaNa: Goal-Based Dispatching Agent Interface
Serves as the REST API and Web Interface for the system.
Delegates all business logic to the core package.
"""
from flask import Flask, render_template, jsonify, request
from core.agent import GoalBasedAgent
from core.loader import loader

app = Flask(__name__)

# Initialize Agent
# The agent manages its own state and dependencies via core/config.py
agent = GoalBasedAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/network')
def get_network():
    """Returns current network state and model metadata."""
    return jsonify({
        'connections': agent.get_network_state(),
        'metadata': loader.get_metadata()
    })

@app.route('/api/randomize')
def randomize():
    """Triggers network randomization."""
    agent.randomize_network()
    return jsonify({'status': 'success'})

@app.route('/api/run', methods=['POST'])
def run_agent():
    """Executes the agent's search strategy."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    start = data.get('start')
    dest = data.get('dest')
    model_type = data.get('model_type', 'linear')
    
    if not start or not dest or start == dest:
        return jsonify({'error': 'Invalid nodes'}), 400
        
    best_route, logs = agent.find_best_route(start, dest, model_type)
    
    response = {
        'best': best_route,
        'logs': logs
    }
    
    if not best_route:
        response['error'] = 'No feasible path found.'
        
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
