# AutoImblearn/components/model_client/base_model_client.py
import time
import json
import os
import docker
import requests
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import socket
from abc import ABC, abstractmethod
import sys


def get_free_host_port():
    """Find a free port on the host (works from inside a container using DooD)"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # let OS pick a free port
        return s.getsockname()[1]

def is_port_free(port):
    """Test if the port is free"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) != 0

class BaseDockerModelClient(ABC):
    """Build and run the docker container for the selected model

    fit: Ensure the container is running
    """
    def __init__(self, image_name, container_name, container_port=5000, volume_mounts=None, dockerfile_dir=None):
        self.image_name = image_name
        self.container_name = container_name
        self.container_port = container_port
        self.volume_mounts = volume_mounts or {}
        self.client = docker.from_env()

        # set container url
        self.host_port = get_free_host_port()
        if not is_port_free(self.host_port):
            raise Exception(f"Port {self.host_port} is not free")
        self.api_url = f"http://localhost:{self.host_port}"

        # Dockerfile
        self.dockerfile_dir = dockerfile_dir

        self.args = None
        self.container_id = None  # Initialize container_id

    # @abstractmethod
    # def transform(self, X, y=None, dockerfile_dir="."):
    #     raise NotImplementedError("Subclass must define 'transform' method'")
    #
    # @abstractmethod
    # def fit_transform(self, X, y=None, dockerfile_dir="."):
    #     raise NotImplementedError("Subclass must define 'fit_transform' method'")

    @property
    @abstractmethod
    def payload(self):
        """Subclasses must return a dict with key arguments."""
        raise NotImplementedError("Subclass must define 'payload'")

    def is_container_running(self):
        """
        Check if the Docker container with self.container_name exists and is running.
        Returns True if running, False otherwise.
        """
        try:
            container = self.client.containers.get(self.container_name)
            return container.status == 'running'
        except docker.errors.NotFound:
            # Container does not exist
            return False
        except Exception as e:
            # Other error (log it if needed)
            import logging
            logging.warning(f"Error checking container status: {e}")
            return False

    def build_image(self):
        """Build image based on Dockerfile provided"""
        logging.info(f"[⛏️ ] Building image '{self.image_name}' from {self.dockerfile_dir}...")
        # self.client.images.build(path=dockerfile_dir, tag=self.image_name)
        try:
            self.client.images.get(self.image_name)
            logging.info('found prebuilt image')
        except docker.errors.ImageNotFound:
            logging.info("Building AutoSMOTE 1.0 image")
            # TODO update this image build process to automate image genenration
            self.client.images.build(path=self.dockerfile_dir, tag=self.image_name, nocache=True)

        logging.info(f"[✓] Image '{self.image_name}' is available now.")

    def start_container(self):
        """
        Start the container
        """
        logging.info(f"[🚀] Starting container '{self.container_name}'...")
        # binds = {
        #     str(Path(local).resolve()): {'bind': container, 'mode': 'rw'}
        #     for local, container in self.volume_mounts.items()
        # }
        binds = {}
        for local, target in self.volume_mounts.items():
            host_path = str(Path(local).resolve())
            if isinstance(target, str):
                binds[host_path] = {'bind': target, 'mode': 'rw'}
            elif isinstance(target, dict):
                binds[host_path] = target  # already formatted correctly
            else:
                raise TypeError(f"Invalid volume mount target for {host_path}: {target}")

        self.container = self.client.containers.run(
            image=self.image_name,
            name=self.container_name,
            ports={f"{self.container_port}/tcp": self.host_port},
            volumes=binds,
            entrypoint=["python3","-m", "app"],
            working_dir='/code/AutoImblearn/Docker',
            detach=True
        )
        self.container_id = self.container.id  # Set container_id

    def get_container_logs(self, tail=50):
        """
        Get container logs for debugging.

        Args:
            tail: Number of lines to retrieve from end of logs

        Returns:
            String containing container logs
        """
        try:
            if not self.container_id:
                return "No container ID available"

            container = self.client.containers.get(self.container_id)
            logs = container.logs(tail=tail).decode('utf-8')
            return logs
        except Exception as e:
            return f"Failed to retrieve logs: {str(e)}"

    def stop_container(self):
        """
        Stop the running container with improved error handling.
        """
        logging.info(f"[🧹] Stopping container '{self.container_name}'...")
        try:
            container = self.client.containers.get(self.container_name)
            container.stop(timeout=5)  # Add timeout
            container.remove()
            logging.info(f"[✓] Container '{self.container_name}' removed.")
            self.container_id = None  # Clear container ID
        except docker.errors.NotFound:
            logging.info("[!] Container not found, skipping.")

    def wait_for_api(self, timeout=60):
        """
        Wait for the container's API to become responsive.
        Raise an error if the container exits or doesn't respond in time.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check container state
                container = self.client.containers.get(self.container_name)
                container.reload()
                if container.status == "exited":
                    logs = container.logs().decode(errors="ignore")
                    raise RuntimeError(f"Container exited prematurely.\nLogs:\n{logs}")

                # Check API health
                response = requests.get(f"{self.api_url}/health")
                if response.status_code == 200:
                    return True
            except requests.exceptions.ConnectionError:
                pass  # wait and retry
            except docker.errors.NotFound:
                raise RuntimeError("Container was removed unexpectedly.")

            time.sleep(1)

        raise TimeoutError("API did not become available within timeout period.")

    def ensure_container_running(self):
        """
        Ensure the Docker container is running. Build and start if needed.
        """
        try:
            container = self.client.containers.get(self.container_name)
            if container.status == 'running':
                # remove helper containers once the target container is up and running
                for c in self.client.containers.list(all=True):
                    if c.id != container.id and c.status in ("exited", "created"):
                        try:
                            c.remove(force=True)
                        except Exception as e:
                            print(f"skip {c.name}: {e}")

                print(f"Container {self.container_name} is already running.")
                ports = container.attrs['NetworkSettings']['Ports']
                internal = f"{self.container_port}/tcp"
                host_info = ports.get(internal)
                if host_info:
                    self.host_port = int(host_info[0]['HostPort'])
                    self.api_url = f"http://localhost:{self.host_port}"
                    print(f"Reusing existing container on port {self.host_port}")
                    return
                else:
                    raise RuntimeError("Could not find port mapping for the running container.")

            else:
                print(f"Container {self.container_name} is not running. Starting...")
                container.start()

        except docker.errors.NotFound:
            print("Container not found. Building and starting a new one...")
            self.build_image()
            print("Building and starting a new container...")
            self.start_container()

        # self.wait_for_api(host="localhost", port=self.host_port, path='/health')
        self.wait_for_api()
        print("API is ready.")

    def save_data_2_volume(self, data_folder_path: str, dataset_name: str, X_train, y_train=None, X_test=None, y_test=None):
        """
        Save data to docker volume
        """
        data_names = [f"X_train_{self.container_name}.csv", f"y_train_{self.container_name}.csv", f"X_test_{self.container_name}.csv",
                      f"y_test_{self.container_name}.csv"]

        for data, name in zip([X_train, y_train, X_test, y_test], data_names):
            if data is None:
                continue
            data_path = os.path.join(data_folder_path, "interim", dataset_name, name)
            np.savetxt(data_path, data, delimiter=",")

        return data_names

    def fit(self, args,  X_train, y_train=None, X_test=None, y_test=None):
        """
        Fit with training data.

        Now includes proper cleanup on error.
        """
        from ..exceptions import DockerContainerError

        logging.info(f"Fitting {self.__class__.__name__}...")
        self.args = args

        # Save temporary data files to docker volume
        try:
            data_names = self.save_data_2_volume(args.path, args.dataset, X_train, y_train, X_test, y_test)
            logging.debug("Data saved to volume")
        except Exception as e:
            raise DockerContainerError(
                f"Failed to save data to Docker volume",
                image_name=self.image_name,
                operation="save_data"
            ) from e

        try:
            self.ensure_container_running()
            logging.debug("Container is running")

            headers = {"Content-Type": "application/json"}

            # Set parameters
            response = requests.post(f"{self.api_url}/set", json=self.payload, headers=headers)
            logging.debug("Parameters set")

            if response.status_code != 201:
                raise DockerContainerError(
                    f"Failed to set parameters: HTTP {response.status_code}",
                    container_id=self.container_id,
                    image_name=self.image_name,
                    operation="set_params"
                )

            # Train model
            response = requests.post(f"{self.api_url}/train", json=self.payload, headers=headers)
            logging.debug("Training complete")
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            # Network/HTTP errors
            logs = self.get_container_logs() if self.container_id else None
            raise DockerContainerError(
                f"API request failed: {str(e)}",
                container_id=self.container_id,
                image_name=self.image_name,
                logs=logs,
                operation="train"
            ) from e

        except Exception as e:
            # Other errors
            logs = self.get_container_logs() if self.container_id else None
            logging.error(f"Error during fit: {e}")
            raise DockerContainerError(
                f"Unexpected error during training: {str(e)}",
                container_id=self.container_id,
                image_name=self.image_name,
                logs=logs,
                operation="fit"
            ) from e

        finally:
            # ALWAYS cleanup (unless using container pool)
            # For now, we stop the container after each use
            # TODO: Integrate with container pool to reuse containers
            try:
                if self.container_id:
                    logging.debug(f"Cleaning up container {self.container_id}")
                    self.stop_container()
            except Exception as cleanup_error:
                logging.error(f"Failed to cleanup container: {cleanup_error}")
