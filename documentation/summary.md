# PreSaNa: Project Summary & Analysis

## 1. Executive Summary
**PreSaNa** (Predictive Smart Navigation Agent) is a Goal-Based Artificial Intelligence agent designed to solve logistics and routing optimization problems within a mesh network. It integrates **Search Algorithms** with **Machine Learning** to make intelligent, data-driven decisions.

The core objective of the agent is to navigate from a *Start Node* to a *Destination Node* with the **minimum cumulative cost**. Unlike traditional routing engines that use static weights, PreSaNa uses ML models (Linear Regression and Random Forest) to learn the cost function dynamically from synthetic historical data, making it adaptable to changing environment metrics like traffic, distance, and road quality.

## 2. System Architecture

The project follows a modular Client-Server architecture:

- **Frontend (Client)**: A responsive web dashboard built with HTML5, CSS3, and Vanilla JavaScript. It serves as the environment visualization and control interface.
- **Backend (Server)**: A Flask (Python) application that acts as the agent's "Brain". It handles API requests, manages state, and executes the search logic.
- **Machine Learning Core**: A standalone module (`ml_model.py`) responsible for generating synthetic data, training regression models, and exporting them for the backend to use.

## 3. Technical Implementation Details

### A. Machine Learning Module (`ml_model.py`)
This module is the foundation of the agent's intelligence.
- **Synthetic Data Generation**: Simulates realistic road segments with attributes:
    - `Distance` (10-100 km)
    - `Traffic Congestion` (0-100%)
    - `Road Quality` (1-10)
    - `Cost`: derived from a weighted formula + Gaussian noise.
- **Model Training**:
    1.  **Linear Regression**: Learns a linear relationship ($w_1 \cdot d + w_2 \cdot t + \dots$). Provides interpretability via coefficients.
    2.  **Random Forest Regressor**: Captures non-linear complexities. Provides `Feature Importances` to understand which factors drive cost.
- **Artifact Export**: Trained models are serialized using `joblib` (`.pkl` files), and metadata is saved to JSON for frontend display.

### B. The Backend Agent (`app.py`)
The `GoalBasedAgent` class encapsulates the agent's logic:
- **Environment**: A mesh network of 5 nodes (A-E) with bidirectional edges.
- **Perception**: It "sees" the attributes of every connection (Distance, Traffic, blocked status).
- **Inference**: Uses the loaded ML models to predict the "cost" of traversing an edge. It dynamically switches between Linear and Random Forest models based on user selection.
- **Search Strategy**: Evaluates all valid paths (Direct and 1-Stop) to find the global minimum. It handles constraints like "Blocked" roads by assigning an infinite cost.

### C. The Frontend Interface
- **Visualization**: Displays the network as a table, showing real-time metrics for every connection.
- **Interactivity**: Users can:
    - Randomize network conditions to test the agent's adaptability.
    - Select the ML model (Linear vs. Random Forest).
    - define Start/End goals.
- **Feedback Loop**: The "Agent Thought Process" console logs every step of the decision-making process, providing transparency into the AI's logic.

## 4. Key Features Analysis

| Feature | Description | Technical Value |
| :--- | :--- | :--- |
| **Multi-Model Support** | Switch between Linear Regression and Random Forest. | Demonstrates trade-off between interpretability and complexity. |
| **Dynamic Environment** | "Randomize" button alters all edge weights. | Tests generalizability of the agent. |
| **Explainable AI (XAI)** | Console logs show exactly which paths were checked and why. | Builds user trust and aids debugging. |
| **Robust Error Handling** | Handles blocked roads and unreachable goals gracefully. | Ensures system stability. |

## 5. Future Enhancements / Roadmap

1.  **Graph Expansion**: Scale from 5 nodes to $N$ nodes using algorithms like Dijkstra or A* for pathfinding.
2.  **Real-Time Learning**: Implement Reinforcement Learning (RL) where the agent updates its weights based on "feedback" from completed trips.
3.  **Visual Graph Rendering**: Use a library like D3.js or Cytoscape.js to render the network as an interactive node-link diagram instead of a table.
4.  **API Integration**: Connect to real-world map APIs (Google Maps, OpenStreetMap) to fetch real traffic and distance data.

## 6. Conclusion
PreSaNa successfully demonstrates how AI agents can leverage Machine Learning to solve optimization problems. By decoupling the learning phase (training) from the execution phase (inference), the system achieves both high performance and modularity. It stands as a solid prototype for intelligent logistics dispatch systems.
