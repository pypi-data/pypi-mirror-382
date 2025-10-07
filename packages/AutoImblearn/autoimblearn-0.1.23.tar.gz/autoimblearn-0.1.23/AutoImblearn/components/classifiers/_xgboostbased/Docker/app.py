import logging

import numpy as np

from xgboost import XGBClassifier

from AutoImblearn.components.api import BaseEstimatorAPI

clfs = {
    "ensemble": XGBClassifier(learning_rate=1.0, max_depth=10, min_child_weight=15, n_estimators=100, n_jobs=1, subsample=0.8, verbosity=0),
}

class RunSklearnClassifierAPI(BaseEstimatorAPI):
    def get_hyperparameter_search_space(self):
        return {
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

    def fit(self, args, X_train, y_train, X_test, y_test):
        clf = self.params.model
        params = self.dict_to_namespace()
        params.metric = args.metric
        params.model = args.model

        if clf in clfs.keys():
            self.clf = clfs[clf]
            self.clf_name = clf
        else:
            raise Exception("Model {} not defined in model.py".format(clf))

        self.clf.fit(X_train, Y_train)

        # size = X_train.shape[0]
        # indices = np.arange(size)
        # np.random.shuffle(indices)
        #
        # val_idx = indices[:int(size * args.val_ratio)]
        # train_idx = indices[int(size * args.val_ratio):]
        #
        # train_X, val_X = X_train[train_idx], X_train[val_idx]
        # train_y, val_y = y_train[train_idx], y_train[val_idx]

        logging.info("finished parameter setting")

        params.ratio_map = [0.0, 0.25, 0.5, 0.75, 1.0]
        clf = get_clf(params.clf)
        return train(params, train_X, train_y, val_X, val_y, X_test, y_test, clf)

    def predict(self, dataset_name: str):
        pass
