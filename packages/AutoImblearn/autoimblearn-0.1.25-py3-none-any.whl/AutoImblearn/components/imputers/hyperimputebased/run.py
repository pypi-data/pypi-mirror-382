from functools import cached_property
import os

from AutoImblearn.components.model_client.base_transformer import BaseTransformer
import pandas as pd


class RunHyperImpute(BaseTransformer):
    # TODO make model parameter work

    def __init__(self, model="ii", data_folder=None, categorical_columns=None, impute_file_path=None, **imputer_kwargs):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name=f"hyperimpute-api",
            container_name=f"{model}_container",
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
            dockerfile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__))),
        )

        self.model = model
        self.categorical_columns = categorical_columns
        self.impute_file_path = impute_file_path
        self.impute_file_name = os.path.basename(self.impute_file_path)
        self.imputer_kwargs = imputer_kwargs

    @cached_property
    def payload(self):
        return {
            "model": self.model,
            "metric": self.args.metric,
            "dataset": self.args.dataset,
            "categorical_columns": self.categorical_columns,
            "imputer_kwargs": self.imputer_kwargs,
            "impute_file_name": self.impute_file_name
        }

