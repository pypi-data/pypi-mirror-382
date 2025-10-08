# AutoImblearn/components/imputers/sklearnbased/run.py
from functools import cached_property
import os

from AutoImblearn.components.model_client.base_transformer import BaseTransformer


class RunSklearnImpute(BaseTransformer):
    # TODO make model parameter work

    def __init__(self, model="ii", data_folder=None, categorical_columns=None, impute_file_path=None, **imputer_kwargs):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name=f"sklearnimpute-api",
            container_name=f"{model}_container",
            # TODO make port dynamic
            container_port=8080,
            volume_mounts={
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Docker'):
                    "/code/AutoImblearn/Docker",
                data_folder: {
                    'bind': '/data',
                    'mode': 'rw'
                },
                "/var/run/docker.sock": "/var/run/docker.sock",  # give container full control of docker
            },  # mount current dir
            dockerfile_dir = os.path.dirname(os.path.abspath(__file__)),
        )
        self.model = model
        self.categorical_columns = categorical_columns
        self.impute_file_path = impute_file_path
        self.impute_file_name = os.path.basename(self.impute_file_path)
        self.imputer_kwargs = imputer_kwargs

    @cached_property
    def payload(self):
        return {
            "metric": self.args.metric,
            "model": self.model,
            "dataset": self.args.dataset,
            "categorical_columns": self.categorical_columns,
            "imputer_kwargs": self.imputer_kwargs,
            "impute_file_name": self.impute_file_name
        }

