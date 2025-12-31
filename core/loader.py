"""
Core Loader Module
Handles secure loading of machine learning models and metadata.
Enhances Reliability and Security by abstracting persistence logic.
"""
import json
import joblib
import os
import logging
from typing import Dict, Any, Optional
from .config import settings

# Configure structured logging
logger = logging.getLogger(__name__)

class ModelLoader:
    """
    Service class responsible for loading and caching ML artifacts.
    Implements Singleton-like pattern via global instance.
    """
    def __init__(self):
        self._models: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}
        self._loaded = False

    def load_resources(self) -> None:
        """
        Loads all required resources from disk.
        Handles errors gracefully to ensure Stability.
        """
        if self._loaded:
            logger.info("Resources already loaded.")
            return

        # Load Metadata
        try:
            if os.path.exists(settings.METADATA_PATH):
                with open(settings.METADATA_PATH, 'r') as f:
                    self._metadata = json.load(f)
                logger.info(f"Metadata loaded from {settings.METADATA_PATH}")
            else:
                logger.warning(f"Metadata file not found at {settings.METADATA_PATH}")
        except Exception as e:
            logger.error(f"Failed to load metadata: {str(e)}")

        # Load Linear Model
        try:
            self._models['linear'] = joblib.load(settings.LINEAR_MODEL_PATH)
            logger.info("Linear Regression model loaded successfully.")
        except FileNotFoundError:
            logger.error(f"Linear model not found at {settings.LINEAR_MODEL_PATH}")
        except Exception as e:
            logger.error(f"Error loading Linear model: {str(e)}")

        # Load Random Forest Model
        try:
            self._models['rf'] = joblib.load(settings.RF_MODEL_PATH)
            logger.info("Random Forest model loaded successfully.")
        except FileNotFoundError:
            logger.error(f"Random Forest model not found at {settings.RF_MODEL_PATH}")
        except Exception as e:
            logger.error(f"Error loading Random Forest model: {str(e)}")

        self._loaded = True

    def get_model(self, model_type: str) -> Optional[Any]:
        """Retrieves a specific model by type."""
        return self._models.get(model_type)

    def get_metadata(self) -> Dict[str, Any]:
        """Retrieves loaded metadata."""
        return self._metadata

# Global loader instance
loader = ModelLoader()
