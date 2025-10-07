import logging

import numpy as np
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score

from xgboost import XGBClassifier

from AutoImblearn.components.api import BaseEstimatorAPI

clfs = {
    "ensemble": XGBClassifier(learning_rate=1.0, max_depth=10, min_child_weight=15, n_estimators=100, n_jobs=1, subsample=0.8, verbosity=0),
}

hyperparameter_search_space = {
    "ensemble": {
        "learning_rate": {
            "type": "float",
            "min": 0.01,
            "max": 1.0,
            "default": 1.0,
            "log_scale": True
        },
        "max_depth": {
            "type": "int",
            "min": 1,
            "max": 20,
            "default": 10
        },
        "min_child_weight": {
            "type": "int",
            "min": 1,
            "max": 30,
            "default": 15
        },
        "n_estimators": {
            "type": "int",
            "min": 10,
            "max": 1000,
            "default": 100
        },
        "subsample": {
            "type": "float",
            "min": 0.5,
            "max": 1.0,
            "default": 0.8
        },
        "colsample_bytree": {
            "type": "float",
            "min": 0.5,
            "max": 1.0,
            "default": 1.0
        },
        "gamma": {
            "type": "float",
            "min": 0.0,
            "max": 5.0,
            "default": 0.0
        },
        "reg_alpha": {
            "type": "float",
            "min": 0.0,
            "max": 5.0,
            "default": 0.0
        },
        "reg_lambda": {
            "type": "float",
            "min": 0.0,
            "max": 5.0,
            "default": 1.0
        },
        "n_jobs": {
            "type": "int",
            "min": 1,
            "max": 16,
            "default": 1
        },
        "verbosity": {
            "type": "categorical",
            "choices": [0, 1, 2, 3],
            "default": 0
        }
    }
}

class RunXGBoostClassifierAPI(BaseEstimatorAPI):

    def __init__(self, import_name):
        super().__init__(import_name)
        self.clf = None
        self.clf_name = None
        self.result_metric = None  # Store the computed metric result

    def get_hyperparameter_search_space(self):
        clf = self.params.model
        return hyperparameter_search_space[clf]

    def fit(self, args, X_train, y_train, X_test, y_test):
        clf = self.params.model
        params = self.dict_to_namespace()

        try:
            clf_params = self.params.params
        except AttributeError:
            pass

        if clf in clfs.keys():
            self.clf = clfs[clf]
            self.clf_name = clf
        else:
            raise Exception("Model {} not defined in model.py".format(clf))

        # TODO add setting params for clf

        self.clf.fit(X_train, y_train)
        logging.info("finished classifier training")

        # Compute the metric and store it as result
        self.result_metric = self.predict(X_test, y_test)
        self.result = self.result_metric

    def predict(self, X_test, y_test):
        """Predict and compute metric on test data"""
        if self.clf is None:
            raise ValueError("Classifier not fitted yet")

        if self.params.metric == "auroc":
            y_proba = self.clf.predict_proba(X_test)[:, 1]
            auroc = roc_auc_score(y_test, y_proba)
            return auroc
        elif self.params.metric == "macro_f1":
            y_pred = self.clf.predict(X_test)
            _, _, f1, _ = (
                precision_recall_fscore_support(y_test, y_pred, average='macro'))
            return f1
        else:
            error_message = "Metric {} is not supported in {} yet".format(self.params.metric, self.clf_name)
            logging.error(error_message)
            raise ValueError(error_message)


if __name__ == '__main__':
    RunXGBoostClassifierAPI(__name__).run()
