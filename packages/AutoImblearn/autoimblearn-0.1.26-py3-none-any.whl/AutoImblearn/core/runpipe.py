# AutoImblearn/core/runpipe.py
import os
import pickle
import numpy as np
import pandas as pd
import logging

from ..processing.utils import DataLoader, Samplar, Result
from ..processing.preprocessing import DataPreprocess
from ..pipelines.customrsp import CustomResamplar
from ..pipelines.customimputation import CustomImputer
from ..pipelines.customclf import CustomClassifier
from ..pipelines.customhbd import CustomHybrid
from ..pipelines.customautoml import CustomAutoML


def average(lst):
    return sum(lst) / len(lst)

class RunPipe:
    """ Run different pipelines and save the trained results
    Parameters
    ----------
    args : The command line arguments that define how the code should run

    Attributes
    ----------
    preprocessor : Split data into features (X) and target (y)
    args : The command line arguments that define how the code should run
    X : Features
    y : Target
    saver : The class to save trained results and load saved results

    """
    def __init__(self, args=None):
        self.preprocessor = None
        self.args = args
        self.X = None
        self.y = None

        self.dataloader = None
        self.saver = None

    def loadData(self):

        # Load data
        logging.info("Loading Start")
        self.dataloader = DataLoader(self.args.dataset, path=self.args.path)
        data = self.dataloader.train_loader()
        logging.info("Loading Done")

        # Load saved result if it exists
        self.saver = Result(str(self.args.train_ratio), self.args.metric, self.args.dataset, dataloader=self.dataloader)
        self.saver.load_saved_result()

        # Proprocess data
        logging.info("Preprocessing Start")
        self.preprocessor = DataPreprocess(data, self.args)

    def stratifiedSample(self, X, y, train_ratio):
        data = pd.concat([X, y], axis=1)
        new_data = data.groupby('Status', group_keys=False).apply(lambda x: x.sample(frac=train_ratio))
        new_data.sort_index(inplace=True)
        new_data.reset_index(inplace=True, drop=True)
        columns = list(new_data.columns.values)
        columns.remove("Status")
        X = new_data[columns].copy()
        y = new_data["Status"].copy()
        return X, y

    def impute_data(self, imp, train_ratio=1.0):
        """
        Perform data imputation and delegate the storage responsibility to the model.

        This method checks whether an imputed dataset already exists. If so, it loads
        the stored imputation results from disk. Otherwise, it preprocesses the raw data,
        applies the specified imputation method, and lets the model handle persistence
        of the imputed output.

        Parameters
        ----------
        imp : str
            The name of the imputation method to apply (e.g., 'mean', 'knn', etc.).
        train_ratio : float, optional (default=1.0)
            The proportion of the dataset to retain after imputation. If less than 1.0,
            a stratified subsample is returned to preserve class distribution.

        Returns
        -------
        X : array-like
            The imputed feature matrix.
        y : array-like
            The corresponding target labels.
        """
        impute_file_name = "imp_" + imp + ".p"
        impute_file_path = os.path.join(self.dataloader.get_interim_data_folder(), self.args.dataset, impute_file_name)

        if os.path.exists(impute_file_path):
            # Load Saved imputation files
            with open(impute_file_path, "rb") as f:
                X, y = pickle.load(f)
        else:
            # Compute imputation files
            X, y = self.preprocessor.preprocess(self.args)
            imputer = CustomImputer(method=imp, data_folder=self.args.path, dataset_name=self.args.dataset, impute_file_path=impute_file_path)
            X = imputer.fit_transform(X, y)

        if train_ratio != 1.0:
            X, y = self.stratifiedSample(X, y, train_ratio)
        return X, y

    def fit_automl(self, pipe, train_ratio=1.0):
        if len(pipe) != 1:
            raise ValueError("Pipeline {} length is not correct, not a AutoML method pipeline".format(pipe))

        # Load saved result if it exists
        # if self.saver.is_in(pipe):
        #     result = self.saver.get(pipe)
        #     return result

        automl = pipe[0]

        X, y = self.preprocessor.preprocess(self.args)

        # fit
        logging.info("\t Training of {} Start".format(pipe))
        trainer = CustomAutoML(self.args, automl)
        trainer.train(X, y)
        logging.info("\t Training of {} Ended".format(pipe))

        # Predict
        logging.info("\t Predicting of {} Start".format(pipe))
        result = trainer.predict()
        logging.info("\t Predicting of {} Ended".format(pipe))

        self.args.repeat += 1

        self.saver.append(pipe, result)
        return result


    def fit_hybrid(self, pipe, train_ratio=1.0):
        if len(pipe) != 2:
            raise ValueError("Pipeline {} length is not correct, not a hybrid method pipeline".format(pipe))

        # Load saved result if it exists
        # if self.saver.is_in(pipe):
        #     result = self.saver.get(pipe)
        #     return result

        # Start training pipeline
        imp, hbd = pipe

        X, y = self.impute_data(imp=imp, train_ratio=train_ratio)
        logging.info("Imputation Done")

        results = []
        train_sampler = Samplar(np.array(X), np.array(y))

        for X_train, y_train, X_test, y_test in train_sampler.apply_kfold(self.args.n_splits):
            logging.info("\t Training in fold {} Start".format(self.args.repeat))
            trainer = CustomHybrid(args=self.args, pipe=pipe)
            if self.args.metric not in trainer.hbd.supported_metrics:
                raise ValueError("Metric {} not yet supported for model {}".format(self.args.metric, hbd))
            trainer.train(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test)
            logging.info("\t Training in fold {} Done".format(self.args.repeat))


            trainer.predict(X_test=X_test, y_test=y_test)

            results.append(trainer.result)

            del trainer

            self.args.repeat += 1

        self.saver.append(pipe, average(results))
        return average(results)


    def fit(self, pipe, train_ratio=1.0):
        if len(pipe) != 3:
            raise ValueError("Pipeline {} length is not correct, not a regular method pipeline")

        # Load saved result if it exists
        # if self.saver.is_in(pipe):
        #     result = self.saver.get(pipe)
        #     return result

        # Run the pipeline
        imp, rsp, clf = pipe

        #
        # Imputation level
        #
        X, y = self.impute_data(imp=imp, train_ratio=train_ratio)

        logging.info("Imputation Done")
        train_sampler = Samplar(np.array(X), np.array(y))

        results = []
        for X_train, y_train, X_test, y_test in train_sampler.apply_kfold(self.args.n_splits):
            logging.info("\t Fold {}".format(self.args.repeat))

            #
            # Resampling level
            #
            resamplar = CustomResamplar(X_train, y_train)
            # params = param_loader()
            # sam_ratio = params[imp][rsp][clf] / 10 if params[imp][rsp][clf] else 1
            # sam_ratio = 1
            # if resamplar.need_resample(sam_ratio):
            if resamplar.need_resample():
                logging.info("\t Re-Sampling Started")
                # X_train, y_train = resamplar.resample(self.args, rsp=rsp, ratio=sam_ratio)
                X_train, y_train = resamplar.resample(self.args, rsp=rsp)
                logging.info("\t Re-Sampling Done")

            #
            # Classification level
            #
            logging.info("\t Training in fold {} Start".format(self.args.repeat))
            trainer = CustomClassifier(self.args)
            trainer.train(X_train, y_train, clf=clf)
            logging.info("\t Training in fold {} Done".format(self.args.repeat))

            # Validation of the result
            trainer.predict(X_test, y_test)

            results.append(trainer.result)

            del trainer

            self.args.repeat += 1

        self.saver.append(pipe, average(results))
        return average(results)


if __name__ == "__main__":
    # import logging
    import warnings

    logging.basicConfig(filename='django_frontend.log', level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    warnings.filterwarnings("ignore")

    class Args:
        def __init__(self):
            self.train_ratio=1.0
            self.n_splits = 10
            self.repeat = 0
            self.dataset = "nhanes.csv"
            self.metric = "auroc"
            self.target = "Status"
    args = Args()
    run_pipe = RunPipe(args)
    # run_pipe.fit("MIRACLE", "mwmote", "lr")
    # print(run_pipe.fit_hybrid(["imp", "hbd"]))
    # print(run_pipe.fit(["imp", "rsp", "clf"]))
    run_pipe.loadData()
    run_pipe.fit_hybrid(["median", "autosmote"])
    # print(run_pipe.fit_automl(["autosklearn"]))
