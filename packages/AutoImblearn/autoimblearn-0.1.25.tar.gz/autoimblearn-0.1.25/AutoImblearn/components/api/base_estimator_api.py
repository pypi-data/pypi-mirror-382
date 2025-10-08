from .base_model_api import BaseModelAPI
from abc import abstractmethod


class BaseEstimatorAPI(BaseModelAPI):
    """Abstract base class for sklearn-like estimators/classifiers."""

    def fit_train(self, args, X_train, y_train, X_test, y_test):
        self.fit(args, X_train, y_train, X_test, y_test)
        result = self.predict(X_test, y_test)
        return result

    @abstractmethod
    def fit(self, args, X_train, y_train, X_test=None, y_test=None):
        pass

    @abstractmethod
    def predict(self, X_test, y_test):
        pass
