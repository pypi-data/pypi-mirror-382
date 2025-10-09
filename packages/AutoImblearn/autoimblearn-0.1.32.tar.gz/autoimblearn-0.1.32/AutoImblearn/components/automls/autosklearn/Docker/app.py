import os
import shutil
import re

from flask import Flask, jsonify, request
import pandas as pd
from sklearn.model_selection import train_test_split
from autosklearn.metrics import f1_macro, roc_auc

import autosklearn.classification

app = Flask(__name__)

params = {}

# POST function to set training parameters
@app.route('/set', methods=['POST'])
def set_params():
    """ Set training parameters """
    data = request.get_json()
    global params
    for key, value in data.items():
        params[key] = value
    if 'metric' not in params or 'dataset' not in params or 'target' not in params:
        raise Exception("data not complete, need to include metric, dataset, and target")

    return jsonify(params), 201

# GET function to retrieve all books
@app.route('/results/<dataset_name>', methods=['GET'])
def get_result(dataset_name: str):
    """ Train the auto-sklearn and return the result in json format """
    global params
    shutil.rmtree('/tmp', ignore_errors=True)
    null_values = ['', ' ']
    data_path = os.path.join("/data/raw", params['dataset'])
    if not os.path.isfile(data_path):
        return jsonify({"result": "file not exist"}, 200)

    file_type = re.search("[^\.]*$", data_path).group()
    if file_type == "csv":
        df = pd.read_csv(data_path, na_values=null_values)
    elif file_type in ["xls,", "xlsx,", "xlsm,", "xlsb,", "odf,", "ods,", "odt"]:
        df = pd.read_excel(data_path, na_values=null_values)
    else:
        return jsonify({"error": "file type of {} not supported".format(dataset_name)}), 400

    headers = list(df.columns.values)
    target = params["target"]
    headers.remove(target)

    X = df[headers]
    y = df[target]

    # The AutoML part
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.1
    )
    automl = autosklearn.classification.AutoSklearnClassifier(
        time_left_for_this_task=120,
        per_run_time_limit=30,
        tmp_folder="/tmp/autosklearn_classification_example_tmp",
        metric=roc_auc,
        resampling_strategy="cv",
        resampling_strategy_arguments={"folds": 10}
    )

    if params["metric"] == "auroc":
        automl.set_params(**{"metric": roc_auc})
    elif params["metric"] == "macro_f1":
        automl.set_params(**{"metric": f1_macro})
    else:
        raise Exception("Evaluation metric {} is not yet supported".format(params["metric"]))

    # Train
    automl.fit(X_train, y_train)

    # Predict
    if params["metric"] == "auroc":
        y_proba = automl.predict_proba(X_test)
        result = roc_auc(y_test, y_proba)
    elif params["metric"] == "macro_f1":
        y_pred = automl.predict(X_test)
        result = f1_macro(y_test, y_pred)
    else:
        raise Exception("Evaluation metric {} is not yet supported".format(params["metric"]))

    return jsonify({"result": result}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)