# AutoImblearn/pipelines/customimputation.py
import os
from pathlib import Path
import json
import pickle
from typing import Dict, Callable, Any, Iterable, Optional

from sklearn.base import BaseEstimator, TransformerMixin
# from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler

import pandas as pd
import numpy as np
from scipy.stats import norm, gaussian_kde
from AutoImblearn.processing.utils import find_categorical_columns
from AutoImblearn.components.imputers import stat_imputer_factory
# from AutoImblearn.processing.persist import with_saving

try:
    from AutoImblearn.components.imputers import RunHyperImpute, RunSklearnImpute
    from AutoImblearn.components.model_client.base_transformer import BaseTransformer
except Exception:
    RunSklearnImpute = None
    RunHyperImpute = None
    BaseTransformer = None


imps: Dict[str, Callable[..., Any]] = {
    # no Docker
    "mean": stat_imputer_factory("mean"),
    "median": stat_imputer_factory("median"),
}

# sklearn or other heavy ones, containerized
if RunSklearnImpute is not None:
    imps.update({
        "knn": lambda **kw: RunSklearnImpute(model="knn", **kw), # KNN based imputer
        "ii":  lambda **kw: RunSklearnImpute(model="ii", **kw),  # IterativeImputer
    })
if RunHyperImpute is not None:
    imps.update({
        "gain":     lambda **kw: RunHyperImpute(model="gain", **kw),
        "MIRACLE":  lambda **kw: RunHyperImpute(model="MIRACLE", **kw),
        "MIWAE":    lambda **kw: RunHyperImpute(model="MIWAE", **kw),
    })

