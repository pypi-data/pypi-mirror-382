# Helper functions to manage and interact with data

from .MLILException import MLILException
from .endpoints import GET_VARIABLE, LIST_VARIABLES, SET_VARIABLE, DELETE_VARIABLE, GET_PREDICTIONS, LIST_PREDICTIONS_MODELS
from typing import Any
import requests
import base64


def _get_variable(
    url: str,
    creds: dict,
    variable_name: str,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Retrieve a variable from the MLIL variable store.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys 'username' and 'key', and associated values.
    variable_name: str
        The name of the variable to access.
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'{url}/{GET_VARIABLE}/{variable_name}'

    # Make the request
    with requests.Session() as sess:
        resp = sess.get(
            url,
            auth=(creds['username'], creds['key']),
            verify=ssl_verify
        )

    # If the request was not successful, raise exception, else return the response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _list_variables(
    url: str,
    creds: dict,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Lists all variables associated with a user.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys 'username' and 'key', and associated values.
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'{url}/{LIST_VARIABLES}'

    # Make the request
    with requests.Session() as sess:
        resp = sess.get(
            url,
            auth=(creds['username'], creds['key']),
            verify=ssl_verify
        )

    # If the request was not successful, raise appropriate exception, else return the response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _set_variable(
    url: str,
    creds: dict,
    variable_name: str,
    value: Any,
    overwrite: bool = False,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Creates a variable within the MLIL variable store.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys 'username' and 'key', and associated values.
    variable_name: str
        The name of the variable to set.
    overwrite: bool = False
        Whether to overwrite any variables that currently exist in MLIL and have the same name.
    value: Any
        Your variable. Can be of type string | integer | number | boolean | object | array<any>.
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'{url}/{SET_VARIABLE}'

    # Format the JSON payload
    json_data = {
        'variable_name': variable_name,
        'value': value,
        'overwrite': overwrite
    }

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.post(
            url,
            auth=(creds['username'], creds['key']),
            json=json_data,
            verify=ssl_verify
        )

    # If the request is not successful, raise an appropriate respone, else return the response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _delete_variable(
    url: str,
    creds: dict,
    variable_name: str,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Removes a variable from the MLIL variable store.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys 'username' and 'key', and associated values.
    variable_name: str
        The name of the variable to delete.
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'{url}/{DELETE_VARIABLE}/{variable_name}'

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.delete(
            url,
            auth=(creds['username'], creds['key']),
            verify=ssl_verify
        )

    # Return the response or raise an exception as necessary
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _get_predictions(
        url: str,
        creds: dict,
        model_name: str,
        model_flavor: str,
        model_version_or_alias: str | int,
        ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Gets predictions that a model has made

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys 'username' and 'key', and associated values.
    model_name: str
        The name of the model to get predictions from
    model_flavor: str
        The flavor of the model to get predictions from
    model_version: str | int
        The version of the model to get predictions from
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'{url}/{GET_PREDICTIONS}/{model_name}/{model_flavor}/{model_version_or_alias}'

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.get(
            url,
            auth=(creds['username'], creds['key']),
            verify=ssl_verify
        )

    # Raise an exception or return the successful response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _list_prediction_models(
        url: str,
        creds: dict,
        ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Lists models that have stored predictions

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform
    creds: dict
        Dictionary that must contain keys 'username' and 'key', and associated values.
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'{url}/{LIST_PREDICTIONS_MODELS}'

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.get(
            url,
            auth=(creds['username'], creds['key']),
            verify=ssl_verify
        )

    # Raise an exception or return the successful response as necessary
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp
