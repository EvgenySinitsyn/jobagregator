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
    string_for_hash = json.dumps(sorted_params).replace(' ', '') + secret
    hash_str = hashlib.sha256(string_for_hash.encode('utf-8')).hexdigest()
    print(hash_str)
    return hash_str

# Пример использования:
params = {
    'app_id': '723',
    'time': str(int(datetime.now().timestamp())),
    'code': '5DDo4tQcbpzebNh0uYM2FAgHrpwWS76i',
}
secret = 'XJeCajJckqBiDBA0KdpCE7sCc72l0TBR'
signature = get_signature(params, secret)

params['signature'] = signature
headers = {
    'content-type': 'application/x-www-form-urlencoded'
}
response = requests.post(
    url='https://api.rabota.ru/oauth/token.html',
    params=params,
    headers=headers,
)
print(response.status_code)

