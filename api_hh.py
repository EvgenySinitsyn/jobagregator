import requests
from config import CONFIG
from base import Resume, Profession, City, Platform, PlatformCity, Vacancy
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HHParser:
    api_url = CONFIG.get('hh_api_url')

    headers = {
        'Authorization': f'Bearer {CONFIG.get("hh_user_authorization_code")}'
    }

    currency_dict = {
        'RUR': 'RUB',
        'USD': 'USD',
        'EUR': 'EUR',
    }

    experience_dict = {
        (0,): 'noExperience',
        tuple(range(12, 37)): 'between1And3',
        tuple(range(37, 73)): 'between3And6',
        tuple(range(73, 100000)): 'moreThan6',
    }

    experience_months_dict = {
        'noExperience': (None, None),
        'between1And3': (12, 36),
        'between3And6': (36, 72),
        'moreThan6': (72, None),
    }

    education_dict = {
        'second': 'secondary',
        'higher': 'higher',
    }

    max_page = 99

    def experience_months(self, exp_list):
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

    def get_resume_db_field_dict(self, item, city_db_object_dict, profession_db_object_dict, platform):
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
            'currency': self.currency_dict.get(item.get('salary') and item['salary'].get('currency')),
            'experience_months': item.get('total_experience') and item.get('total_experience').get('months'),
            'summary_info': item,
            'link': item['alternate_url'],
        }
        return db_field_item_dict

    def get_vacancy_db_field_dict(self, item, city_db_object_dict, profession_db_object_dict, platform):
        city_name = item['area']['name']
        experience_name = item.get('experience') and item['experience'].get('id')
        experience_range = self.experience_months_dict.get(experience_name)
        if not experience_range:
            experience_range = (None, None)
        db_field_item_dict = {
            'platform': platform,
            'platform_vacancy_id': item['id'],
            'platform_vacancy_tm_create': datetime.strptime(item['created_at'], "%Y-%m-%dT%H:%M:%S%z"),
            'city': city_db_object_dict.setdefault(
                city_name,
                City.get_or_create(name=city_name)[0]
            ),
            'profession': profession_db_object_dict.setdefault(
                item['name'],
                Profession.get_or_create(name=item['name'])[0]
            ),
            'salary_from': item.get('salary') and item['salary'].get('from'),
            'salary_to': item.get('salary') and item['salary'].get('to'),
            'schedule': item.get('schedule') and item['schedule'].get('name'),
            'currency': self.currency_dict.get(item.get('salary') and item['salary'].get('currency')),
            'experience_months_from': experience_range[0],
            'experience_months_to': experience_range[1],
            'link': item.get('alternate_url'),
            'employer_name': item.get('employer') and item['employer'].get('name'),
            'contact_email': item.get('contacts') and item['contacts'].get('email'),
            'contact_phone': item.get('contacts') and item['contacts'].get('phones') and item['contacts'].get(
                'phones')[0].get('formatted'),
            'contact_person': item.get('contacts') and item['contacts'].get('name'),
            'summary_info': item,
        }
        return db_field_item_dict

    def db_add_areas_info(self, areas, platform_id):
        for area in areas:
            self.db_add_areas_info(area['areas'], platform_id)
            city_id = City.get_or_create(name=area['name'])[0]
            platform_city_id = area['id']
            PlatformCity.add(
                platform_id=platform_id,
                city_id=city_id,
                platform_city_id=platform_city_id,
            )

    def get_area(self):
        params = {
        }
        response = requests.get(
            url=self.api_url + '/areas',
            headers=self.headers,
            params=params,
        ).json()
        platform = Platform.get_or_create(name='HH')[0]
        self.db_add_areas_info(response, platform)

    def get_vacancies(
            self,
            city=None,
            create_tm=None,
            experience_from=None,
            salary=None,
            text=None,
            page=0,
    ):
        platform = Platform.get_or_create(name='HH')[0]
        city_db_object_dict = {}
        profession_db_object_dict = {}
        params = {
            'page': page % self.max_page,
            'salary': salary,
        }
        if text:
            params['text'] = text

        if experience_from:
            for months, value in self.experience_dict.items():
                if experience_from in months:
                    params['experience'] = value

        if city:
            platform_city = PlatformCity.get_by_name(city)
            if platform_city:
                params['area'] = platform_city.platform_city_id

        if create_tm:
            date_object = datetime.strptime(create_tm, "%Y-%m-%d")
            params['period'] = (datetime.now() - date_object).days

        response = requests.get(
            url=self.api_url + '/vacancies',
            headers=self.headers,
            params=params,
        ).json()
        data = []
        for item in response['items']:
            data.append(self.get_vacancy_db_field_dict(item, city_db_object_dict, profession_db_object_dict, platform))
        Vacancy.add(data)
        return data

    def get_resumes(
            self,
            city=None,
            gender=None,
            create_tm=None,
            experience_from=None,
            text=None,
            education=None,
            age_from=None,
            age_to=None,
            page=0,
    ):
        platform = Platform.get_or_create(name='HH')[0]
        city_db_object_dict = {}
        profession_db_object_dict = {}
        params = {
            'gender': gender,
            'education_level': self.education_dict.get(education),
            'age_from': age_from,
            'age_to': age_to,
            'page': page % self.max_page,
        }

        if city:
            platform_city = PlatformCity.get_by_name(city)
            if platform_city:
                params['area'] = platform_city.platform_city_id
        if create_tm:
            date_object = datetime.strptime(create_tm, "%Y-%m-%d")
            params['period'] = (datetime.now() - date_object).days

        if experience_from:
            for months, value in self.experience_dict.items():
                if experience_from in months:
                    params['experience'] = value

        if text:
            params['text'] = text.split()
        response = requests.get(
            url=self.api_url + '/resumes',
            headers=self.headers,
            params=params,
        ).json()
        data = []
        for item in response['items']:
            data.append(self.get_resume_db_field_dict(item, city_db_object_dict, profession_db_object_dict, platform))
        Resume.add(data)
        return data


# поля резюме
keys = ['last_name', 'first_name', 'middle_name', 'title', 'created_at', 'updated_at', 'area', 'age', 'gender',
        'salary', 'photo', 'total_experience', 'certificate', 'owner', 'can_view_full_info', 'negotiations_history',
        'hidden_fields', 'actions', 'url', 'alternate_url', 'id', 'download', 'platform', 'education', 'experience',
        'favorited', 'viewed', 'marked', 'last_negotiation']

if __name__ == '__main__':
    hh = HHParser()
    hh.get_resumes(page=1, text='ВТБ')
