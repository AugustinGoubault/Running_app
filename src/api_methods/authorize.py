import requests

from src.api_methods import endpoints
from src.env_handler import env_variables


def get_authorization_url():
    '''return URL string to access strava authorization page'''
    return (
        f"{endpoints.auth_endpoint}"
        f"?client_id={env_variables['CLIENT_ID']}"
        f"&response_type=code"
        f"&redirect_uri={endpoints.local_endpoint}"
        f"&approval_prompt=force"
        f"&scope=read,activity:read_all"
    )

def get_acces_token(code:str):
    # these params needs to be passed to get access
    # token used for retrieveing actual data
    payload = {
    'client_id': env_variables['CLIENT_ID'],
    'client_secret': env_variables['CLIENT_SECRET'],
    'refresh_token': env_variables['REFRESH_TOKEN'],
    'code': code,
    'grant_type': "authorization_code",
    'f': 'json'
    }
    res = requests.post(endpoints.token_endpoint, data=payload, verify=True)
    access_token = res.json()['access_token']
    return access_token