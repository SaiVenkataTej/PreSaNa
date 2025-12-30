"""
PreSaNa
Handles synthetic data generation, model training (Linear & Random Forest), and artifact export.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import json
import joblib
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
    Trains Linear Regression and Random Forest models.
    Exports trained models (.pkl) and metadata (.json).
    """
    print("PreSaNa: Generating synthetic training data...")
    df = generate_training_data()
    
    # Preprocessing
    # We transform quality to 'inverse quality' for the linear relationship we want: (11-quality)
    X = df[['distance', 'traffic', 'quality']].copy()
    X['quality_inv'] = 11 - X['quality']
    
    # Feature set for models: distance, traffic, quality_inv
    X_train = X[['distance', 'traffic', 'quality_inv']]
    y_train = df['cost']
    
    # --- Linear Regression ---
    print("PreSaNa: Training Linear Regression model...")
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)
    
    # --- Random Forest ---
    print("PreSaNa: Training Random Forest model...")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # --- Export Models ---
    print("PreSaNa: Exporting models...")
    joblib.dump(linear_model, 'model_artifacts/linear_model.pkl')
    joblib.dump(rf_model, 'model_artifacts/rf_model.pkl')
    
    # --- Export Metadata ---
    metadata = {
        'linear': {
            'w_distance': float(linear_model.coef_[0]),
            'w_traffic': float(linear_model.coef_[1]),
            'w_quality_inv': float(linear_model.coef_[2]),
            'intercept': float(linear_model.intercept_)
        },
        'rf': {
            'feature_importances': {
                'distance': float(rf_model.feature_importances_[0]),
                'traffic': float(rf_model.feature_importances_[1]),
                'quality_inv': float(rf_model.feature_importances_[2])
            }
        }
    }
    
    with open('model_artifacts/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)
    
    print("Training complete. Models and metadata exported.")

if __name__ == "__main__":
    train_and_export()
