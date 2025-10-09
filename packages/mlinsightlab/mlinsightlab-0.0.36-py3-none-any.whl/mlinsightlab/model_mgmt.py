# Helper functions to manage and interat with models in the platform
from .MLILException import MLILException
from typing import Union, List, Optional
from .endpoints import DEPLOY_MODEL_ENDPOINT, LIST_MODELS_ENDPOINT, UNDEPLOY_MODEL_ENDPOINT, PREDICT_ENDPOINT, GET_MODEL_LOGS
import pandas as pd
import requests


def _deploy_model(
    url: str,
    creds: dict,
    model_name: str,
    model_flavor: str,
    model_version_or_alias: str,
    load_request: dict,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Deploys a model.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys 'username' and 'key', and associated values.
    model_name: str
        The name of the model to load
    model_flavor: str
        The flavor of the model, e.g. 'transformers', 'pyfunc', etc.
    model_version_or_alias: str
        The version of the model that you wish to load (from MLFlow).
    load_request : dict = None
        A dictionary containing additional parameters for loading the model,
        including 'requirements', 'quantization_kwargs', and 'kwargs'.
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    if load_request is None:
        load_request = {
            'model_name': model_name,
            'model_flavor': model_flavor,
            'model_version_or_alias': model_version_or_alias
        }
    else:
        load_request['model_name'] = model_name
        load_request['model_flavor'] = model_flavor
        load_request['model_version_or_alias'] = model_version_or_alias

    # Format the URL
    url = f'''{
        url}/{DEPLOY_MODEL_ENDPOINT}'''

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.post(
            url,
            auth=(creds['username'], creds['key']),
            json=load_request,
            verify=ssl_verify
        )

    # If request is not successful, raise appropriate exception, else return response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _list_models(
    url: str,
    creds: dict,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Lists all *deployed* models. To view undeployed models, check the MLFlow UI.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds:
        Dictionary that must contain keys 'username' and 'key', and associated values.
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'{url}/{LIST_MODELS_ENDPOINT}'

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.get(
            url,
            auth=(creds['username'], creds['key']),
            verify=ssl_verify
        )

    # If the request is not successful, raise an appropriate exception, else return response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _undeploy_model(
    url: str,
    creds: dict,
    model_name: str,
    model_flavor: str,
    model_version_or_alias: str,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Unloads a model from the deployment service.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys 'username' and 'key', and associated values.
    model_name: str
        The name of the model to unload.
    model_flavor: str
        The flavor of the model, e.g. 'transformers', 'pyfunc', etc.
    model_version_or_alias: str
        The version of the model that you wish to unload (from MLFlow).
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'''{
        url}/{UNDEPLOY_MODEL_ENDPOINT}/{model_name}/{model_flavor}/{model_version_or_alias}'''

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.delete(
            url,
            auth=(creds['username'], creds['key']),
            verify=ssl_verify
        )

    # If the request is not successful, raise exception, else return response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _predict(
    url: str,
    creds: dict,
    model_name: str,
    model_flavor: str,
    model_version_or_alias: str,
    inputs: Union[list, int, float, str],
    convert_to_numpy: bool = True,
    predict_function: str = 'predict',
    dtype: str = None,
    params: Optional[dict] = None,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Calls the 'predict' function of the specified deployed model.

    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds:
        Dictionary that must contain keys 'username' and 'key', and associated values.
    model_name: str
        The name of the model to be invoked.
    model_flavor: str
        The flavor of the model, e.g. 'transformers', 'pyfunc', etc.
    model_version_or_alias: str
        The version of the model that you wish to invoke (from MLFlow).
    inputs: varied types
        The input data for prediction. Can be a single value or list of values
    convert_to_numpy: bool = True
        Whether or not to convert inputs to a NumPy array.
    predict_function: str, optional
        The name of the prediction function to call. Default is 'predict'.
    dtype: str, optional
        The data type of the input
    params: dict, optional
        Additional parameters for the prediction.
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # TODO: Remove this block once working
    # Format the data so that it is a list
    # if isinstance(inputs, str):
    # data = [inputs]

    # Format the JSON payload
    json_data = {
        'model_name': model_name,
        'model_flavor': model_flavor,
        'model_version_or_alias': model_version_or_alias,
        'inputs': inputs,
        'predict_function': predict_function,
        'params': params if params else {},
        'convert_to_numpy': convert_to_numpy
    }

    # Add dtype to the JSON payload, if provided
    if dtype:
        json_data.update({'dtype': dtype})

    # Format the URL
    url = f'''{url}/{PREDICT_ENDPOINT}'''

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.post(
            url,
            auth=(creds['username'], creds['key']),
            json=json_data,
            verify=ssl_verify
        )

    # If the request is not successful, raise exception, else return response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _get_model_logs(
    url: str,
    creds: dict,
    model_name: str,
    model_flavor: str,
    model_version_or_alias: str,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Gets model logs.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment to the platform.
    creds: dict
        Dictionary that must contain keys 'username' and 'key', and associated values.
    model_name: str
        The name of the model to unload.
    model_flavor: str
        The flavor of the model, e.g. 'transformers', 'pyfunc', etc.
    model_version_or_alias: str
        The version of the model that you wish to unload (from MLFlow).
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'''{
        url}/{GET_MODEL_LOGS}/{model_name}/{model_flavor}/{model_version_or_alias}'''

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.get(
            url,
            auth=(creds['username'], creds['key']),
            verify=ssl_verify
        )

    # If the request is not successful, raise exception, else return response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp
