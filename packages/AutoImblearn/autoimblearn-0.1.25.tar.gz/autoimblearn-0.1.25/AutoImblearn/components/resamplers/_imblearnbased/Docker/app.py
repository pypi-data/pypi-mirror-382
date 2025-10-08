from AutoImblearn.components.api import BaseTransformerAPI
from imblearn.over_sampling import SMOTE, RandomOverSampler, ADASYN, BorderlineSMOTE
from imblearn.under_sampling import RandomUnderSampler, TomekLinks, EditedNearestNeighbours
from imblearn.combine import SMOTEENN, SMOTETomek
import numpy as np
import pandas as pd
import logging


rsps = {
    'rus': RandomUnderSampler(random_state=42),
    'ros': RandomOverSampler(random_state=42),
    'smote': SMOTE(random_state=42),
    'adasyn': ADASYN(random_state=42),
    'borderline_smote': BorderlineSMOTE(random_state=42),
    'tomek': TomekLinks(),
    'enn': EditedNearestNeighbours(),
    'smoteenn': SMOTEENN(random_state=42),
    'smotetomek': SMOTETomek(random_state=42),
}


class RunImblearnSamplerAPI(BaseTransformerAPI):
    def __init__(self):
        self.resampler = None  # Store the resampler instance
        self.result_X = None  # Store resampled X
        self.result_y = None  # Store resampled y
        super().__init__(__name__)

    def get_hyperparameter_search_space(self):
        return {
            "rus": {},
            "ros": {},
            "smote": {
                "k_neighbors": {
                    "type": "int", "min": 1, "max": 10, "default": 5
                },
            },
            "adasyn": {
                "n_neighbors": {
                    "type": "int", "min": 1, "max": 10, "default": 5
                },
            },
            "borderline_smote": {
                "k_neighbors": {
                    "type": "int", "min": 1, "max": 10, "default": 5
                },
            },
            "tomek": {},
            "enn": {},
            "smoteenn": {},
            "smotetomek": {},
        }

    def fit(self, params, *args, **kwargs):
        """Fit and resample the data"""
        model_name = params.model

        if 'data' in kwargs:
            # data is X with y as the last column (from save_data_2_volume)
            full_data = kwargs.get('data')
            # Separate X and y
            X = full_data.iloc[:, :-1]  # All columns except last
            y = full_data.iloc[:, -1]   # Last column is y
        else:
            raise ValueError("No data passed in")

        # Get the resampler
        if model_name in rsps:
            self.resampler = rsps[model_name]
        else:
            raise ValueError(f"Resampler {model_name} not defined")

        # Perform resampling
        X_resampled, y_resampled = self.resampler.fit_resample(X, y)

        # Convert back to DataFrame/Series
        if not isinstance(X_resampled, pd.DataFrame):
            X_resampled = pd.DataFrame(X_resampled, columns=X.columns)

        if not isinstance(y_resampled, pd.Series):
            y_resampled = pd.Series(y_resampled, name=y.name if hasattr(y, 'name') else 'target')

        self.result_X = X_resampled
        self.result_y = y_resampled

        # Store in self.result for BaseModelAPI compatibility
        self.result = self.result_X

        logging.info(f"Resampling complete: {X.shape} -> {X_resampled.shape}")
        return

    def transform(self, *args, **kwargs):
        """Return the resampled X (for compatibility)"""
        return self.result_X


RunImblearnSamplerAPI().run()
