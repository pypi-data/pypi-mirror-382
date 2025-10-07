from flask import Flask, jsonify, request
import os
import re
import shutil
import pandas as pd
from sklearn.model_selection import train_test_split
import h2o
from h2o.sklearn import H2OAutoMLClassifier

app = Flask(__name__)
params = {}

@app.route('/set', methods=['post'])
def set_params():
    """ Set training parameters """
    data = request.get_json()
    global params
    for key, value in data.items():
        params[key] = value
    if 'metric' not in params or 'dataset' not in params or 'target' not in params:
        raise Exception("data not complete, need to include metric, dataset, and target")

    return jsonify(params), 201

@app.route('/results/<dataset_name>', methods=['GET'])
def get_result(dataset_name: str):
    """ Train the auto-sklearn and return the result in json format """
    h2o.init(ip="localhost", port=54323)
    global params
    # shutil.rmtree('/tmp', ignore_errors=True)
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
    y = df[[target]]

    # The AutoML part
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y,test_size=0.1
    )


    if params["metric"] == "auroc":
        model = H2OAutoMLClassifier(max_models=10, seed=42, sort_metric='auc')
    else:
        raise Exception("Evaluation metric {} is not yet supported".format(params["metric"]))


    model.fit(X_train, y_train)
    from sklearn.metrics import  roc_auc_score
    if params["metric"] == "auroc":
        y_proba = model.predict_proba(X_test)
        result = roc_auc_score(y_test, y_proba)
    else:
        raise Exception("Evaluation metric {} is not yet supported".format(params["metric"]))
    return jsonify({"result": result}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)