import os
import numpy as np
import logging
import docker
import time
import requests
import sys
sys.path.append("..")
from ...processing.utils import DATA_VOLUME_PATH
from time import sleep
import json

class Arguments:
    def __init__(self):
        self.dataset = "nhanes.csv"
        self.metric = "auroc"
        self.target = "Status"

        self.device = "cpu"
        self.cuda = "0"

        self.val_ratio = 0.1,
        self.test_raito = 0.1,


class RunTPOT:
    def __init__(self):
        self.flags = Arguments()
        os.environ["CUDA_VISIBLE_DEVICES"] = self.flags.cuda
        np.random.seed(42)
        self.supported_metrics = ["auroc, macro_f1"]
        self.result = None

    def fit(self, metric=None):
        self.flags.metric = metric

        # Start training
        client = docker.from_env()
        image_name = 'tpot:version1.0'
        # Get the image build
        try:
            client.images.get(image_name)
            logging.info('found image')
        except docker.errors.ImageNotFound:
            logging.info("Building tpot 1.0 image")
            client.images.build(path="tpot/", tag=image_name, nocache=True)

        volume1 = os.path.abspath("tpot")
        volume2 = os.path.abspath(DATA_VOLUME_PATH)
        container_name = "tpot-flask"

        try:
            container = client.containers.get(container_name)
            # container.remove(force=True, v=True)
            # print("container remove")
            logging.info('found container')
        except:
            container = client.containers.run(
                #docker run -v /var/run/docker.sock:/var/run/docker.sock --name containerB myimage ...
                name=container_name,
                image=image_name,
                ports={"8082": 8082},
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
        print(container.status)
        while container.status != 'running' and elapsed_time < timeout:
            if container.status == 'exited':
                raise Exception("TPOT docker container build error")
            sleep(stop_time)
            elapsed_time += stop_time
            container = client.containers.get(container_name)
            continue
        print(container.status)
        post_url = 'http://127.0.0.1:8082/set'
        headers = {"Content-Type": "application/json"}
        response = requests.post(post_url, json.dumps(self.flags.__dict__), headers=headers)
        if response.status_code != 201:
            raise Exception("There is an error in setting TPOT parameters")

        # GET -- get result
        logging.info('Getting result from REST API')
        get_url = 'http://127.0.0.1:8082/results/' + self.flags.dataset
        response_API = requests.get(get_url)
        self.result = response_API.json()

        container.remove(force=True, v=True)

    def predict(self):
        return self.result


if __name__ == "__main__":
    tmp = RunTPOT()
    tmp.fit("auroc")

