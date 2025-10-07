from AutoImblearn.components.api import BaseTransformerAPI
from imblearn.over_sampling import SMOTE, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
import smote_variants as sv
import numpy as np
import pandas as pd
import logging

# Suppress smote_variants logging
logging.getLogger(sv.__name__).setLevel(logging.CRITICAL)


# Define resamplers - mwmote and other smote_variants methods
rsps = {
    'rus': RandomUnderSampler(random_state=42),
    'ros': RandomOverSampler(random_state=42),
    'smote': SMOTE(random_state=42),
    'mwmote': sv.MWMOTE(proportion=1, random_state=42),
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

        # Perform resampling - smote_variants uses .sample() instead of .fit_resample()
        if hasattr(self.resampler, 'fit_resample'):
            X_resampled, y_resampled = self.resampler.fit_resample(X, y)
        elif hasattr(self.resampler, 'sample'):
            X_resampled, y_resampled = self.resampler.sample(X.to_numpy(), y.to_numpy())
        else:
            raise ValueError(f"Resampler {model_name} has no fit_resample or sample method")

        # Convert back to DataFrame/Series
        if not isinstance(X_resampled, pd.DataFrame):
            X_resampled = pd.DataFrame(X_resampled, columns=X.columns)

        if not isinstance(y_resampled, pd.Series):
            y_resampled = pd.Series(y_resampled, name=y.name if hasattr(y, 'name') else 'target')

        self.result_X = X_resampled
        self.result_y = y_resampled

        logging.info(f"Resampling complete: {X.shape} -> {X_resampled.shape}")
        return

    def transform(self, *args, **kwargs):
        """Return the resampled X (for compatibility)"""
        return self.result_X


RunImblearnSamplerAPI().run()
