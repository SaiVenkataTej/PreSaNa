"""
Core Configuration Module
Centralizes all application settings to improve Maintainability and Changeability.
"""
import os
from dataclasses import dataclass

@dataclass
class Config:
    """
    Application configuration settings.
    Uses dataclass for immutability and type safety.
    """
    # Base Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ARTIFACTS_DIR: str = os.path.join(BASE_DIR, 'model_artifacts')
    
    # Model Paths
    METADATA_PATH: str = os.path.join(ARTIFACTS_DIR, 'model_metadata.json')
    LINEAR_MODEL_PATH: str = os.path.join(ARTIFACTS_DIR, 'linear_model.pkl')
    RF_MODEL_PATH: str = os.path.join(ARTIFACTS_DIR, 'rf_model.pkl')
    
    # Network Settings
    NODES = ['A', 'B', 'C', 'D', 'E']
    CONNECTIONS = [
        ('A', 'B'), ('A', 'C'), ('A', 'D'),
        ('B', 'C'), ('B', 'D'), ('B', 'E'),
        ('C', 'E'), ('D', 'E'), ('C', 'D')
    ]
    
    # Defaults
    DEFAULT_WEIGHTS = {
        'w_distance': 0.3,
        'w_traffic': 0.5,
        'w_quality_inv': 0.2,
        'intercept': 0.0
    }

# Singleton instance
settings = Config()
