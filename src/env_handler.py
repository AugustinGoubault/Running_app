import os
from environs import Env


def _load_env_variables() -> dict:
    # Load environment variables from .env file
    env = Env()
    env.read_env()

    # Get environment variables from .env file
    CLIENT_ID = os.environ.get('CLIENT_ID')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
    REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')

    env_variables = {
        'CLIENT_ID': CLIENT_ID,
        'CLIENT_SECRET': CLIENT_SECRET,
        'REFRESH_TOKEN': REFRESH_TOKEN
    }

    return env_variables

env_variables = _load_env_variables()