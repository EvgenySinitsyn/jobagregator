import aiohttp
import requests
from config import CONFIG
from datetime import datetime
from base import Platform, Profession, City, Resume, Vacancy
import random

from utils import filter_params


class SuperjobParser:
    api_key = CONFIG.get('superjob_api_auth_key')
    api_url = CONFIG.get('superjob_api_url')

    headers = {
        'X-Api-App-Id': api_key,
    }

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

    period_dict = {
        (0,): 0,
        (1,): 1,
        tuple(range(2, 4)): 3,
        tuple(range(4, 8)): 7,
        tuple(range(8, 15)): 14,
        tuple(range(15, 31)): 30,
        tuple(range(31, 61)): 60,
    }

    education_dict = {
        'second': 5,
        'higher': 2,
    }

    experience_dict = {
        (0,): 1,
        tuple(range(12, 37)): 2,
        tuple(range(37, 73)): 3,
        tuple(range(73, 100000)): 4,
    }

    experience_months_dict = {
        1: (None, None),
        2: (None, 12),
        3: (12, 72),
        4: (72, None),
    }

    def get_towns(self, keyword=None):
        params = {
            'keyword': keyword,
        }
        response = requests.get(
            url=self.api_url + '/towns',
            headers=self.headers,
            params=params,
        ).json()

    async def get_vacancies(
            self,
            city=None,
            create_tm=None,
            experience_from=None,
            salary=None,
            text=None,
            page=0,
            count=20,
    ):
        print('start superjob vacancies')
        platform = Platform.get_or_create(name='Superjob')[0]
        city_db_object_dict = {}
        profession_db_object_dict = {}
        params = {
            'keyword': text,
            'count': count,
            'town': city,
            'page': page,
            'payment_from': salary,
        }
        if create_tm:
            date_object = datetime.strptime(create_tm, "%Y-%m-%d")
            difference = (datetime.now() - date_object).days
            for period, value in self.period_dict.items():
                if difference in period:
                    params['period'] = value

        if experience_from:
            for months, value in self.experience_dict.items():
                if experience_from in months:
                    params['experience'] = value

        async with aiohttp.ClientSession() as session:
            url = self.api_url + '/vacancies'
            async with session.get(url, headers=self.headers, params=filter_params(**params)) as response:
                if response.status == 200:
                    print('superjob ok')
                    response = await response.json()
                else:
                    print("ERROR API HH")
                    return
        data = []
        for item in response['objects']:
            data.append(self.get_vacancy_db_field_dict(item, city_db_object_dict, profession_db_object_dict, platform))
        Vacancy.add(data)
        return data

    async def get_resumes(
            self,
            city=None,
            gender=None,
            create_tm=None,
            experience_from=None,
            experience_to=None,
            text=None,
            education=None,
            age_from=None,
            age_to=None,
            page=0,
    ):
        print('start superjob resumes')
        params = {
            'keyword': text,
            'town': city,
            'education': self.education_dict.get(education),
            'age_from': age_from,
            'age_to': age_to,
            'page': page,
        }

        if gender:
            for key, value in self.gender_dict.items():
                if gender == value:
                    params['gender'] = key
        if experience_from:
            for months, value in self.experience_dict.items():
                if experience_from in months:
                    params['experience'] = value
        if create_tm:
            date_object = datetime.strptime(create_tm, "%Y-%m-%d")
            difference = (datetime.now() - date_object).days
            for period, value in self.period_dict.items():
                if difference in period:
                    params['period'] = value
        platform = Platform.get_or_create(name='Superjob')[0]
        city_db_object_dict = {}
        profession_db_object_dict = {}
        async with aiohttp.ClientSession() as session:
            url = self.api_url + '/resumes'
            async with session.get(url, headers=self.headers, params=filter_params(**params)) as response:
                if response.status == 200:
                    response = await response.json()
                    print('superjob ok')
                else:
                    print("ERROR API Superjob")
                    return

        data = []
        for item in response.get('objects'):
            data.append(self.get_resume_db_field_dict(item, city_db_object_dict, profession_db_object_dict, platform))
        Resume.add(data)
        return data

    def get_resume_db_field_dict(self, item, city_db_object_dict, profession_db_object_dict, platform):
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
            'sex': self.gender_dict.get(item['gender']['id']),
            'age': item['age'],
            'salary_from': item.get('payment'),
            'currency': self.currency_dict.get(item.get('currency')),
            'experience_months': item['experience_month_count'],
            'summary_info': item,
            'link': item['link'],
            'phone': random.choice(CONFIG.get('temp_phones'))
        }
        return db_field_item_dict

    def get_vacancy_db_field_dict(self, item, city_db_object_dict, profession_db_object_dict, platform):
        city_name = item['town']['title']
        experience_name = item.get('experience') and item['experience'].get('id')
        experience_range = self.experience_months_dict.get(experience_name)
        phones = item.get('phones')
        phone = None
        if phones:
            phone = phones[0].get('number')
            if phone:
                phone = '+' + phone
        if not experience_range:
            experience_range = (None, None)
        db_field_item_dict = {
            'platform': platform,
            'platform_vacancy_id': item['id'],
            'platform_vacancy_tm_create': datetime.fromtimestamp(item['date_published']),
            'city': city_db_object_dict.setdefault(
                city_name,
                City.get_or_create(name=city_name)[0]
            ),
            'profession': profession_db_object_dict.setdefault(
                item['profession'],
                Profession.get_or_create(name=item['profession'])[0]
            ),
            'salary_from': item.get('payment_from'),
            'salary_to': item.get('payment_to'),
            'currency': self.currency_dict.get(item.get('currency')),
            'experience_months_from': experience_range[0],
            'experience_months_to': experience_range[1],
            'link': item.get('link'),
            'employer_name': item.get('client') and item['client'].get('title'),
            'contact_email': item.get('email'),
            'contact_phone': phone,
            'contact_person': item.get('contact'),
            'summary_info': item,
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


if __name__ == '__main__':
    superjob_parser = SuperjobParser()
    superjob_parser.get_vacancies()
