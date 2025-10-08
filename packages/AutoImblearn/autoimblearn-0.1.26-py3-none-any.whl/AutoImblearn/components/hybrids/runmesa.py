
import numpy as np
from src.hybrids.mesa.mesa import Mesa
from src.customclf import clfs
from src.hybrids.mesa.arguments import args
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, classification_report, \
    average_precision_score
class RunMESA:
    def __init__(self):
        self.mesa = None
        self.metric = None
    def fit(self, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray, clf="ada", metric=None):
        if clf in clfs.keys():
            clf = clfs[clf]
            self.mesa= Mesa(args=args,base_estimator=clf,n_estimators=10)
            self.mesa.meta_fit(X_train, y_train, X_test, y_test)
            self.mesa.fit(X_train, y_train,X_test,y_test)
            self.metric = metric
        else:
            raise "Model {} not defined in model.py".format(clf)
    def predict(self, X_test: np.ndarray = None, y_test: np.ndarray = None):
        if self.metric == "auroc":
            y_proba = self.mesa.predict_proba(X_test)[:, 1]
            auroc = roc_auc_score(y_test, y_proba)
            self.result = auroc
            return auroc
        elif self.metric == "macro_f1":
            y_pred = self.mesa.predict(X_test)
            _, _, f1, _ = (
                precision_recall_fscore_support(y_test, y_pred, average='macro'))
            self.result = f1
            return f1
        else:
            raise ValueError("Metric {} is not supported in {}".format(self.metric, "MESA"))
