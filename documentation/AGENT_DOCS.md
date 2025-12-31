# Agent Documentation: PreSaNa Dispatching Agent

## 1. Agent Type: Goal-Based Agent
A **Goal-Based Agent** is an AI agent that makes decisions based on achieving a specific goal. Unlike a simple reflex agent that only reacts to its current percepts, a goal-based agent considers the consequences of its actions and how they lead toward a desired state. In this application, the goal is to reach the "Destination Node" from the "Start Node" with the **minimum cumulative cost**.

## 2. System Architecture & Design
The system employs a robust, modular architecture designed for Scalability and Reliability.

### A. Core Package (`core/`)
The business logic is encapsulated in a dedicated package to ensure Separation of Concerns:
- **`core/agent.py`**: The "Brain". Handles perception, decision-making, and state management. Decoupled from the web framework.
- **`core/loader.py`**: Robust Resource Management. Handles the secure loading of ML models and metadata with error tolerance.
- **`core/config.py`**: Centralized Configuration. Single source of truth for all file paths, network settings, and constants.

### B. Interface Layer (`app.py`)
A thin Flask wrapper that acts solely as a REST API and Web Interface. It delegates all logic to the `core` package, ensuring high Cohesion.

### C. Machine Learning Core (`ml_model.py`)
A standalone training module that generates synthetic data and trains regression models. It uses the centralized configuration to ensure consistency with the backend.

## 3. Functions
The agent relies on several key functions to perform its task:
- **ML Training (Preprocessing)**: Trains Linear Regression and Random Forest models on historical data.
- **Perception Function**: Scans the web environment (mesh network) to gather real-time data on distance, traffic, quality, and status.
- **Cost Calculation (Learned Utility)**: Uses the learned weights to calculate cost:
  $$Cost = w_1 \times Distance + w_2 \times Traffic + w_3 \times (11 - Quality) + Intercept$$
  - **Infinite Penalty**: If a road is `Blocked`, the cost is set to `999,999`.
- **Decision Logic (Search)**: Iterates through all possible connections:
    1. **Direct Routes**: Direct connections between Start and End.
    2. **1-Stop Routes**: Routes that go through one intermediate node (Start -> Mid -> End).
- **Execution Function**: Selects the route with the minimum total cost and reports the path to the user.

## 4. Environment
The environment is the **Mesh Network** consisting of 5 nodes (A, B, C, D, E).
- **State Space**: The current location of the agent and the status of all edges (connections) in the network.
- **Action Space**: Moving from one node to another through an existing connection.

## 5. Environment Flavors (Properties)
- **Discrete**: The number of nodes and connections is finite.
- **Static vs Dynamic**: The environment data is static per execution but can be randomized dynamically via the UI.
- **Fully Observable**: The agent has full visibility of the network dashboard.
- **Web-Based Interface**: Implemented with Flask, HTML, CSS, and JS for premium interactivity.
- **Deterministic**: The result of moving between nodes is certain.
- **Sequential**: Each step (or path selection) depends on the previous state.
- **Single-Agent**: There is only one agent navigating the network at a time.

## 6. System Limitations
While effective as a prototype, the current system has specific constraints:
- **Fixed Network Topology**: The mesh is hardcoded to 5 nodes (A-E). Adding new nodes requires valid code changes to the configuration.
- **Limited Search Depth**: The pathfinding logic currently evaluates only **Direct** and **1-Hop** routes. It will not find complex paths involving 3 or more stops.
- **Synthetic Training Data**: The ML models are trained on simulated data. Real-world physics (like weather impact on road quality) are not modeled.
- **Static Edge Connections**: While weights (traffic/distance) are dynamic, the physical road connections are static.