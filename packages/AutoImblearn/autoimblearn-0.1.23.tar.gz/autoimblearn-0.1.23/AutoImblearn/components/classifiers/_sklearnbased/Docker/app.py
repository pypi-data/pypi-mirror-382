import logging

import numpy as np
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, classification_report, \
    average_precision_score

from AutoImblearn.components.api import BaseEstimatorAPI

clfs = {
    "lr": LogisticRegression(random_state=42, max_iter=500, solver='lbfgs'),
    "mlp": MLPClassifier(alpha=1, random_state=42, max_iter=1000),
    "ada": AdaBoostClassifier(random_state=42),
    "svm": svm.SVC(random_state=42, probability=True, kernel='linear'),
    # "SVM": svm.SVC(random_state=42, probability=True, kernel='poly'),
    # "rf": RandomForestClassifier(random_state=42),
    # "ensemble": XGBClassifier(learning_rate=1.0, max_depth=10, min_child_weight=15, n_estimators=100, n_jobs=1, subsample=0.8, verbosity=0),
    # "bst": GradientBoostingClassifier(random_state=42),
}

hyperparameter_search_space = {
    "lr": {
        "penalty": {
            "type": "categorical",
            "choices": ["l2", "l1", "elasticnet", "none"],
            "default": "l2"
        },
        "C": {
            "type": "float",
            "min": 0.01,
            "max": 10.0,
            "default": 1.0,
            "log_scale": True
        },
        "solver": {
            "type": "categorical",
            "choices": ["lbfgs", "liblinear", "saga", "newton-cg", "sag"],
            "default": "lbfgs"
        },
        "max_iter": {
            "type": "int",
            "min": 100,
            "max": 1000,
            "default": 500
        }
    },
    "mlp": {
        "hidden_layer_sizes": {
            "type": "categorical",
            "choices": [(50,), (100,), (100, 50), (100, 100)],
            "default": (100,)
        },
        "activation": {
            "type": "categorical",
            "choices": ["relu", "tanh", "logistic"],
            "default": "relu"
        },
        "solver": {
            "type": "categorical",
            "choices": ["adam", "sgd", "lbfgs"],
            "default": "adam"
        },
        "alpha": {
            "type": "float",
            "min": 1e-5,
            "max": 1.0,
            "default": 1.0,
            "log_scale": True
        },
        "learning_rate": {
            "type": "categorical",
            "choices": ["constant", "invscaling", "adaptive"],
            "default": "constant"
        },
        "max_iter": {
            "type": "int",
            "min": 200,
            "max": 2000,
            "default": 1000
        }
    },
    "ada": {
        "n_estimators": {
            "type": "int",
            "min": 10,
            "max": 1000,
            "default": 50
        },
        "learning_rate": {
            "type": "float",
            "min": 0.01,
            "max": 2.0,
            "default": 1.0,
            "log_scale": True
        },
        "algorithm": {
            "type": "categorical",
            "choices": ["SAMME", "SAMME.R"],
            "default": "SAMME.R"
        }
    },
    "svm": {
        "C": {
            "type": "float",
            "min": 0.01,
            "max": 10.0,
            "default": 1.0,
            "log_scale": True
        },
        "kernel": {
            "type": "categorical",
            "choices": ["linear", "poly", "rbf", "sigmoid"],
            "default": "linear"
        },
        "degree": {
            "type": "int",
            "min": 2,
            "max": 5,
            "default": 3  # used in poly kernel
        },
        "gamma": {
            "type": "categorical",
            "choices": ["scale", "auto"],
            "default": "scale"
        },
        "coef0": {
            "type": "float",
            "min": 0.0,
            "max": 1.0,
            "default": 0.0
        },
        "probability": {
            "type": "categorical",
            "choices": [True, False],
            "default": True
        }
    },
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

class RunSklearnClassifierAPI(BaseEstimatorAPI):

    def __init__(self, import_name):
        super().__init__(import_name)
        self.clf = None

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

    def predict(self, X_test, y_test):
        if self.params.metric == "auroc":
            y_proba = self.clf.predict_proba(X_test)[:, 1]
            auroc = roc_auc_score(y_test, y_proba)
            self.result = auroc
            return auroc
        elif self.params.metric == "macro_f1":
            y_pred = self.clf.predict(X_test)
            _, _, f1, _ = (
                precision_recall_fscore_support(y_test, y_pred, average='macro'))
            self.result = f1
            return f1
        else:
            error_message = "Metric {} is not supported in {} yet".format(self.params.metric, self.clf_name)
            logging.error(error_message)
            raise ValueError(error_message)
