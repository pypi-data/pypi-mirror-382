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
        """
        Transform the input data X using the fitted transformer.

        Since fit() already transforms both train and test data in one go,
        this method simply loads the pre-computed test result from the file.
        No need to call the Docker container again!
        """
        from ..exceptions import DockerContainerError

        try:
            # Load the transformed test data that was saved during fit()
            # The test result is saved with _test.p suffix
            test_result_path = self.impute_file_path.replace('.p', '_test.p')

            if not os.path.exists(test_result_path):
                raise DockerContainerError(
                    f"Test result file not found: {test_result_path}. "
                    f"Make sure fit() was called with both X_train and X_test.",
                    container_id=None,
                    image_name=self.image_name,
                    logs=None,
                    operation="transform"
                )

            with open(test_result_path, "rb") as f:
                result = pickle.load(f)

            return result

        except Exception as e:
            if isinstance(e, DockerContainerError):
                raise
            raise DockerContainerError(
                f"Transform failed: {str(e)}",
                container_id=None,
                image_name=self.image_name,
                logs=None,
                operation="transform"
            ) from e

    def fit_transform(self, X, y=None, dockerfile_dir="."):
        """
        Fit the transformer and return the transformed training data.

        This calls fit() and then loads the training result (not test result).
        """
        self.fit(X, y, dockerfile_dir)

        # Load the transformed training data (main result, not _test.p)
        with open(self.impute_file_path, "rb") as f:
            result = pickle.load(f)

        return result

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
