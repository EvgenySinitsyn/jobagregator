import os
import sys
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv('.env'))


try:
    CONFIG = {
        'superjob_api_auth_key': os.environ.get('SUPERJOB_API_AUTH_KEY'),
        'superjob_api_url': os.environ.get('SUPERJOB_API_URL'),

        'hh_client_id': os.environ.get('HH_CLIENT_ID'),
        'hh_client_secret': os.environ.get('HH_CLIENT_SECRET'),
        'hh_app_token': os.environ.get('HH_APP_TOKEN'),
        'hh_user_authorization_code': os.environ.get('HH_USER_AUTHORIZATION_CODE'),
        'hh_api_url': os.environ.get('HH_API_URL'),
    }
except KeyError as error:
    print('KeyError: {}'.format(error))
    sys.exit(-1)
