import json
import hashlib
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
    return hashlib.sha256((json.dumps(sorted_params) + secret).encode('utf-8')).hexdigest()

# Пример использования:
params = {
    'app_id': '723',
    'time': int(datetime.now().timestamp()),
    'code': '32SiX2NT6eJcc04wZKGFzg3bmlbphCwI',
}
secret = 'XJeCajJckqBiDBA0KdpCE7sCc72l0TBR'
signature = get_signature(params, secret)

params['signature'] = signature
headers = {
    'content-type': 'application/x-www-form-urlencoded'
}
response = requests.post(
    url='https://api.rabota.ru/oauth/token.json',
    params=params,
    headers=headers,
)
for i in response.__dict__.items():
    print(i)
for i in params.items():
    print(i)

