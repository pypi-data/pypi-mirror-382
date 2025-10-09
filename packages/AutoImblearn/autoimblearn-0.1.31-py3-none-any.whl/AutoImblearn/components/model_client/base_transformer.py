import requests
import pickle
import pandas as pd
import numpy as np
import os
from .base_model_client import BaseDockerModelClient


class BaseTransformer(BaseDockerModelClient):
    """ Abstract base class for sklearn-like transformers.

    This class provides a sklearn-compatible interface for Docker-based transformers.

    Workflow:
    1. fit(args, X_train, y=None): Fit the transformer on training data (container stays running)
    2. transform(X): Transform new data using the fitted transformer (calls Docker API, container stays running)
    3. Container cleanup happens when object is deleted or cleanup() is called explicitly

    Note: Container stays alive across multiple transform() calls to avoid rebuild overhead.
    """

    def __init__(self, *args, **kwargs):
        # Set is_transformer=True so container stays running after fit()
        super().__init__(*args, **kwargs, is_transformer=True)

    def transform(self, X, y=None):
        """
        Transform the input data X using the fitted transformer.

        This method:
        1. Saves X to a temporary CSV file
        2. Calls the Docker container's /transform endpoint
        3. Loads and returns the transformed result

        The container stays running to allow multiple transform() calls.

        Args:
            X: Data to transform (DataFrame or numpy array)
            y: Ignored (for sklearn compatibility)

        Returns:
            Transformed data as DataFrame
        """
        from ..exceptions import DockerContainerError

        try:
            # Ensure we have container running from fit()
            if not self.container_id:
                raise DockerContainerError(
                    "No container running. Call fit() before transform().",
                    container_id=None,
                    image_name=self.image_name,
                    logs=None,
                    operation="transform"
                )

            # Save the data to transform
            transform_csv_name = f"X_transform_{self.container_name}.csv"
            transform_csv_path = os.path.join(
                self.args.path, "interim", self.args.dataset, transform_csv_name
            )

            if isinstance(X, pd.DataFrame):
                X.to_csv(transform_csv_path, index=False, header=False)
            else:
                np.savetxt(transform_csv_path, X, delimiter=",")

            # Call the /transform endpoint
            headers = {"Content-Type": "application/json"}
            payload = {
                "transform_file": transform_csv_name,
                "impute_file_name": os.path.basename(self.impute_file_path).replace('.p', '_transform.p')
            }

            response = requests.post(f"{self.api_url}/transform", json=payload, headers=headers)
            response.raise_for_status()

            # Load the transformed result
            result_path = self.impute_file_path.replace('.p', '_transform.p')
            with open(result_path, 'rb') as f:
                result = pickle.load(f)

            return result

        except requests.exceptions.RequestException as e:
            logs = self.get_container_logs() if self.container_id else None
            raise DockerContainerError(
                f"Transform API request failed: {str(e)}",
                container_id=self.container_id,
                image_name=self.image_name,
                logs=logs,
                operation="transform"
            ) from e

        except Exception as e:
            if isinstance(e, DockerContainerError):
                raise
            logs = self.get_container_logs() if self.container_id else None
            raise DockerContainerError(
                f"Transform failed: {str(e)}",
                container_id=self.container_id,
                image_name=self.image_name,
                logs=logs,
                operation="transform"
            ) from e

    def fit_transform(self, args, X, y=None):
        """
        Fit the transformer and return the transformed training data.

        This sklearn-compatible method:
        1. Calls fit(args, X, y) to train the transformer
        2. Calls transform(X) to get the transformed result

        Args:
            args: Arguments object with path, dataset, etc.
            X: Training data to fit and transform
            y: Labels (optional, for sklearn compatibility)

        Returns:
            Transformed training data
        """
        # Fit the transformer
        self.fit(args, X, y)

        # Transform the same data
        return self.transform(X)

    def cleanup(self):
        """
        Explicitly cleanup (stop and remove) the Docker container.

        Call this when you're done with all transformations.
        """
        try:
            if self.container_id:
                self.stop_container()
        except Exception as e:
            import logging
            logging.error(f"Failed to cleanup container: {e}")

    def __del__(self):
        """
        Cleanup container when object is garbage collected.
        """
        self.cleanup()

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
