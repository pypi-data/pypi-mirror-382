# Manage users and credentials
from .MLILException import MLILException
from .endpoints import CREATE_USER_ENDPOINT, DELETE_USER_ENDPOINT, VERIFY_PASSWORD_ENDPOINT, NEW_PASSWORD_ENDPOINT, GET_USER_ROLE_ENDPOINT, UPDATE_USER_ROLE_ENDPOINT, LIST_USERS_ENDPOINT
import requests


def _create_user(
    url: str,
    creds: dict,
    username: str,
    role: str,
    api_key: str | None,
    password: str | None,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Create a user within the platform.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    cred:
        Dictionary that must contain keys 'username' and 'key', and associated values.
    username: str
        The user's display name and login credential
    role: str
        The role to be given to the user
    api_key: str or NULL
        An API key for the new user
    password: str or NULL
        Password for user login
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'{url}/{CREATE_USER_ENDPOINT}'

    # Format the JSON payload
    json_data = {
        'username': username,
        'role': role
    }

    # Format additional parameters for API key and password, if provided
    if api_key:
        json_data['api_key'] = api_key
    if password:
        json_data['password'] = password

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


def _delete_user(
    url: str,
    creds: dict,
    username: str,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Delete a user within the platform.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds:
        Dictionary that must contain keys 'username' and 'key', and associated values.
    username: str
        The user's display name and login credential
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    json_data = {
        'username': username
    }

    url = f'{url}/{DELETE_USER_ENDPOINT}/{username}'

    with requests.Session() as sess:
        resp = sess.delete(
            url,
            auth=(creds['username'], creds['key']),
            json=json_data,
            verify=ssl_verify
        )

    # If the request is not successful, raise exception, else return response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _verify_password(
    url: str,
    creds: dict,
    username: str,
    password: str,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Verify a user's password.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds:
        Dictionary that must contain keys 'username' and 'key', and associated values.
    username: str
        The user's display name and login credential
    password: str
        Password for user login
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    json_data = {
        'username': username,
        'password': password
    }

    url = f'{url}/{VERIFY_PASSWORD_ENDPOINT}'

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


def _issue_new_password(
    url: str,
    creds: dict,
    username: str,
    new_password: str,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Create a new a password for an existing user.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds:
        Dictionary that must contain keys 'username' and 'key', and associated values.
    username: str
        The user's display name and login credential
    new_password: str
        New password for user authentication
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'{url}/{NEW_PASSWORD_ENDPOINT}/{username}'

    # Format the JSON payload
    json_data = {
        'username': username,
        'new_password': new_password
    }

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.put(
            url,
            auth=(creds['username'], creds['key']),
            json=json_data,
            verify=ssl_verify
        )

    # If the request is not successful, raise exception, else return response
    if not resp.ok:
        raise MLILException(resp.json())
    return resp


def _get_user_role(
    url: str,
    creds: dict,
    username: str,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Check a user's role.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds:
        Dictionary that must contain keys 'username' and 'key', and associated values.
    username: str
        The user's display name and login credential.
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'{url}/{GET_USER_ROLE_ENDPOINT}/{username}'

    # Format the JSON payload
    json_data = {
        'username': username
    }

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.get(
            url,
            auth=(creds['username'], creds['key']),
            json=json_data,
            verify=ssl_verify
        )

    # If the request is not successful, raise exception, else return response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _update_user_role(
    url: str,
    creds: dict,
    username: str,
    new_role: str,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Update a user's role.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds:
        Dictionary that must contain keys 'username' and 'key', and associated values.
    username: str
        The user's display name and login credential
    new_role: str
        New role to attribute to the specified user
    ssl_verify: bool (default True)
        Whether to verify SSL certificates in the request
    '''

    # Format the URL
    url = f'{url}/{UPDATE_USER_ROLE_ENDPOINT}/{username}'

    # Format the JSON payload
    json_data = {
        'username': username,
        'new_role': new_role
    }

    # Make the request to the platform
    with requests.Session() as sess:
        resp = sess.put(
            url,
            auth=(creds['username'], creds['key']),
            json=json_data,
            verify=ssl_verify
        )

    # If the request is not successful, raise exception, else return response
    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _list_users(
    url: str,
    creds: dict,
    ssl_verify: bool = True
):
    '''
    NOT MEANT TO BE CALLED BY THE END USER

    Update a user's role.
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
    url = f'{url}/{LIST_USERS_ENDPOINT}'

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
