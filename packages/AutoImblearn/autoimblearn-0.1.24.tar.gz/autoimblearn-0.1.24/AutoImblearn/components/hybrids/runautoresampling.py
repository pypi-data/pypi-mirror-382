import json
import os
import numpy as np
import logging
import docker
import requests
from time import sleep


import sys
sys.path.append("..")
from ...processing.utils import DATA_VOLUME_PATH


class Arguments:
    def __init__(self):
        self.dataset = "nhanes.csv"
        self.metric = "auroc"
        self.target = "Status"

        self.device = "cpu"
        self.cuda = "0"

        self.val_ratio = 0.1,
        self.test_raito = 0.1,


class RunAutoRSP:
    def __init__(self):
        self.flags = Arguments()
        os.environ["CUDA_VISIBLE_DEVICES"] = self.flags.cuda
        self.supported_metrics = ["auroc, macro_f1"]
        self.result = None

    def fit(self, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray, metric=None):
        self.flags.metric = metric

        import pandas as pd
        train_data = np.hstack((X_train, y_train.reshape(-1, 1)))
        test_data = np.hstack((X_test, y_test.reshape(-1, 1)))
        train_df = pd.DataFrame(train_data,columns=[f'feature_{i}' for i in range(X_train.shape[1])] + ['target'])
        test_df = pd.DataFrame(test_data,columns=[f'feature_{i}' for i in range(X_test.shape[1])] + ['target'])
        train_df.to_csv('../../data/interim/autorsp_train.csv', index=False)
        test_df.to_csv('../../data/interim/autorsp_test.csv', index=False)

        client = docker.from_env()

        # Get the image build
        image_name = 'autorsp:version1.0'
        try:
            client.images.get(image_name)
            logging.info('found image')
        except docker.errors.ImageNotFound:
            logging.info("Building AutoResampling 1.0 image")
            client.images.build(path="autorsp/", tag=image_name, nocache=True)
        # Create the container
        volume1 = os.path.abspath("autorsp")
        volume2 = os.path.abspath(DATA_VOLUME_PATH)
        container_name = "autorsp-flask"

        logging.info('Creating AutoResampling container')

        try:
            container = client.containers.get(container_name)
            logging.info('found container')
        except:
            container = client.containers.run(
                name=container_name,
                image=image_name,
                ports={"8083": 8083},
                volumes=['{}:/code'.format(volume1),
                         '{}:/data'.format(volume2)],
                entrypoint="Rscript /code/app/autorsp.R",
                detach=True,
            )
        timeout = 120
        stop_time = 3
        elapsed_time = 0
        logging.info('waiting container to be ready')
        print(container.status)
        while container.status != 'running' and elapsed_time < timeout:
            if container.status == 'exited':
                raise Exception("AutoResampling docker container build error")
            sleep(stop_time)
            elapsed_time += stop_time
            container = client.containers.get(container_name)
            continue
        print(container.status)

        sleep(5)
        # logging.info('Getting result from REST API')
        get_url = "http://0.0.0.0:8083/result?metric={}&target=target".format(metric)
        print(get_url)
        response_API = requests.get(get_url)
        self.result = response_API.json()
        print(self.result)

        container.remove(force=True, v=True)

    def predict(self, X_test: np.ndarray = None, y_test: np.ndarray = None):
        return self.result

if __name__ == "__main__":
    import pickle
    from src.utils import  Samplar
    file_path = '../../data/interim/imp_gain_.p'
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    train_sampler = Samplar(np.array(data[0]), np.array(data[1]))
    for X_train, y_train, X_test, y_test in train_sampler.apply_kfold(10):
        run = RunAutoRSP()
        run.fit(X_train, y_train, X_test, y_test, metric="macro_f1")
        break