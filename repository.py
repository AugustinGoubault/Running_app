import os
import requests


class StravaRepository:
    def __init__(self):
        self.client_id = os.environ['CLIENT_ID']
        self.client_secret = os.environ['CLIENT_SECRET']
        self.redirect_uri = 'http://localhost:8501/'
    
    def get_authorization_url(self)->str:
        '''return URL string to access strava authorization page'''
        return (
            f"https://www.strava.com/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={self.redirect_uri}"
            f"&approval_prompt=force"
            f"&scope=read,activity:read_all"
        )

    def query_authorization_code(self, query_parameters:dict)->str:
        '''return authorization code from query parameters'''
        return query_parameters.get("code", None)
    



    
    def get_activities(self, access_token:str)->dict:
        '''return activities data from strava api after connection is established'''
        activities_response = requests.get(
            'https://www.strava.com/api/v3/athlete/activities',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        return activities_response.json()

 