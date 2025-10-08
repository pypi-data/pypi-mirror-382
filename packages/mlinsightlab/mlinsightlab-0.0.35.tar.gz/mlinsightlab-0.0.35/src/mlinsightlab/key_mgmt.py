# Manage authentication keys

from .MLILException import MLILException
from .endpoints import NEW_API_KEY_ENDPOINT
import requests


def _create_api_key(
    url: str,
    for_username: str,
    username: str,
    password: str,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Create a new API key for a user.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    for_username: str
        The user's display name to issue a new API key for
    username: str
        The user's display name to use for authentication
    password: str
        Password for verification
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'{url}/{NEW_API_KEY_ENDPOINT}/{for_username}'

    # Format the JSON payload
    json_data = {
        'username': for_username
    }

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.put(
            url,
            auth=(username, password),
            json=json_data,
            verify=ssl_verify
        )

    # If not successful, raise exception, else return response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp
