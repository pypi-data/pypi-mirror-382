# Perform platform admin tasks
from .MLILException import MLILException
from .endpoints import RESET_ENDPOINT, RESTART_JUPYTER_ENDPOINT, RESOURCE_USAGE
import requests


def _reset_platform(
    url: str,
    creds: dict,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Resets the MLIL platform

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
    url = f'{url}/{RESET_ENDPOINT}'

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


def _restart_jupyter(
        url: str,
        creds: dict,
        ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Restarts the Jupyter service

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
    url = f'{url}/{RESTART_JUPYTER_ENDPOINT}'

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


def _get_platform_resource_usage(
    url: str,
    creds: dict,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Returns the resource utilization of MLIL.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds:
        Dictionary that must contain keys 'username' and 'key', and associated values.
    '''

    # Format the URL
    url = f'{url}/{RESOURCE_USAGE}'

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
