# Agent Documentation: PreSaNa Dispatching Agent

## 1. Agent Type: Goal-Based Agent
A **Goal-Based Agent** is an AI agent that makes decisions based on achieving a specific goal. Unlike a simple reflex agent that only reacts to its current percepts, a goal-based agent considers the consequences of its actions and how they lead toward a desired state. In this application, the goal is to reach the "Destination Node" from the "Start Node" with the **minimum cumulative cost**.

## 2. Functions
The agent relies on several key functions to perform its task:
- **ML Training Function (Preprocessing)**: Trains a Linear Regression model on historical data to derive optimal cost weights.
- **Perception Function**: Scans the web environment (mesh network) to gather real-time data on distance, traffic, quality, and status.
- **Cost Calculation Function (Learned Utility)**: Uses the learned weights to calculate cost:
  $$Cost = w_1 \times Distance + w_2 \times Traffic + w_3 \times (11 - Quality) + Intercept$$
  - **Infinite Penalty**: If a road is `Blocked`, the cost is set to `999,999`.
- **Decision Logic (Search)**: Iterates through all possible connections:
    1. **Direct Routes**: Direct connections between Start and End.
    2. **1-Stop Routes**: Routes that go through one intermediate node (Start -> Mid -> End).
- **Execution Function**: Selects the route with the minimum total cost and reports the path to the user.
- **Reporting & Closure**: Upon reaching the goal or ending the session, the agent presents a final report and a personalized "Thank You" screen for the user.

## 3. Environment
The environment is the **Mesh Network** consisting of 5 nodes (A, B, C, D, E).
- **State Space**: The current location of the agent and the status of all edges (connections) in the network.
- **Action Space**: Moving from one node to another through an existing connection.

## 4. Environment Flavors (Properties)
- **Discrete**: The number of nodes and connections is finite.
- **Static vs Dynamic**: The environment data is static per execution but can be randomized dynamically via the UI (**PreSaNa Controls**).
- **Fully Observable**: The agent has full visibility of the network dashboard.
- **Web-Based Interface**: Implemented with Flask, HTML, CSS, and JS for premium interactivity.
- **Deterministic**: The result of moving between nodes is certain; if the agent chooses node B from A, it arrives at B.
- **Sequential**: Each step (or path selection) depends on the previous state.
- **Single-Agent**: There is only one agent navigating the network at a time.