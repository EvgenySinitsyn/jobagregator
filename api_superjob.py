import requests
from config import CONFIG
from pprint import pprint

api_key = CONFIG.get('superjob_api_auth_key')
api_url = CONFIG.get('superjob_api_url')

headers = {
    'X-Api-App-Id': api_key,
}

url = api_url + '/resumes'

response = requests.get(
    url=url,
    headers=headers,
).json()

# pprint(response)
pprint(response.get('objects')[0]['age'])

# for i in response.get('objects'):
#     print(i['simple_contacts_open'])

resp_keys = ['objects', 'total', 'more', 'id_search_session']

keys = ['id', 'last_profession', 'payment', 'currency', 'birthday', 'birthmonth', 'birthyear', 'hide_birthday', 'age',
        'metro', 'address', 'citizenship', 'published', 'draft', 'photo', 'photo_sizes', 'moveable', 'agreement',
        'receive_sms', 'moveable_towns', 'type_of_work', 'place_of_work', 'education', 'children', 'business_trip',
        'maritalstatus', 'languages', 'driving_licence', 'catalogues', 'town', 'region', 'experience_text',
        'experience_month_count', 'work_history', 'base_education_history', 'education_history', 'contacts_bought',
        'link', 'short_link', 'gender', 'achievements', 'additional_info', 'date_published', 'date_last_modified',
        'profession', 'is_archive', 'timeToUpdate', 'id_user', 'portfolio', 'simple_contacts_open']
