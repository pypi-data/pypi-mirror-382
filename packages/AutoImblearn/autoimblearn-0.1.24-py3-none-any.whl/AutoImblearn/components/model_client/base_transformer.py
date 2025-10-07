import requests
import pickle
import pandas as pd
import numpy as np
import os
from .base_model_client import BaseDockerModelClient


class BaseTransformer(BaseDockerModelClient):
    """ Abstract base class for sklearn-like transformers.
    transform    : Post the transform request through RESTful API
    fit_transform: Perform both fit and transform
    """

    def transform(self, X, y=None, dockerfile_dir="."):
        """Transform the input data X using the fitted transformer"""
        from ..exceptions import DockerContainerError

        try:
            self.ensure_container_running()

            # Convert X to DataFrame if needed
            if isinstance(X, np.ndarray):
                X_df = pd.DataFrame(X)
            elif isinstance(X, pd.DataFrame):
                X_df = X
            else:
                X_df = pd.DataFrame(X)

            # Save X to temp file in the docker volume
            temp_data_path = os.path.join(
                self.args.path, 'interim', self.args.dataset,
                f'X_transform_{self.container_name}.csv'
            )
            X_df.to_csv(temp_data_path, index=False)

            # Call the transform API endpoint
            headers = {"Content-Type": "application/json"}
            payload = {
                **self.payload,
                'transform_file': f'X_transform_{self.container_name}.csv'
            }

            response = requests.post(
                f"{self.api_url}/predict",
                json=payload,
                headers=headers
            )
            response.raise_for_status()

            # Load the transformed result from the impute file
            with open(self.impute_file_path, "rb") as f:
                result = pickle.load(f)

            # Clean up temp file
            if os.path.exists(temp_data_path):
                os.remove(temp_data_path)

            return result

        except Exception as e:
            logs = self.get_container_logs() if hasattr(self, 'container_id') and self.container_id else None
            raise DockerContainerError(
                f"Transform failed: {str(e)}",
                container_id=getattr(self, 'container_id', None),
                image_name=self.image_name,
                logs=logs,
                operation="transform"
            ) from e

        finally:
            self.stop_container()

    def fit_transform(self, X, y=None, dockerfile_dir="."):
        self.fit(X, y, dockerfile_dir)
        return self.transform(X, y, dockerfile_dir)

    def fit_resample(self, X, y):
        """
        Fit and resample the data (for resampler components).

        This method is for resamplers that transform both X and y.
        It combines fit and transform but returns both X and y.

        Args:
            X: Feature data
            y: Labels

        Returns:
            Tuple of (X_resampled, y_resampled)
        """
        from ..exceptions import DockerContainerError

        try:
            # Call fit with both X and y
            self.fit(self.args, X, y)

            # The resampler API should save both X and y resampled
            # Load them back from the saved files
            impute_file_path_X = self.impute_file_path
            impute_file_path_y = self.impute_file_path.replace('.p', '_y.p')

            with open(impute_file_path_X, "rb") as f:
                X_resampled = pickle.load(f)

            with open(impute_file_path_y, "rb") as f:
                y_resampled = pickle.load(f)

            return X_resampled, y_resampled

        except Exception as e:
            logs = self.get_container_logs() if hasattr(self, 'container_id') and self.container_id else None
            raise DockerContainerError(
                f"Fit resample failed: {str(e)}",
                container_id=getattr(self, 'container_id', None),
                image_name=self.image_name,
                logs=logs,
                operation="fit_resample"
            ) from e
