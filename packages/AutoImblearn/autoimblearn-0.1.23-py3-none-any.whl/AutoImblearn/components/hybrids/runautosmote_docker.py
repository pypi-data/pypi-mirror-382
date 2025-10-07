import os
import json
import requests
from time import sleep
import warnings

import docker
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)

import logging


class Arguments:
    def __init__(self):
        self.dataset = "imp_knn_.p"
        self.seed = 1
        self.clf = "ada"
        self.metric = "auroc"

        self.device = "cpu"
        self.cuda = "0"

        self.xpid = "AutoSMOTE"
        self.undersample_ratio = 100

        self.num_instance_specific_actions = 10
        self.num_max_neighbors = 30
        self.cross_instance_scale = 4
        self.savedir = "logs"
        self.num_actors = 10
        self.total_steps = 500
        self.batch_size = 8
        self.cross_instance_unroll_length = 2
        self.instance_specific_unroll_length = 300
        self.low_level_unroll_length = 300
        self.num_buffers = 20

        # Loss settings.
        self.entropy_cost = 0.0006
        self.baseline_cost = 0.5
        self.discounting = 1.0

        # Optimizer settings.
        self.learning_rate = 0.005
        # self.learning_rate = 0.0005
        self.grad_norm_clipping = 40.0
        self.val_ratio = 0.2
        self.test_raito = 0.2
        self.data_names = None


class RunAutoSmote:
    def __init__(self):
        self.data_folder_path = None
        self.flags = Arguments()
        os.environ["CUDA_VISIBLE_DEVICES"] = self.flags.cuda
        np.random.seed(self.flags.seed)
        self.supported_metrics = ["auroc", "macro_f1"]
        self.result = None
        # self.host_url = os.popen("ip -4 route show default").read().split()[2]      # Get the host machine's internal IP
        self.host_url = "127.0.0.1"

    def fit(self, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray, clf="ada",
            imp="gain", metric=None, args=None):
        """Train the selecting prediction pipeline selection system"""

        if self.data_folder_path is None:
            raise Exception("Please set the data folder path")

        # Set the parameters
        if args is not None:
            self.flags.metric = args.metric
            self.flags.dataset = args.dataset
        else:
            self.flags.metric = metric
            # TODO make the dataset transfer work
            self.flags.dataset = None
        # self.flags.metric = args.metric

        self.flags.clf = clf
        self.flags.data_names = ["X_train_autosmote.csv", "y_train_autosmote.csv", "X_test_autosmote.csv",
                                 "y_test_autosmote.csv"]
        #------------------
        # save x and y to data folder

        for data, name in zip([X_train, y_train, X_test, y_test], self.flags.data_names):
            data_path = os.path.join(self.data_folder_path, "interim", name)
            np.savetxt(data_path, data, delimiter=",")
            # df = pd.DataFrame(data)
            # df.to_csv(data_path, sep=",", header=False, index=False)

        # Start training
        client = docker.from_env()

        # Get the image build
        image_name = 'autosmote:version1.0'
        image_build_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "autosmote")
        try:
            client.images.get(image_name)
            logging.info('found image')
        except docker.errors.ImageNotFound:
            logging.info("Building AutoSMOTE 1.0 image")
            client.images.build(path=image_build_path, tag=image_name, nocache=True)

        # Create the container
        # volume1 = os.path.abspath("hybrids/autosmote")
        volume1 = image_build_path
        volume2 = os.path.abspath(self.data_folder_path)
        container_name = "autosmote-flask"

        logging.info('Creating AutoSMOTE container')
        try:
            container = client.containers.get(container_name)
            if container.status == "exited":
                container.start()
            logging.info('found container')
        except:
            container = client.containers.run(
                name=container_name,
                image=image_name,
                network_mode="host",
                # ports={"8080": 8080},
                volumes=[f'{volume1}:/code',
                         '/var/run/docker.sock:/var/run/docker.sock', # start container inside a container
                         f'{volume2}:/data'],
                entrypoint=["python3", "/code/app.py"],
                ipc_mode='host',
                detach=True,
            )
        timeout = 120
        stop_time = 3
        elapsed_time = 0
        logging.info('waiting container to be ready')
        while container.status != 'running' and elapsed_time < timeout:
            print(container.status)
            if container.status == 'exited':
                # TODO remove comment after project finish
                # container.remove(force=True, v=True)
                raise Exception("AutoSMOTE docker container build error")
            sleep(stop_time)
            elapsed_time += stop_time
            container = client.containers.get(container_name)
            continue

        # Wait the flask REST API to be ready
        sleep(5)

        # POST -- set parameters
        post_url = f'http://{self.host_url}:8080/set'
        headers =  {"Content-Type":"application/json"}
        response = requests.post(post_url, json.dumps(self.flags.__dict__), headers=headers)
        if response.status_code != 201:
            raise Exception("There is an error in setting AutoSMOTE parameters")

        # GET -- get result
        logging.info('Getting result from REST API')
        get_url = f'http://{self.host_url}:8080/results/' + self.flags.dataset

        # Delete container if error is encountered
        try:
            response_API = requests.get(get_url)
            self.result = response_API.json()['result']
        except Exception as e:
            container.remove(force=True, v=True)
            print(e)
            raise Exception("There is an error in getting AutoSMOTE result")


        # remove used container
        container.remove(force=True, v=True)

        # remove unuseful data files
        for name in self.flags.data_names:
            data_path = os.path.join(self.data_folder_path, "interim", name)
            if os.path.isfile(data_path):
                os.remove(data_path)

    def predict(self, X_test: np.ndarray = None, y_test: np.ndarray = None):
        return self.result


if __name__ == "__main__":
    logging.basicConfig(filename='cvd.log', level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    warnings.filterwarnings("ignore")
    run_autosmote = RunAutoSmote()
    run_autosmote.fit(clf="mlp", imp="MIRACLE", metric="auroc", train_ratio=0.2)
