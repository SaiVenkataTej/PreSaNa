"""
Machine Learning Training Module
Responsible for generating synthetic data and training regression models.
Refactored for Modularity and consistency with Core Config.
"""
import pandas as pd
import numpy as np
import json
import joblib
import logging
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_training_data(n_samples: int = 500) -> pd.DataFrame:
    """
    Generates synthetic training data based on the formula:
    Cost = (w_dist * distance) + (w_traffic * traffic/100) + (w_quality_inv * (11-quality)) + Noise
    """
    np.random.seed(42)
    
    # Feature Generation
    distance = np.random.randint(10, 100, n_samples)
    traffic = np.random.randint(0, 100, n_samples)
    quality = np.random.randint(1, 10, n_samples)
    
    # Target Calculation (Cost)
    # Using weights defined in centralised config
    w_d = settings.DEFAULT_WEIGHTS['w_distance']
    w_t = settings.DEFAULT_WEIGHTS['w_traffic']
    w_q = settings.DEFAULT_WEIGHTS['w_quality_inv']
    
    # Cost formula
    # Note: traffic is normalized /100 in the formula logic but coefficients handle scale
    # Let's align with the original logic: Traffic (0-100) * 0.5 can be high cost.
    
    cost = (w_d * distance) + \
           (w_t * traffic) + \
           (w_q * (11 - quality)) + \
           np.random.normal(0, 5, n_samples)  # Gaussian Noise
           
    df = pd.DataFrame({
        'distance': distance,
        'traffic': traffic,
        'quality_inv': 11 - quality,
        'cost': np.round(cost, 2)
    })
    
    return df

def train_and_export():
    """
    Main execution pipeline:
    1. Generate Data
    2. Train Models (Linear + Random Forest)
    3. Export Artifacts (Models + Metadata) to configured paths
    """
    logger.info("Generating synthetic data...")
    df = generate_training_data()
    
    X_train = df[['distance', 'traffic', 'quality_inv']]
    y_train = df['cost']
    
    # --- Linear Regression ---
    logger.info("Training Linear Regression model...")
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)
    
    # --- Random Forest ---
    logger.info("Training Random Forest model...")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # --- Export Models ---
    logger.info(f"Exporting models to {settings.ARTIFACTS_DIR}...")
    try:
        joblib.dump(linear_model, settings.LINEAR_MODEL_PATH)
        joblib.dump(rf_model, settings.RF_MODEL_PATH)
    except Exception as e:
        logger.error(f"Failed to save models: {e}")
        return

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
    
    try:
        with open(settings.METADATA_PATH, 'w') as f:
            json.dump(metadata, f, indent=4)
        logger.info("Metadata exported successfully.")
    except Exception as e:
        logger.error(f"Failed to save metadata: {e}")

if __name__ == "__main__":
    train_and_export()
