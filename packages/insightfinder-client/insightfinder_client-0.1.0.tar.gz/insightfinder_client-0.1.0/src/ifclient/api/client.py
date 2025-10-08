from typing import Dict
import requests
import os
import json
import time
from ifclient.utils.logger import setup_logger

logger = setup_logger(__name__)

def apply_config(project: Dict, baseUrl: str):

    assert(all(x in project for x in ['name', 'userName', 'data']))

    session = requests.session()

    token = login(baseUrl, project['userName'], session)

    update_project_config(baseUrl, project['userName'], token, project, session)


def update_project_config(baseUrl: str, username: str, token: str, project: str, session: requests.Session) -> None:

    try:
        
        update_url = f"{baseUrl}api/v1/watch-tower-setting"

        params = {
            "projectName": project['name'],
            "customerName": username
        }

        logger.info(f"Sending data for project {project['name']}: {json.dumps(project['data'], indent=4)}")
        update_response = session.post(update_url, params=params, headers={"Content-Type": "application/json", "X-CSRF-TOKEN": token}, json=project['data']) 
        
        time.sleep(1)

        update_response.raise_for_status()

        
    except Exception as e:
        raise Exception(f"Unable to apply project config: {e}")

        

def login(baseUrl: str, username: Dict, session: requests.Session):


    try:

        login_url = f"{baseUrl}api/v1/login-check"

        user_password_env_var_name = username + '_PASSWORD'

        user_password = os.getenv(user_password_env_var_name, None)

        if not user_password:
            raise Exception("User password is not available in environment variables. Env variable name should be in the format username_PASSWORD")

        params = {
            'userName': username,
            'password': user_password
        }

        login_response = session.post(login_url, params=params, headers={"Content-Type": "application/json"})

        login_response.raise_for_status()

        return login_response.json()['token']

    except Exception as e:
        raise Exception(f"Unable to login: {e}")
