import argparse
import logging
import os.path
import warnings

import joblib

from .core.runpipe import RunPipe
from .core.autoimblearn import AutoImblearn
from .processing.utils import ArgsNamespace

logging.basicConfig(filename='django_frontend.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

warnings.filterwarnings("ignore")


class AutoImblearnTraining:
    def __init__(self,
                dataset,      # Dataset name
                target,       # Set the name of the prediction target

                # Model parameters
                T_model,      # Traditional models
                repeat,

                # Pre-Processing
                aggregation,
                missing,      # Handle null values

                # K-Fold
                n_splits,     # Number of split in for K-fold

                # Resample related
                infor_method, # Choose how to handle AUDM
                resampling,
                resample_method,
                samratio,     # target sample ratio

                # Feature Importance
                feature_importance,   # Which model to use

                # GridSearchCV
                grid,         # Use Grid search to find best hyper-parameter

                # top k feature
                top_k,        # The number of features to keep

                # Auto-Imblearn related
                train_ratio,  # Only use certain ratio of dataset
                metric,       # Determine the metric
                rerun,        # Re-run the best pipeline found with 100% data
                exhaustive,   # run exhaustive search instead of AutoImblearn
                path = None,  # the path that stores all kinds of data
                ):

        self.args = ArgsNamespace(
            dataset=dataset,
            target=target,
            T_model=T_model,
            repeat=repeat,
            aggregation=aggregation,
            missing=missing,
            n_splits=n_splits,
            infor_method=infor_method,
            resampling=resampling,
            resample_method=resample_method,
            samratio=samratio,
            feature_importance=feature_importance,
            grid=grid,
            top_k=top_k,
            train_ratio=train_ratio,
            metric=metric,
            rerun=rerun,
            exhaustive=exhaustive,
            path=path,
        )

        self.model_dir = os.path.join(self.args.path, "interim", self.args.dataset, "saved_models")
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, "autoimblearn.pkl")

        # Save the result
        self.result = None   # save the final result from training

    def fit(self):
        logging.info("-------------------------")

        for arg, value in sorted(vars(self.args).items()):
            logging.info("Argument {}: {}".format(arg, value))

        # Load the data
        run_pipe = RunPipe(args=self.args)
        run_pipe.loadData()

        # Run Auto-Imblearn to find best pipeline
        checked = {}
        automl = AutoImblearn(run_pipe, metric=self.args.metric)

        if self.args.exhaustive:
            print("Exhaustive search...")
            automl.exhaustive_search(checked=checked, train_ratio=self.args.train_ratio)

        else:
            print("Finding best pipeline...")
            best_pipe, counter, best_score = automl.find_best(checked=checked, train_ratio=self.args.train_ratio)

            print(f'Final result. Best pipe: {" ".join(list(best_pipe))}, counter: {counter}, best score: {best_score}')
            if self.args.train_ratio != 1.0 and self.args.rerun:
                # Re-run the best pipeline with whole dataset to get the output score
                print("Re-running best pipeline")
                best_score = automl.run_best(best_pipe)

            logging.info(
                f'Final result. Best pipe: {" ".join(list(best_pipe))}, counter: {counter}, best score: {best_score}')
        self.result = {'best_pipeline': best_pipe, 'counter': counter, 'best_score': best_score}

    def predict(self):
        return self.result

    def save_model(self):
        if self.result:
            joblib.dump(self.result, self.model_path)

    def load_model(self):
        if os.path.exists(self.model_path):
            self.result = joblib.load(self.model_path)
        else:
            raise FileNotFoundError("No trained model found")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--dataset', type=str, default="nhanes.csv")
    parser.add_argument('--target', default="Status", type=str)  # Set the name of the prediction target

    #
    # Model parameters
    #
    parser.add_argument('--T_model', default="lr",
                        choices=["SVM", 'LSVM', 'lr', 'rf', 'mlp', 's2sl', 's2sLR', 'ensemble', 'ada',
                                 'bst'])  # Traditional models

    parser.add_argument('--repeat', default=0, type=int)

    #
    # Pre-Processing
    #
    parser.add_argument('--aggregation', default="binary", choices=["categorical", "binary"])

    parser.add_argument('--missing', default='median', choices=['median', 'mean', 'dropna', 'knn', 'ii', 'gain', 'MIRACLE', 'MIWAE'],
                        type=str)  # Handle null values

    # K-Fold
    parser.add_argument('--n_splits', default=10, type=int)  # Number of split in for K-fold

    # Resample related
    parser.add_argument('--infor_method', default='normal', choices=['normal', 'nothing'])  # Choose how to handle AUDM

    parser.add_argument('--resampling', default=False, action="store_true")
    parser.add_argument('--resample_method', default="under",
                        choices=['under', 'over', 'combined', 'herding', 's2sl_mwmote', 'MWMOTE', "smote"])
    parser.add_argument('--samratio', default=0.4, type=float)  # target sample ratio

    # Feature Importance
    parser.add_argument('--feature_importance', default='NA', choices=['NA', 'lime', 'shap'],
                        type=str)  # Which model to use

    # GridSearchCV
    parser.add_argument('--grid', default=False, action="store_true")  # Use Grid search to find best hyper-parameter

    # top k feature
    parser.add_argument('--top_k', default=-1, type=int)  # The number of features to keep

    # Auto-Imblearn related
    parser.add_argument('--train_ratio', default=1.0, type=float)  # Only use certain ratio of dataset
    parser.add_argument('--metric', default='auroc', choices=['auroc', 'macro_f1'], type=str)  # Determine the metric
    # parser.add_argument('--rerun', default=False, action="store_true")  # Re-run the best pipeline found with 100% data
    parser.add_argument('--rerun', default=False, action="store_true")  # Re-run the best pipeline found with 100% data
    parser.add_argument('--exhaustive', default=False, action="store_true") # run exhaustive search instead of AutoImblearn

    args = parser.parse_args()

    logging.info("-------------------------")

    for arg, value in sorted(vars(args).items()):
        logging.info("Argument {}: {}".format(arg, value))

    # Load the data
    run_pipe = RunPipe(args=args)
    run_pipe.loadData()

    # Run Auto-Imblearn to find best pipeline
    checked = {}
    automl = AutoImblearn(run_pipe, metric=args.metric)

    if args.exhaustive:
        print("exhaustive search")
        automl.exhaustive_search(checked=checked, train_ratio=args.train_ratio)

    else:
        best_pipe, counter, best_score = automl.find_best(checked=checked, train_ratio=args.train_ratio)

        print("Final result:", best_pipe, args.metric, counter, end=" ")
        if args.train_ratio != 1.0 and args.rerun:
            # Re-run the best pipeline with whole dataset to get the output score
            print("Re-running best pipeline")
            best_score = automl.run_best(best_pipe)

        print(best_score)
        best_pipe = list(best_pipe)
        logging.info("Final result. Best pipe: {}, {}, {}, counter: {}, best score: {}".format(best_pipe[0], best_pipe[1],
                                                                                               best_pipe[2], counter,
                                                                                               best_score))