class CustomImputer(BaseEstimator, TransformerMixin):
    """ Unified imputer wrapper built on registry `imps`.

    method:            key in `registry` (e.g., 'median', 'knn', ...).
    categorical_cols:  optional list of columns to round to integers after imputation.
                       If not provided, the class can load them from disk (data_folder/dataset_name),
                       or infer via a simple heuristic on fit().
    data_folder:       base folder where metadata is stored/loaded (JSON).
    dataset_name:      dataset identifier for metadata filenames.
    categorical_columns:
                       if True, saves discovered categorical columns to disk after fit().
    registry:          mapping from method name -> factory that returns an estimator.
    **imputer_kwargs:  forwarded to the underlying estimator factory.
    """

    def __init__(self,
                 method: str ="median",
                 categorical_cols: Optional[Iterable[str]] = None,
                 registry:         Optional[Dict[str, Callable[..., Any]]] = None,
                 data_folder:      Optional[str] = None,
                 dataset_name:     Optional[str] = None,
                 impute_file_path: Optional[str] = None,
                 **imputer_kwargs: Any):

        self.method           = method
        self.registry         = imps if registry is None else registry
        self.data_folder      = data_folder
        self.dataset_name     = dataset_name
        self.categorical_cols = None if categorical_cols is None else self.find_categorical(self.data_folder, dataset_name)
        self.impute_file_path = impute_file_path
        self.imputer_kwargs   = dict(imputer_kwargs)

        self._impl            = self._build_impl()

        self.feature2drop     = []
        self.y = None

    def fit(self, args, X, y=None):
        X_arr = self._ensure_array(X)
        self._impl.fit(args, X_arr, y)
        self.y = y
        return self

    def transform(self, X):
        X_imp = self._impl.transform(X)
        if not isinstance(X_imp, pd.DataFrame):
            raise ValueError("The transform() method only works with pandas DataFrames.")
        self._round_categoricals_inplace(X_imp)

        # save imputed result if self._impl is not a docker model
        if not isinstance(self._impl, BaseTransformer):
            self._save_imputed(X_imp, self.y)

        return X_imp

    def fit_transform(self, args, X, y=None):
        self.fit(args, X, y)
        return self.transform(X)

    def get_params(self, deep: bool = True):
        params = {
            "method": self.method,
            "categorical_cols": self.categorical_cols,
            "data_folder": self.data_folder,
            "dataset_name": self.dataset_name,
            "categorical_columns": self.categorical_columns,
            "registry": self.registry,
            **{f"impl__{k}": v for k, v in self.imputer_kwargs.items()},
        }
        if deep and hasattr(self._impl, "get_params"):
            for k, v in self._impl.get_params(deep=True).items():
                params.setdefault(f"impl__{k}", v)
        return params

    def set_params(self, **params):
        if "method" in params:
            self.method = params.pop("method")
        if "categorical_cols" in params:
            val = params.pop("categorical_cols")
            self.categorical_cols = None if val is None else list(val)
        if "data_folder" in params:
            self.data_folder = params.pop("data_folder")
        if "dataset_name" in params:
            self.dataset_name = params.pop("dataset_name")
        if "categorical_columns" in params:
            self.categorical_columns = params.pop("categorical_columns")
        if "registry" in params:
            self.registry = params.pop("registry")

        impl_updates = {k[len("impl__"):]: v for k, v in list(params.items()) if k.startswith("impl__")}
        for k in list(params.keys()):
            if k.startswith("impl__"):
                params.pop(k)

        self.imputer_kwargs.update(params)
        self._impl = self._build_impl()

        if impl_updates and hasattr(self._impl, "set_params"):
            self._impl.set_params(**impl_updates)
        return self

    def _build_impl(self):
        """
        Instantiate the underlying imputer from the registry.

        Looks up `self.method` in the registry, instantiates the factory,
        and attaches optional metadata (e.g. data_folder) if supported.
        """
        if self.method not in self.registry:
            raise KeyError(
                f"Unknown imputation method '{self.method}'. "
                f"Known methods: {sorted(self.registry.keys())}"
            )

        # registry values are factories (lambda **kw)
        self.imputer_kwargs["data_folder"] = self.data_folder
        self.imputer_kwargs["impute_file_path"] = self.impute_file_path
        factory = self.registry[self.method]
        impl = factory(**self.imputer_kwargs)

        # Optionally set data_folder if provided and supported
        if self.data_folder is not None:
            if hasattr(impl, "set_params") and hasattr(impl, "data_folder"):
                # setattr(impl, "data_folder", self.data_folder)
                impl.set_params(data_folder=self.data_folder)

        return impl

    def _save_imputed(self, X_imp, y):
        """Persist imputed result to data_folder"""
        if isinstance(X_imp, pd.DataFrame):
            data2save = (X_imp, y)
            if not os.path.isdir(os.path.dirname(self.impute_file_path)):
                os.makedirs(os.path.dirname(self.impute_file_path))
            with open(self.impute_file_path, "wb") as f:
                pickle.dump(data2save, f)

        else:
            raise ValueError("The input data is not a DataFrame.")

    @staticmethod
    def _ensure_array(X):
        if isinstance(X, pd.DataFrame):
            return X.values
        if isinstance(X, np.ndarray):
            return X
        return np.asarray(X)


    def _round_categoricals_inplace(self, df: pd.DataFrame):
        if not self.categorical_cols:
            return
        for c in self.categorical_cols:
            if c in df.columns and pd.api.types.is_numeric_dtype(df[c]):
                df[c] = df[c].round(0)

    def find_categorical(self, data_folder_path, dataset_name):
        """find all the categorical columns"""
        # TODO change the location and the name to constant, and place in to utils.py
        subfolder = os.path.join(data_folder_path, f'interim/{dataset_name}')
        Path(subfolder).mkdir(parents=True, exist_ok=True)
        json_file_path = os.path.join(subfolder, 'category.json')
        if os.path.exists(json_file_path):
            self.categorical_columns = json.load(open(json_file_path, 'r'))
        else:
            self.category_columns = find_categorical_columns(self.data).keys()

    def transform_categorical(self, columns=None):
        """use one-hot encoding to transform categorical columns"""
        if columns is not None:
            self.category_columns = columns

        # Transform the categorical
        self.category_columns = [i for i in self.category_columns if i in self.data.columns.values]

        self.data = pd.get_dummies(data=self.data, columns=self.category_columns)
