import requests
from config import CONFIG
from base import Resume, Profession, City, Platform
from datetime import datetime
from dateutil.relativedelta import relativedelta

api_url = CONFIG.get('hh_api_url')
url = api_url + '/resumes'

headers = {
    'Authorization': f'Bearer {CONFIG.get("hh_user_authorization_code")}'
}

params = {
    'text': ('разработчик', 'sql', 'senior'),
    'period': 7,
}

currency_dict = {
    'RUR': 'RUB',
    'USD': 'USD',
    'EUR': 'EUR',
}


def experience_months(exp_list):
    if not exp_list:
        return 0
    dt_start = datetime.strptime(exp_list[-1]['start'], "%Y-%m-%d").date()
    dt_end = exp_list[0]['end']
    if not dt_end:
        dt_end = datetime.now().date()
    else:
        dt_end = datetime.strptime(dt_end, "%Y-%m-%d").date()

    difference = relativedelta(dt_end, dt_start)
    months_difference = difference.years * 12 + difference.months
    return months_difference


def get_item_db_field_dict(item, city_db_object_dict, profession_db_object_dict, platform):
    city_name = item['area']['name']
    db_field_item_dict = {
        'platform': platform,
        'platform_resume_id': item['id'],
        'platform_resume_tm_create': datetime.strptime(item['created_at'], "%Y-%m-%dT%H:%M:%S%z"),
        'platform_resume_tm_update': datetime.strptime(item['updated_at'], "%Y-%m-%dT%H:%M:%S%z"),
        'profession': profession_db_object_dict.setdefault(
            item['title'],
            Profession.get_or_create(name=item['title'])[0]
        ),
        'city': city_db_object_dict.setdefault(
            city_name,
            City.get_or_create(name=city_name)[0]
        ),
        'sex': item['gender']['id'],
        'age': item['age'],
        'salary_from': item.get('salary') and item['salary'].get('amount'),
        'currency': currency_dict.get(item.get('salary') and item['salary'].get('currency')),
        'experience_months': item['total_experience']['months'],
        'summary_info': item,
        'link': item['alternate_url'],
    }
    return db_field_item_dict


def get_resumes(page):
    platform = Platform.get_or_create(name='HH')[0]
    city_db_object_dict = {}
    profession_db_object_dict = {}
    params['page'] = page
    response = requests.get(
        url=url,
        headers=headers,
        params=params,
    ).json()
    page += 1
    data = []
    for item in response['items']:
        print(item['created_at'])
        data.append(get_item_db_field_dict(item, city_db_object_dict, profession_db_object_dict, platform))
    Resume.add(data)


keys = ['last_name', 'first_name', 'middle_name', 'title', 'created_at', 'updated_at', 'area', 'age', 'gender',
        'salary', 'photo', 'total_experience', 'certificate', 'owner', 'can_view_full_info', 'negotiations_history',
        'hidden_fields', 'actions', 'url', 'alternate_url', 'id', 'download', 'platform', 'education', 'experience',
        'favorited', 'viewed', 'marked', 'last_negotiation']


if __name__ == '__main__':
    get_resumes(3)
