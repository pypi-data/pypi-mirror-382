from typing import Union, List, Optional, Any
from pathlib import Path
import getpass
import ollama
import httpx
import boto3
import json
import os

# from .endpoints import *

from .MLILException import MLILException
from .user_mgmt import _create_user, _delete_user, _verify_password, _issue_new_password, _get_user_role, _update_user_role, _list_users
from .key_mgmt import _create_api_key
from .model_mgmt import _deploy_model, _undeploy_model, _list_models, _predict, _get_model_logs
from .platform_mgmt import _reset_platform, _get_platform_resource_usage, _restart_jupyter
from .data_mgmt import _get_variable, _list_variables, _set_variable, _delete_variable, _get_predictions, _list_prediction_models
from .endpoints import OLLAMA


class MLILClient:
    '''
    Client for interacting with the ML Insight Lab (MLIL) Platform

    Parameters
    ----------
    use_cached_credentials: bool (default True)
        Login using credentials that have been previosuly cached on your system.
        Bypasses the interactive login flow.
    auth: dict or None (default None)
        Dictionary of credentials to use for the instantiated client.
        Must be of structure:
        {
            'username':username,
            'key':your api key,
            'password':your user password,
            'url':the base URL of your platform
        }
    cache_credentials: bool (default True)
        If you provided an auth dictionary, whether you would like to cache those credentials for future use.
    set_mlflow_environment_variables: bool (default True)
        If true, sets mlflow variables needed to interface with the lab.
    ssl_verify: bool (default True)
        Whether to verify SSL certificates when making requests to the server.
        NOTE: Not validating SSL certificates is discouraged, but necessary in some scenarios, such as using self-signed certificates. Use at your discretion!
    '''

    def __init__(
        self,
        use_cached_credentials: bool = True,
        auth: dict | None = None,
        cache_credentials: bool = True,
        set_mlflow_environment_variables=True,
        ssl_verify=True
    ):

        # Set SSL verify
        self.ssl_verify = ssl_verify

        # Configuration path
        self.config_path = Path((f'{Path.home()}/.mlil/config.json'))

        # Try to log in using cached credentials as directed
        if auth is None:
            auth = self._login(use_cached_credentials=use_cached_credentials)

        # Get the authentication information from the auth credentials
        self.username = auth.get('username')
        self.api_key = auth.get('key')
        self.url = auth.get('url')
        self.password = auth.get('password')

        # Raise any errors as needed
        if not self.username or not self.api_key or not self.password:
            raise ValueError(
                'You must provide your username, password, and API key.')
        if not self.url:
            raise ValueError(
                'You must provide the base URL of your instance of the platform.')

        # Set and save credentials as directed
        self.creds = {'username': self.username, 'key': self.api_key}
        if cache_credentials:
            self._save_credentials(auth)

        # Set mlflow environment variables
        if set_mlflow_environment_variables:
            if not os.getenv('MLFLOW_TRACKING_URI'):
                os.environ['MLFLOW_TRACKING_URI'] = self.url.replace(
                    '/api', '/mlflow')
            if not os.getenv('MLFLOW_TRACKING_USERNAME'):
                os.environ['MLFLOW_TRACKING_USERNAME'] = self.username
            if not os.getenv('MLFLOW_TRACKING_PASSWORD'):
                os.environ['MLFLOW_TRACKING_PASSWORD'] = self.password

        # Create ollama client
        self.ollama = ollama.Client(
            host=f'{self.url}/{OLLAMA}',
            auth=httpx.BasicAuth(
                username=self.username,
                password=self.api_key
            ),
            verify=self.ssl_verify
        )

        # Create s3 client
        s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')

        if s3_endpoint_url is None:
            protocol = self.url.split('://')[0]
            host = self.url.split('://')[-1].replace('/api', '')
            s3_endpoint_url = f'{protocol}://s3.{host}'

        self.s3 = boto3.client(
            's3',
            endpoint_url=s3_endpoint_url,
            aws_access_key_id=self.username,
            aws_secret_access_key=self.password,
            verify=self.ssl_verify
        )

    '''
    ###########################################################################
    ########################## Login Operations ################################
    ###########################################################################
    '''

    def _login(self, use_cached_credentials):
        '''
        Authenticates user.

        Not meant to be called by the user directly.
        '''

        # Load the stored credentials if possible
        if use_cached_credentials and self.config_path.exists():
            return self._load_stored_credentials()

        else:

            # Check for environment variables indicating that the user is logging in from Jupyter
            url = os.getenv('API_URL')
            confirmation = ''

            # Ask the user if they're logging in from the platform
            if url is not None:
                while confirmation not in ['y', 'n']:
                    confirmation = input(
                        'It appears you are using this client from within the platform. Is that true? [y]/n ').lower()
                    if confirmation == '':
                        confirmation = 'y'

            # If the user is not in the Jupyter instance of the platform, then ask for the platform URL
            if confirmation == 'n' or url is None:
                url = input('Enter platform URL: ')
                if not url.endswith('api'):
                    url += '/api'

            # Get all other configuration parameters
            username = input('Enter username: ')
            password = getpass.getpass('Enter password: ')
            api_key = getpass.getpass(
                'Enter API key (or leave blank to generate new): ')

            # Generate a new API key
            if not api_key:
                generate_new = input(
                    'Generate new API key? [y]/n ').lower() in ['', 'y']
                if generate_new:
                    api_key = self.issue_api_key(
                        username=username, password=password, url=url).json()

            # Verify the password
            resp = self.verify_password(url=url, creds={
                                        'username': username, 'key': api_key}, username=username, password=password)

            # Verify that the response is okay, raise exception otherwise
            if resp:
                print(f'User verified. Welcome {username}!')
            else:
                print('User not verified.')
                raise MLILException(str(resp.json()))

            # Return authentication information
            auth = {'username': username, 'key': api_key,
                    'url': url, 'password': password}
            return auth

    def _load_stored_credentials(self):
        '''
        Loads stored credentials from the config file.

        This function is not meant to be called by the user directly.
        '''

        # Open and load the file
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _save_credentials(self, auth):
        '''
        Saves credentials to the config file.

        This function is not meant to be called by the user directly.
        '''

        # Create all subdirectories for the file as needed
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        with open(self.config_path, 'w') as f:
            json.dump(auth, f)

    def purge_credentials(self, ask=True):
        '''
        Enables user to delete the file containing cached credentials.

        Parameters
        ----------
        ask : bool (default True)
            Whether to ask for confirmation
        '''

        if ask:
            purge_creds = input(
                'Are you sure you want to delete your saved credentials? This cannot be undone. (y/n): ').lower() == 'y'
        else:
            purge_creds = True

        if purge_creds:
            if os.path.exists(self.config_path):
                os.remove(self.config_path)
            else:
                print('No credentials file found.')

    '''
    ###########################################################################
    ########################## User Operations ################################
    ###########################################################################
    '''

    def create_user(
        self,
        username: str,
        role: str,
        password: str | None = None,
        api_key: str | None = None,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Create a user within the platform.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.create_user('username')

        Parameters
        ----------
        username: str
            The username of the user
        role: str
            The role of the user
        password: str
            The password for the user. If not provided, will be generated
        api_key: str or None (default None)
            The API key for the user. If not provided, will be generated
        url: str or None (default None)
            The URL for the platform. If not provided, will use client parameters
        creds: dict or None (default None)
            The credentials to use to authenticate with the platform. If not provided, will use client parameters
        verbose: bool (default False)
            Whether to print intermediate results
        '''

        # Get parameters as necessary from the client
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Create user
        resp = _create_user(url, creds, username, role,
                            api_key, password, ssl_verify=self.ssl_verify)

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(f'user {username} is now on the platform! Go say hi!')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the response
        return resp.json()

    def delete_user(
        self,
        username: str,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Delete a user of the platform.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.delete_user('username')

        Parameters
        ----------
        username: str
            The username of the user to delete
        url: str or None (default None)
            The URL for the platform. If not provided, will use client parameters
        creds: dict or None (default None)
            The credentials to use to authenticate with the platform. If not provided, will use client parameters
        verbose: bool (default False)
            Whether to print intermediate results

        '''

        # Populate parameters from client as necessary
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the delete user function
        resp = _delete_user(url, creds, username, ssl_verify=self.ssl_verify)

        # Print as needed for verbosity requested
        if verbose:
            if resp.status_code == 200:
                print(
                    f'user {username} is now off the platform! Good riddance!')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the response
        return resp.json()

    def verify_password(
        self,
        password: str,
        url: str = None,
        creds: dict = None,
        username: str = None,
        verbose: bool = False
    ):
        '''
        Verify a user's password.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.verify_password('my_password')

        Parameters
        ----------
        password: str
            The password to verify
        url: str or None (default None)
            The URL for the platform. If not provided, will use client parameters
        creds: dict or None (default None)
            The credentials to use to authenticate with the platform. If not provided, will use client parameters
        username: str or None (default None)
            The username to test the password for
        verbose: bool (default False)
            Whether to print intermediate results
        '''

        # Use parameters from the client as necessary
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds
        if username is None:
            username = self.username

        # Run the verify password function
        resp = _verify_password(url, creds, username,
                                password, ssl_verify=self.ssl_verify)

        # Print results if verbosity requested
        if verbose:
            if resp.status_code == 200:
                print(
                    f'Your password "{password}" is verified. Congratulations!')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return True if correct
        return True

    def issue_new_password(
        self,
        new_password: str,
        username: str = None,
        overwrite_password: bool = True,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Create a new a password for an existing user.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.issue_new_password('new_password')

        Parameters
        ----------
        new_password: str
            New password for user authentication.
            It must have:
            - At least 8 characters
            - At least 1 uppercase character
            - At least 1 lowercase character
        username: str or None (default None)
            The user's display name and login credential
        overwrite_password: bool (default True)
            Whether or not to overwrite the password in the config file.
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters as necessary from client
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds
        if username is None:
            username = self.username

        # Run the issue new password function
        resp = _issue_new_password(
            url, creds, username, new_password=new_password, ssl_verify=self.ssl_verify)

        # Set new password for client
        if resp.ok:
            self.password = new_password
        else:
            return MLILException(str(resp.json()))

        # If overwrite, save the password
        if overwrite_password:
            auth = {'username': self.username, 'key': self.api_key,
                    'url': url, 'password': new_password}
            print(f'Your password has been overwritten.')
            self._save_credentials(auth)

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(
                    f'Your new password "{new_password}" is created. Try not to lose this one!')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the response
        return resp.json()

    def get_user_role(
        self,
        username: str,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Check a user's role.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.get_user_role('username')

        Parameters
        ----------
        username: str
            The username of the user to get a role for
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters from the client as necessary
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the get_user_role function
        resp = _get_user_role(url, creds, username=username,
                              ssl_verify=self.ssl_verify)

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(
                    f'User {username} works here, and they sound pretty important.')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the response
        return resp.json()

    def update_user_role(
        self,
        username: str,
        new_role: str,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Update a user's role.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.update_user_role('username', 'new_role')

        Parameters
        ----------
        username: str
            The user's display name and login credential
        new_role: str
            New role to attribute to the specified user
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters from the client as necessary
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the update_user_role function
        resp = _update_user_role(
            url, creds, username=username, new_role=new_role, ssl_verify=self.ssl_verify)

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(f'User {username} now has the role {new_role}.')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the response
        return resp.json()

    def list_users(
        self,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Update a user's role.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.create_user()

        Parameters
        ----------
        url: str
            String containing the URL of your deployment of the platform.
        creds: dict
            Dictionary that must contain keys 'username' and 'key', and associated values.
        '''
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        resp = _list_users(url, creds, ssl_verify=self.ssl_verify)

        if verbose:
            if resp.status_code == 200:
                print(f'Gaze upon your co-workers in wonder!')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        return resp.json()

    '''
    ###########################################################################
    ########################## Key Operations ################################
    ###########################################################################
    '''

    def issue_api_key(
        self,
        username: str = None,
        password: str = None,
        url: str = None,
        overwrite_api_key: bool = True,
        verbose: bool = False
    ):
        '''
        Create a new API key for a user.

        Parameters
        ----------

        username: str or None (default None)
            The display name of the user for whom you're creating a key.
        password: str or None (default None)
            Password for user verification.
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        overwrite_api_key: bool (default True)
            Overwrites the API key stored in the credentials cached in config.js
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters from client as necessary
        if url is None:
            url = self.url
        if username is None:
            username = self.username
        if password is None:
            password = self.password

        # Run the create_api_key function
        resp = _create_api_key(url, for_username=username,
                               username=self.username, password=self.password, ssl_verify=self.ssl_verify)

        # Assign the API key to client
        self.api_key = resp.json()

        # Overwrite the saved credentials if requested and the API key being changed is the user's
        if overwrite_api_key and username == self.username:
            auth = {'username': username, 'key': self.api_key,
                    'url': url, 'password': password}
            self._save_credentials(auth)

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(f'New key granted. Please only use this power for good.')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the API key
        return resp.json()

    '''
    ###########################################################################
    ########################## Model Operations ###############################
    ###########################################################################
    '''

    def deploy_model(
        self,
        model_name: str,
        model_flavor: str,
        model_version_or_alias: str,
        requirements: str = None,
        quantization_kwargs: dict = None,
        url: str = None,
        creds: dict = None,
        verbose: bool = False,
        **kwargs
    ):
        '''
        Deploys a model with the platform.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.deploy_model('test_model', 'test_model_flavor', 'test_model_version_or_alias')

        Parameters
        ----------
        model_name: str
            The name of the model to load
        model_flavor: str
            The flavor of the model. It can be one of:
                1. 'pyfunc'
                2. 'sklearn'
                3. 'transformers'
                4. 'hfhub'
        model_version_or_alias: str
            The version of the model that you wish to load (from MLFlow).
        requirements: str or None (default None)
            Any pip requirements for loading the model.
        quantization_kwargs : dict or None (default None)
            Quantization keyword arguments. NOTE: Only applies for hfhub models
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        **kwargs : additional keyword arguments
            Additional keyword arguments. NOTE: Only applies to hfhub models
        '''

        # Get parameters from client as necessary
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Format the request
        load_request = {}
        if requirements:
            load_request['requirements'] = requirements
        if quantization_kwargs:
            load_request['quantization_kwargs'] = quantization_kwargs
        if kwargs:
            load_request['kwargs'] = kwargs

        # Run the load_model function
        resp = _deploy_model(url,
                             creds,
                             model_name=model_name,
                             model_flavor=model_flavor,
                             model_version_or_alias=model_version_or_alias,
                             load_request=load_request,
                             ssl_verify=self.ssl_verify
                             )

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(
                    f'{model_name} is loading. This may take a few minutes, so go grab a doughnut. Mmmmmmm…doughnuts…')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the response JSON
        return resp.json()

    def list_models(
        self,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Lists all *loaded* models. To view unloaded models, check the MLFlow UI.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.list_models()

        Parameters
        ----------
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters from the client as necessary
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the list_models function
        resp = _list_models(url=url, creds=creds, ssl_verify=self.ssl_verify)

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(f'These are your models, Simba, as far as the eye can see.')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the response
        return resp.json()

    def undeploy_model(
        self,
        model_name: str,
        model_flavor: str,
        model_version_or_alias: str,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Removes a deployed model.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.undeploy_model('test_model', 'test_model_flavor', 'test_model_version')

        Parameters
        ----------
        model_name: str
            The name of the model to unload.
        model_flavor: str
            The flavor of the model. It can be one of:
                1. 'pyfunc'
                2. 'sklearn'
                3. 'transformers'
                4. 'hfhub'
        model_version_or_alias: str
            The version of the model that you wish to unload (from MLFlow).
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters from the client as necessary
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the unload_model function
        resp = _undeploy_model(
            url,
            creds,
            model_name=model_name,
            model_flavor=model_flavor,
            model_version_or_alias=model_version_or_alias,
            ssl_verify=self.ssl_verify
        )

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(f'{model_name} has been unloaded from memory.')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the response
        return resp.json()

    def predict(
        self,
        model_name: str,
        model_flavor: str,
        model_version_or_alias: str,
        inputs: Union[str, List[str]],
        predict_function: str = 'predict',
        dtype: str = None,
        params: Optional[dict] = None,
        convert_to_numpy: bool = True,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Calls the 'predict' function of the specified MLFlow model.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.predict()

        Parameters
        ----------
        model_name: str
            The name of the model to be invoked.
        model_flavor: str
            The flavor of the model, which can be one of:
                1. 'pyfunc'
                2. 'sklearn'
                3. 'transformers'
                4. 'hfhub'
        model_version_or_alias: str
            The version of the model that you wish to invoke.
        inputs: Union[str, list, dict]
            The input input data for prediction.
        predict_function: str (default 'predict')
            The name of the prediction function to call.
        dtype: str or None (default None)
            The data type of the input.
        params: dict or None (default None)
            Additional parameters for the prediction.
        convert_to_numpy: bool (default True)
            Whether to convert the data to a NumPy array server-side.
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters from the client as necessary
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the predict function
        resp = _predict(
            url=url,
            creds=creds,
            model_name=model_name,
            model_flavor=model_flavor,
            model_version_or_alias=model_version_or_alias,
            inputs=inputs,
            predict_function=predict_function,
            dtype=dtype,
            params=params,
            convert_to_numpy=convert_to_numpy,
            ssl_verify=self.ssl_verify
        )

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(f'Sometimes I think I think')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the response
        return resp.json()

    def get_model_logs(
        self,
        model_name: str,
        model_flavor: str,
        model_version_or_alias: str,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Get logs for a model.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.get_model_logs('test_model', 'test_model_flavor', 'test_model_version')

        Parameters
        ----------
        model_name: str
            The name of the model to unload.
        model_flavor: str
            The flavor of the model. It can be one of:
                1. 'pyfunc'
                2. 'sklearn'
                3. 'transformers'
                4. 'hfhub'
        model_version_or_alias: str
            The version of the model that you wish to unload (from MLFlow).
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters from the client as necessary
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the function
        resp = _get_model_logs(
            url,
            creds,
            model_name=model_name,
            model_flavor=model_flavor,
            model_version_or_alias=model_version_or_alias,
            ssl_verify=self.ssl_verify
        )

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(f'Logs retrieved!')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}'
                )

        # Return the response
        return resp.json()

    '''
    ###########################################################################
    ########################## Admin Operations ################################
    ###########################################################################
    '''

    def reset_deployment_server(
        self,
        failsafe: bool = True,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Resets the MLIL deployment server. Unloads all models and restarts the server, at which point the models will be loaded again.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.reset_deployment_server()

        Parameters
        ----------
        failsafe: bool (default True)
            This is a safety catch that prompts the user to confirm before they reset the platform.
            Should only be set to False if you are scripting and/or know what you are doing.
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters from client as needed
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Check based on failsafe
        if not failsafe:
            really_reset = True
        else:
            really_reset = input(
                'Are you sure you want to restart the deployment server? This cannot be undone. (y/n): ').lower() == 'y'

        # Run the reset
        if really_reset:
            resp = _reset_platform(url=url, creds=creds,
                                   ssl_verify=self.ssl_verify)

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(
                    f'You have become death, destroyer of, well, your platform deployment server...')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the response
        return resp.json()

    def restart_jupyter(
        self,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Restarts the Jupyter service within the platform

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.restart_jupyter()

        Parameters
        ----------
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters as needed
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the restart function
        resp = _restart_jupyter(url=url, creds=creds,
                                ssl_verify=self.ssl_verify)

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(
                    'Jupyter is no longer a planet'
                )
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}'
                )

        # Return the response
        return resp.json()

    def get_resource_usage(
        self,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Get system resource usage, in terms of free CPU and GPU memory (if GPU-enabled).
        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.get_resource_usage()

        Parameters
        ----------
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters as needed
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the function
        resp = _get_platform_resource_usage(
            url=url, creds=creds, ssl_verify=self.ssl_verify)

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(
                    f'Vroom vroom!')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the response
        return resp.json()

    '''
    ###########################################################################
    ########################## Data Operations ################################
    ###########################################################################
    '''

    def get_variable(
        self,
        variable_name: str,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Fetches a variable from the MLIL data store.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.get_variable('test_variable')

        Parameters
        ----------
        variable_name: str
            The name of the variable you wish to access.
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters as needed
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the get_variable function
        resp = _get_variable(
            url,
            creds,
            variable_name=variable_name,
            ssl_verify=self.ssl_verify
        )

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(f'{variable_name} has been fetched.')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return response
        return resp.json()

    def list_variables(
        self,
        url: str = None,
        creds: dict = None,
        verbose: bool = False
    ):
        '''
        Lists all available variables in the MLIL variable store

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.list_variables()

        Parameters
        ----------
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters as needed
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the list_variables function
        resp = _list_variables(
            url,
            creds,
            ssl_verify=self.ssl_verify
        )

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(f'Varying degrees of inter-variable variablility.')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return response
        return resp.json()

    def set_variable(
        self,
        variable_name: str,
        value: Any,
        overwrite: bool = False,
        verbose: bool = False,
        url: str = None,
        creds: dict = None
    ):
        '''
        Creates a new variable in the MLIL variable store.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.set_variable('test_variable', 'test_value')

        Parameters
        ----------
        variable_name: str
            The name to give your variable in the MLIL datastore.
        value: Any
            Your variable. Can be of type string, integer, number, boolean, object, or array<any>.
        overwrite: bool = False
            Whether or not to delete any variables called <variable_name> that
            currently exist in MLIL. Defaults to False.
        '''

        # Get parameters as needed
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the set_variable function
        resp = _set_variable(
            url,
            creds,
            variable_name=variable_name,
            value=value,
            overwrite=overwrite,
            ssl_verify=self.ssl_verify
        )

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(f'{variable_name} has been uploaded to MLIL.')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return the response
        return resp.json()

    def delete_variable(
        self,
        variable_name: str,
        verbose: bool = False,
        url: str = None,
        creds: dict = None
    ):
        '''
        Creates a new variable in the MLIL variable store.

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.delete_variable('test_variable')

        Parameters
        ----------
        variable_name: str
            The name to give your variable in the MLIL datastore.
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters as necessary
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the delete_variable function
        resp = _delete_variable(
            url,
            creds,
            variable_name=variable_name,
            ssl_verify=self.ssl_verify
        )

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print(f'{variable_name} has been removed from MLIL.')
            else:
                print(
                    f'Something went wrong, request returned a status code {resp.status_code}')

        # Return response
        return resp.json()

    def get_predictions(
            self,
            model_name: str,
            model_flavor: str,
            model_version_or_alias: str | int,
            url: str = None,
            creds: dict = None,
            verbose: bool = False
    ):
        '''
        Gets predictions from a deployed model

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.get_predictions('test_model', 'test_model_flavor', 'test_model_version')

        Parameters
        ----------
        model_name: str
            The name of the model to get predictions from
        model_flavor: str
            The flavor of the model to get predictions from
        model_version_or_alias: str | int
            The version or alias of the model to get predictions from
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters as needed
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the get_predictions function
        resp = _get_predictions(
            url,
            creds,
            model_name,
            model_flavor,
            model_version_or_alias,
            ssl_verify=self.ssl_verify
        )

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print('Predictions have been retrieved')
            else:
                print(
                    f'Something went wrong, request returned a status code of {resp.status_code}')

        # Return the response
        return resp.json()

    def list_prediction_models(
            self,
            verbose: bool = False,
            url: str = None,
            creds: dict = None
    ):
        '''
        Lists models for which predictions are stored

        >>> from mlinsightlab import MLILClient
        >>> client = MLILClient()
        >>> client.list_prediction_models()

        Parameters
        ----------
        url: str or None (default None)
            String containing the URL of your deployment of the platform.
        creds: dict or None (default None)
            Dictionary that must contain keys 'username' and 'key', and associated values.
        verbose: bool (default False)
            Whether to log verbosely
        '''

        # Get parameters as needed
        if url is None:
            url = self.url
        if creds is None:
            creds = self.creds

        # Run the list_prediction_models function
        resp = _list_prediction_models(
            url,
            creds,
            ssl_verify=self.ssl_verify
        )

        # Log if verbose
        if verbose:
            if resp.status_code == 200:
                print('Models have been retrieved')
            else:
                print(
                    f'Something went wrong, request returned a status code of {resp.status_code}'
                )

        # Return response
        return resp.json()
