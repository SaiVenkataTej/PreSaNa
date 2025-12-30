"""
PreSaNa
Handles synthetic data generation and Linear Regression model training.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import json
import os

def generate_training_data(n_samples=500):
    """
    Generates a synthetic dataset for the PreSaNa routing model.
    Models the relationship between road metrics and transport cost.
    """
    # Features: Distance (km), Traffic Congestion (%), and Surface Quality (1-10)
    distance = np.random.randint(10, 100, n_samples)
    traffic = np.random.randint(0, 100, n_samples)
    quality = np.random.randint(1, 11, n_samples)
    
    # Target Formula: w_dist*0.3 + w_traffic*0.5 + w_quality*(11-q)
    noise = np.random.normal(0, 1, n_samples)
    cost = (distance * 0.3) + (traffic * 0.5) + ((11 - quality) * 0.2) + noise
    
    df = pd.DataFrame({
        'distance': distance,
        'traffic': traffic,
        'quality': quality,
        'cost': cost
    })
    return df

def train_and_export():
    """
    Trains the Linear Regression model, extracts the learned weights,
    and exports them for use by the backend agent.
    """
    print("PreSaNa: Generating synthetic training data...")
    df = generate_training_data()
    
    X = df[['distance', 'traffic', 'quality']]
    # We transform quality to 'inverse quality' for the linear relationship we want: (11-quality)
    X_transformed = X.copy()
    X_transformed['quality_inv'] = 11 - X_transformed['quality']
    X_final = X_transformed[['distance', 'traffic', 'quality_inv']]
    
    y = df['cost']
    
    print("PreSaNa: Training Linear Regression model...")
    model = LinearRegression()
    model.fit(X_final, y)
    
    weights = {
        'w_distance': float(model.coef_[0]),
        'w_traffic': float(model.coef_[1]),
        'w_quality_inv': float(model.coef_[2]),
        'intercept': float(model.intercept_)
    }
    
    print(f"Learned Weights: {weights}")
    
    with open('model_weights.json', 'w') as f:
        json.dump(weights, f)
    
    print("Weights exported to model_weights.json")
    return weights

if __name__ == "__main__":
    train_and_export()