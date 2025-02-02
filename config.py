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

        'mysql_base': os.environ.get('MYSQL_DATABASE'),
        'mysql_user': os.environ.get('MYSQL_ROOT_USER'),
        'mysql_password': os.environ.get('MYSQL_PASSWORD'),
        'mysql_charset': os.environ.get('MYSQL_CHARSET'),
        'log_filename': os.environ.get('LOG_FILENAME'),
        'mysql_name_host': os.environ.get('MYSQL_NAME_HOST'),
        'mysql_port': int(os.environ.get('MYSQL_PORT')),
        'mailru_password': os.environ.get('MAILRU_PASS'),
        'email': os.environ.get('MAILRU_ADDR'),
        'yandexmail': os.environ.get('YANDEXMAIL'),
        'yandexmail_pass': os.environ.get('YANDEXMAIL_PASS'),
        'secret_key': os.environ.get('SECRET_KEY'),
        'temp_phones': os.environ.get('TEMP_PHONES').split(',')
    }
except KeyError as error:
    print('KeyError: {}'.format(error))
    sys.exit(-1)
