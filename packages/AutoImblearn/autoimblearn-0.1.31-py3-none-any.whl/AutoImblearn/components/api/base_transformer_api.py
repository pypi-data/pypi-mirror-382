from .base_model_api import BaseModelAPI
from abc import abstractmethod


class BaseTransformerAPI(BaseModelAPI):
    """Abstract base class for sklearn-like transformers."""
    def fit_train(self, params, *args, **kwargs):
        self.fit(params, *args, **kwargs)
        result = self.transform(*args, **kwargs)
        return result

    @abstractmethod
    def fit(self, params, *args, **kwargs):
        pass

    @abstractmethod
    def transform(self, *args, **kwargs):
        pass
