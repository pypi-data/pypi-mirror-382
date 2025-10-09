import docker
import json
import os

from .MLILException import MLILException


class ModelManager:
    '''
    ModelManager class used to abstract away the deployment of MLflow models to dedicated containers
    '''

    def __init__(
        self,
        model_image: str = 'ghcr.io/mlinsightlab/mlinsightlab-model-container:latest',
        model_network: str = 'mlinsightlab_model_network',
        mlflow_tracking_uri: str = 'http://mlflow:5000',
        model_port: str = '8888',
        deploy_mode='compose'
    ):
        '''
        Parameters
        ----------
        model_image : str (default 'ghcr.io/mlinsightlab/mlinsightlab-model-container:latest)'
            The image of the container to use
        model_network : str (default 'mlinsightlab_model_network')
            The network to deploy the models to
        mlflow_tracking_uri : str (default 'http://mlflow:5000')
            The tracking URI for the MLflow service on the docker network
        model_port : str (default '8888')
            The port to deploy the model to on the container
        deply_mode : str (default 'compose')
            The deployment mode to run in. One of either 'compose' or 'swarm'
        '''

        # Create docker container client
        self.docker_client = docker.from_env()

        # Store the image, network, and port on which the images will be stored
        self.model_image = model_image if model_image else os.environ['MODEL_CONTAINER_IMAGE']
        self.model_network = model_network if model_network else os.environ['MODEL_NETWORK']
        self.mlflow_tracking_uri = mlflow_tracking_uri if mlflow_tracking_uri else os.environ[
            'MLFLOW_TRACKING_URI']
        self.container_port = model_port if model_port else os.environ['MODEL_PORT']
        self.deploy_mode = deploy_mode if deploy_mode else os.environ['DEPLOY_MODE']

        # Store the containers
        self.models = []

    def deploy_model(
            self,
            model_uri: str,
            model_name: str,
            model_flavor: str,
            model_version_or_alias: str,
            use_gpu: bool = False,
            volumes: dict = None,
            requirements: str = None,
            kwargs: dict = None,
            quantization_kwargs: dict = None
    ):
        '''
        Deploy a containerized model

        Parameters
        ----------
        model_uri : str
            The URI of the model according to MLflow
        model_name : str
            The name of the model
        model_flavor : str
            The flavor of the model
        model_version_or_alias : str
            The version or alias of the model
        use_gpu : bool (default False)
            If true, will allow the container access to available GPUs
        volumes : dict or None (default None)
            If provided, a dictionary of volumes to mount to the container
        requirements: str or None (default None)
            Additional pip requirements needed to deploy the model
        kwargs: dict or None (default None)
            Additional keyword arguments needed to deploy the model
        quantization_kwargs: dict or None (default None)
            Additional quantization keyword arguments needed to deploy the model

        Returns
        -------
        success : bool
            Returns True if successful
        '''

        # Environment variables for the contianer
        environment = {
            'MODEL_URI': model_uri,
            'MODEL_FLAVOR': model_flavor,
            'MLFLOW_TRACKING_URI': self.mlflow_tracking_uri
        }
        if os.getenv('OLLAMA_HOST'):
            environment['OLLAMA_HOST'] = os.environ['OLLAMA_HOST']
        if requirements:
            environment['REQUIREMENTS'] = requirements
        if kwargs:
            environment['KWARGS'] = json.dumps(kwargs)
        if quantization_kwargs:
            environment['QUANTIZATION_KWARGS'] = json.dumps(
                quantization_kwargs)

        # Name for the container
        container_name = f'mlinsightlab__model__{model_name}__{model_flavor}__{model_version_or_alias}'

        # Run via docker if deploy_mode is via compose
        if self.deploy_mode == 'compose':

            # Run the container, giving it access to the GPU if requested
            if use_gpu:
                model_container = self.docker_client.containers.run(
                    self.model_image,
                    auto_remove=True,
                    environment=environment,
                    network=self.model_network,
                    name=container_name,
                    detach=True,
                    device_requests=[
                        docker.types.DeviceRequest(
                            count=-1, capabilities=[['gpu']])
                    ],
                    volumes=volumes
                )
            else:
                model_container = self.docker_client.containers.run(
                    self.model_image,
                    auto_remove=True,
                    environment=environment,
                    network=self.model_network,
                    name=container_name,
                    detach=True,
                    volumes=volumes
                )

        else:
            if use_gpu:
                model_container = self.docker_client.services.create(
                    self.model_image,
                    environment=environment,
                    network=self.model_network,
                    name=container_name,
                    device_requests=[
                        docker.types.DeviceRequest(
                            count=-1, capabilities=[['gpu']])
                    ],
                    volumes=volumes
                )
            else:
                model_container = self.docker_client.services.create(
                    self.model_image,
                    env=environment,
                    networks=[self.model_network],
                    name=container_name,
                )

        # Append the container properties to the models list
        self.models.append(
            {
                'model_name': model_name,
                'model_flavor': model_flavor,
                'model_version_or_alias': model_version_or_alias,
                'container_name': model_container.name
            }
        )

        return True

    def remove_deployed_model(
            self,
            model_name: str,
            model_flavor: str,
            model_version_or_alias: str,
    ):
        '''
        Remove a deployed model

        Parameters
        ----------
        model_name : str
            The name of the model
        model_flavor : str
            The flavor of the model
        model_version_or_alias : str
            The version or alias of the model

        Returns
        -------
        success : bool
            Returns True if successful
        '''

        # Search for the container name
        container_name = None
        for model in self.models:
            if model['model_name'] == model_name and model['model_flavor'] == model_flavor and model['model_version_or_alias'] == model_version_or_alias:
                container_name = model['container_name']
                break

        # Raise exception if container not found
        if container_name is None:
            raise MLILException('Container for that model not found')

        # Get the container, raise exception if not found
        if self.deploy_mode == 'compose':
            try:
                container = self.docker_client.containers.get(container_name)
            except Exception:
                raise MLILException('Container for that model not found')
        else:
            try:
                container = self.docker_client.services.get(container_name)
            except Exception:
                raise MLILException('Container for that model not found')

        # Try to stop the container, raise exception if unable to
        try:
            if self.deploy_mode == 'compose':
                container.stop()
            else:
                container.remove()
            self.models = [
                model for model in self.models if model['container_name'] != container_name
            ]
        except Exception as e:
            raise MLILException(
                f'Error trying to stop containerized model: {str(e)}')

        return True

    def remove_all_models(self):
        '''
        Remove all models
        '''

        # Go through the models and remove them all
        for model in self.models:
            self.remove_deployed_model(
                model['model_name'],
                model['model_flavor'],
                model['model_version_or_alias']
            )

        return True

    def get_model_status(
            self,
            model_name: str,
            model_flavor: str,
            model_version_or_alias: str
    ):
        '''
        Get the status of a deployed model

        Parameters
        ----------
        model_name : str
            The name of the model
        model_flavor : str
            The flavor of the model
        model_version_or_alias : str
            The version or alias of the model

        Returns
        -------
        status : str
            The status of the model container
        '''

        # Search for the container name
        container_name = None
        for model in self.models:
            if model['model_name'] == model_name and model['model_flavor'] == model_flavor and model['model_version_or_alias'] == model_version_or_alias:
                container_name = model['container_name']
                break

        # Raise exception if not found
        if not container_name:
            raise MLILException('Container for that model not found')

        # Return status
        if self.deploy_mode == 'compose':
            return self.docker_client.containers.get(container_name).status
        else:
            tasks = self.docker_client.services.get(container_name).tasks()
            tasks_states = [
                task['Status']['State'] for task in tasks
            ]
            unique_states = list(set(task_states))
            return ', '.join(unique_states)

    def get_model_logs(
            self,
            model_name: str,
            model_flavor: str,
            model_version_or_alias: str
    ):
        '''
        Get the logs of a deployed model

        Parameters
        ----------
        model_name : str
            The name of the model
        model_flavor : str
            The flavor of the model
        model_version_or_alias : str
            The version or alias of the model

        Returns
        -------
        logs : str
            The logs of the model container
        '''

        # Search for the container name
        container_name = None
        for model in self.models:
            if model['model_name'] == model_name and model['model_flavor'] == model_flavor and model['model_version_or_alias'] == model_version_or_alias:
                container_name = model['container_name']
                break

        # Raise exception if not found
        if not container_name:
            raise MLILException('Container for that model not found')

        # Return logs
        if self.deploy_mode == 'compose':
            return self.docker_client.containers.get(container_name).logs().decode('utf-8')
        else:
            logs = self.docker_client.services.get(
                container_name).logs(stdout=True)
            return ''.join(
                [log.decode('utf-8') for log in logs]
            )
