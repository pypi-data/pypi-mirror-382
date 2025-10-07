import logging

import numpy as np
from sklearn.multiclass import OneVsRestClassifier
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, classification_report, \
    average_precision_score
# from AutoImblearn.components.classifiers import RunSklearnClf, RunXGBoostClf

# from xgboost import XGBClassifier
from sklearn.ensemble import GradientBoostingClassifier

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

class CustomClassifier:
    def __init__(self, args):
        # def __init__(self, X: pd.DataFrame, Y: pd.DataFrame):
        self.args = args
        # self.f1 = None
        # self.precision = None
        # self.recall = None
        # self.w_precision = None
        # self.w_recall = None
        # self.auroc = None
        # self.auprc = None
        #
        # self.c_index = None
        self.clf = None
        self.clf_name = None

    def train(self, X_train: np.ndarray, Y_train: np.ndarray, clf=None):
        # Train classifier
        if clf in clfs.keys():
            self.clf = clfs[clf]
            self.clf_name = clf
        else:
            raise Exception("Model {} not defined in model.py".format(clf))

        self.clf.fit(X_train, Y_train)

    def predict(self, X_test: np.ndarray, Y_test: np.ndarray):

        if self.args.metric == "auroc":
            y_proba = self.clf.predict_proba(X_test)[:, 1]
            auroc = roc_auc_score(Y_test, y_proba)
            self.result = auroc
            return auroc
        elif self.args.metric == "macro_f1":
            y_pred = self.clf.predict(X_test)
            _, _, f1, _ = (
                precision_recall_fscore_support(Y_test, y_pred, average='macro'))
            self.result = f1
            return f1
        else:
            raise ValueError("Metric {} is not supported in {}".format(self.args.metric, self.clf_name))
