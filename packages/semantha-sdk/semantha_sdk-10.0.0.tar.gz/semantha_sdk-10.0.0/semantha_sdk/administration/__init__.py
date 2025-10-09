import json
import logging
from jproperties import Properties

from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from semantha_sdk.administration.administration_api import AdministrationAPI


def login(server_url: str = None, key: str = None, key_file: str = None, client_id: str = None, client_secret: str = None, token_url: str = None) -> AdministrationAPI:
    """ Access to the Administration API.

        author semantha, this is a generated class do not change manually!

    Args:
        server_url (str): URL to the Administration server
        key (str): A valid bearer token for accessing the given url.
        key_file (str): Path to a json file providing a valid `API_Key` value for the given url or a properties file providing client credentials.
        client_id (str): OAuth2 client id.
        client_secret (str): OAuth2 client secret.
        token_url (str): OAuth2 url to get a valid access token.

    Returns:
        AdministrationAPI: Entry point to the Administration API.
    """
    if key:
        pass
    elif key_file:
        if key_file.endswith((".json", ".JSON", ".Json")):
            with open(key_file, "r") as key_file:
                p = json.load(key_file)
                key = p['API_Key']
                if 'server_url' in p:
                    server_url = p['server_url']
        elif key_file.endswith((".properties", ".PROPERTIES")):
            p = Properties()
            with open(key_file, "rb") as f:
                p.load(f)
            client_id = p['clientId'][0]
            client_secret = p['clientSecret'][0]
            token_url = p['tokenUrl'][0]
            if 'serverUrl' in p:
                server_url = p['serverUrl'][0]
        else:
            raise ValueError(f"Unsupported key file: {key_file} only .json or .properties is supported")
    elif client_id and client_secret and token_url:
        pass
    else:
        raise ValueError("You need to supply an API key to login, either directly or via a file.")

    if server_url.endswith("/"):
        server_url = server_url[:-1]
    if server_url.endswith("/tt-platform-ui/en/#"):
        server_url = server_url.replace("/tt-platform-ui/en/#", "/tt-product-server")
    elif not server_url.endswith("/tt-product-server"):
        server_url += "/tt-product-server"
    
    __api = AdministrationAPI(RestClient(server_url, key, client_id, client_secret, token_url), "/api")

    if hasattr(__api, "info"):
        # check whether API key is valid or not
        info = __api.info.get()
        logger = logging.getLogger()
        logger.info(f"Semantha API version: {info.version}")
    return __api
