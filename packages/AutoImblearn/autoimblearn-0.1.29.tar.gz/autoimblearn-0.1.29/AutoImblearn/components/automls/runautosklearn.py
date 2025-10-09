import json
import os
import numpy as np
import logging
import docker
import requests
from time import sleep

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


class RunAutoSklearn:
    def __init__(self):
        self.flags = Arguments()
        os.environ["CUDA_VISIBLE_DEVICES"] = self.flags.cuda
        self.supported_metrics = ["auroc, macro_f1"]
        self.result = None

    def fit(self, X_train: np.ndarray, y_train: np.ndarray, metric=None):
        self.flags.metric = metric


        # Start training
        client = docker.from_env()

        # Get the image build
        image_name = 'autosklearn:version1.0'
        try:
            client.images.get(image_name)
            logging.info('found image')
        except docker.errors.ImageNotFound:
            logging.info("Building AutoSklearn 1.0 image")
            client.images.build(path="autosklearn/", tag=image_name, nocache=True)
        # Create the container
        volume1 = os.path.abspath("autosklearn")
        volume2 = os.path.abspath(DATA_VOLUME_PATH)
        container_name = "autosklearn-flask"

        logging.info('Creating AutoSklearn container')

        try:
            container = client.containers.get(container_name)
            # container.remove(force=True, v=True)
            # print("container remove")
            logging.info('found container')
        except:
            container = client.containers.run(
                name=container_name,
                image=image_name,
                ports={"8080": 8080},
                volumes=['{}:/code'.format(volume1),
                         # start container from a container code
                         # '/var/run/docker.sock:/var/run/docker.sock',
                         '{}:/data'.format(volume2)],
                entrypoint="python3 /code/app/app.py",
                detach=True,
            )
        timeout = 120
        stop_time = 3
        elapsed_time = 0
        logging.info('waiting container to be ready')

        while container.status != 'running' and elapsed_time < timeout:
            if container.status == 'exited':
                raise Exception("AutoSklearn docker container build error")
            sleep(stop_time)
            elapsed_time += stop_time
            container = client.containers.get(container_name)
            continue
        # print(container.status)
        # POST -- set parameters
        post_url = 'http://127.0.0.1:8080/set'
        headers =  {"Content-Type":"application/json"}
        response = requests.post(post_url, json.dumps(self.flags.__dict__), headers=headers)
        if response.status_code != 201:
            raise Exception("There is an error in setting AutoSklearn parameters")

        # GET -- get result
        logging.info('Getting result from REST API')
        get_url = 'http://127.0.0.1:8080/results/' + self.flags.dataset
        response_API = requests.get(get_url)
        self.result = response_API.json()
        print(self.result)
        container.remove(force=True, v=True)

    def predict(self, X_test: np.ndarray = None, y_test: np.ndarray = None):
        return self.result


if __name__ == "__main__":

    tmp = RunAutoSklearn()
    tmp.fit(None, None,  "auroc")
