import requests

from src.api_methods import endpoints


def access_activity_data(access_token:str, params:dict=None) -> dict:
    headers = {'Authorization': f'Authorization: Bearer {access_token}'}
    if not params:
        response = requests.get(endpoints.activites_endpoint, headers=headers)
    response = requests.get(endpoints.activites_endpoint, headers=headers, params=params)
    response.raise_for_status()
    activity_data = response.json()
    return activity_data