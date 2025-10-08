import logging
import numpy as np
import pandas as pd

from hyperimpute.plugins.imputers import Imputers
from AutoImblearn.components.api import BaseTransformerAPI

# imps = {
#     "gain": lambda **kw: RunHyperImpute(model="gain", **kw),
#     "MIRACLE": lambda **kw: RunHyperImpute(model="MIRACLE", **kw),
#     "MIWAE": lambda **kw: RunHyperImpute(model="MIWAE", **kw),
# }
# imps = {
#     "MIWAE": Imputers().get(self.method.lower(), random_state=42, batch_size = 128),
# }

class RunHyperImputerAPI(BaseTransformerAPI):
    def __init__(self):
        super().__init__(__name__)

        self.result = None
        self.imputer = None  # Store the fitted imputer
        self.columns = None  # Store column names
        self.dict_types = None  # Store column dtypes
        self.param_space = {
            "miwae": {
                "random_state": {
                    "type": "int", "min": 0, "max": 10000, "default": 42
                },
                "batch_size": {
                    "type": "int", "min": 32, "max": 512, "default": 128
                },
                "epochs": {
                    "type": "int", "min": 10, "max": 500, "default": 50
                },
                "latent_dim": {
                    "type": "int", "min": 4, "max": 64, "default": 16
                },
                "lr": {
                    "type": "float", "min": 1e-5, "max": 1e-2, "default": 1e-3, "log_scale": True
                },
            },
            "miracle": {
                "n_components": {
                    "type": "int", "min": 2, "max": 100, "default": 10
                },
                "tol": {
                    "type": "float", "min": 1e-6, "max": 1e-2, "default": 1e-3, "log_scale": True
                },
                "max_iter": {
                    "type": "int", "min": 50, "max": 1000, "default": 200
                },
            },
            "gain": {
                "random_state": {
                    "type": "int", "min": 0, "max": 10000, "default": 0
                },
                "batch_size": {
                    "type": "int", "min": 32, "max": 512, "default": 128
                },
                "epochs": {
                    "type": "int", "min": 10, "max": 500, "default": 100
                },
                "hint_rate": {
                    "type": "float", "min": 0.1, "max": 1.0, "default": 0.9
                },
                "alpha": {
                    "type": "int", "min": 1, "max": 200, "default": 10
                },
            },
        }

    def get_hyperparameter_search_space(self):
        return self.param_space

    def _validate_kwargs(self, name: str, kwargs: dict):
        allowed = set(self.param_space[name].keys())
        unknown = set(kwargs) - allowed
        if unknown:
            raise ValueError(
                f"Unsupported parameters for '{name}': {sorted(unknown)}. "
                f"Allowed: {sorted(allowed)}"
            )


    def fit(self, params, *args, **kwargs):
        # Get parameters
        model_name = params.model
        imputer_kwargs = params.imputer_kwargs
        categorical_columns = params.categorical_columns
        if 'data' in kwargs:
            data = kwargs.get('data')
        else:
            raise ValueError("There is no data passed in")

        # old_columns = data.column
        self.dict_types = dict(data.dtypes)
        self.columns = data.columns

        # Train
        model_name = model_name.lower()
        self.imputer = Imputers().get(model_name, **imputer_kwargs)
        imp_out = self.imputer.fit_transform(data)

        # Change back to DataFrame with previous column names
        if not isinstance(imp_out, pd.DataFrame):
            imp_out = pd.DataFrame(imp_out, columns=data.columns)
        else:
            imp_out.columns = data.columns

        # Change back to old column dtypes
        imp_out = imp_out.astype(self.dict_types)

        logging.info("finished training")
        self.result = imp_out
        return

    def transform(self, *args, **kwargs):
        # If data is provided, transform it; otherwise return cached result
        if 'data' in kwargs:
            data = kwargs.get('data')
            if self.imputer is None:
                raise ValueError("Imputer not fitted. Call fit() first.")

            imp_out = self.imputer.transform(data)

            # Change back to DataFrame with previous column names
            if not isinstance(imp_out, pd.DataFrame):
                imp_out = pd.DataFrame(imp_out, columns=self.columns)
            else:
                imp_out.columns = self.columns

            # Change back to old column dtypes
            imp_out = imp_out.astype(self.dict_types)

            return imp_out
        else:
            # Fallback to cached result for backward compatibility
            return self.result

RunHyperImputerAPI().run()