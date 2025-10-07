import requests
import pandas as pd
from .base_model_client import BaseDockerModelClient


class BaseEstimator(BaseDockerModelClient):
    """Abstract base class for sklearn-like estimators/classifiers."""

    def payload(self):
        pass

    def predict(self, X):
        """Predict with data X"""
        try:
            self.ensure_container_running()
            payload = {
                # "data": self.(X).to_dict(orient="records")
            }
            response = requests.post(f"{self.api_url}/predict", json=payload)
            response.raise_for_status()
            result = response.json().get("balanced_data", [])
            return pd.DataFrame(result)
        finally:
            self.stop_container()
