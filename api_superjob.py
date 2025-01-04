import requests
from config import CONFIG
from datetime import datetime
from base import Platform, Profession, City, Resume

api_key = CONFIG.get('superjob_api_auth_key')
api_url = CONFIG.get('superjob_api_url')

headers = {
    'X-Api-App-Id': api_key,
}

url = api_url + '/resumes'

currency_dict = {
    'rub': 'RUB',
    'usd': 'USD',
    'eur': 'EUR',
}

gender_dict = {
    0: None,
    1: None,
    2: 'male',
    3: 'female'
}


def get_item_db_field_dict(item, city_db_object_dict, profession_db_object_dict, platform):
    city_name = item['town']['title']
    db_field_item_dict = {
        'platform': platform,
        'platform_resume_id': item['id'],
        'platform_resume_tm_create': datetime.fromtimestamp(item['date_published']),
        'platform_resume_tm_update': datetime.fromtimestamp(item['date_last_modified']),
        'profession': profession_db_object_dict.setdefault(
            item['profession'],
            Profession.get_or_create(name=item['profession'])[0]
        ),
        'city': city_db_object_dict.setdefault(
            city_name,
            City.get_or_create(name=city_name)[0]
        ),
        'sex': item['gender']['id'],
        'age': item['age'],
        'salary_from': item.get('payment'),
        'currency': currency_dict.get(item.get('currency')),
        'experience_months': item['experience_month_count'],
        'summary_info': item,
        'link': item['link'],
    }
    return db_field_item_dict


# поля резюме
keys = ['id', 'last_profession', 'payment', 'currency', 'birthday', 'birthmonth', 'birthyear', 'hide_birthday', 'age',
        'metro', 'address', 'citizenship', 'published', 'draft', 'photo', 'photo_sizes', 'moveable', 'agreement',
        'receive_sms', 'moveable_towns', 'type_of_work', 'place_of_work', 'education', 'children', 'business_trip',
        'maritalstatus', 'languages', 'driving_licence', 'catalogues', 'town', 'region', 'experience_text',
        'experience_month_count', 'work_history', 'base_education_history', 'education_history', 'contacts_bought',
        'link', 'short_link', 'gender', 'achievements', 'additional_info', 'date_published', 'date_last_modified',
        'profession', 'is_archive', 'timeToUpdate', 'id_user', 'portfolio', 'simple_contacts_open']


def get_resumes():
    platform = Platform.get_or_create(name='Superjob')[0]
    city_db_object_dict = {}
    profession_db_object_dict = {}
    response = requests.get(
        url=url,
        headers=headers,
    ).json()
    data = []
    for item in response.get('objects'):
        data.append(get_item_db_field_dict(item, city_db_object_dict, profession_db_object_dict, platform))
    Resume.add(data)


if __name__ == '__main__':
    get_resumes()
