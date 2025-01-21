import json
import hashlib
import pprint

import requests
from datetime import datetime


def get_signature(params, secret):
    # Приводим все значения к типу строка (str)
    params = {k: str(v) for k, v in params.items()}

    # Функция сортировки по ключам
    def sort_dict(d):
        if not isinstance(d, dict):
            return d
        sorted_dict = {k: sort_dict(v) for k, v in sorted(d.items())}
        return sorted_dict

    # Возвращаем требуемый хэш
    sorted_params = sort_dict(params)
    string_for_hash = json.dumps(sorted_params).replace(' ', '') + secret
    hash_str = hashlib.sha256(string_for_hash.encode('utf-8')).hexdigest()
    return hash_str

# Пример использования:

def get_token():
    now = str(int(datetime.now().timestamp()))
    params = {
        'app_id': '723',
        'time': now,
        'code': '2ZtnrssXnJi5RTN5jsSR656MODo6t6te',
    }
    secret = 'XJeCajJckqBiDBA0KdpCE7sCc72l0TBR'
    signature = get_signature(params, secret)

    params['signature'] = signature
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(
        url='https://api.rabota.ru/oauth/token.json',
        data=params,
        headers=headers,
    )
    print(response.status_code)
    if response.status_code == 200:
        pprint.pprint(response.json())


def refresh_token():
    now = str(int(datetime.now().timestamp()))
    params = {
        'app_id': '723',
        'time': now,
        'token': 'YUs8dQ5wB3Jepii1k04fd73dw8qe0ssr',
    }
    secret = 'XJeCajJckqBiDBA0KdpCE7sCc72l0TBR'
    signature = get_signature(params, secret)

    params['signature'] = signature
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(
        url='https://api.rabota.ru/oauth/refresh-token.json',
        data=params,
        headers=headers,
    )
    print(response.status_code)
    if response.status_code == 200:
        pprint.pprint(response.json())

if __name__ == '__main__':
    refresh_token()


# {
#     "access_token": "YUs8dQ5wB3Jepii1k04fd73dw8qe0ssr",
#     "expires_in": 86400
# }