import pprint
from base import Profession, Resume, Vacancy

DATA = {
    'names': [], # список профессий, нужно выводить в блоке под боковой панелью фильтров с возможностью прокрутки
    # все доли указаны в процентах
    'resume': {
        'count': 0, # количество резюме,
        'cities': [ # всего 5 городов с наисвысшим показателем
            {
                'name': '', # название города
                'proc': 0, # показатель доли резюме в городе
            },
        ],
        'gender': {
            'male': 0, # количество мужчин
            'female': 0, # количество женщин
            'exists_proc': 0, # доля записей с указанием пола
        },
        'age': {
            'exists_proc': 0, # доля записей с указанием возраста
            'average': 0, # средний возраст
        },
        'salary': {
            'exists_proc': 0, # доля записей с указанием зарплатных ожиданий
            'average': 0, # средние ожидания
        },
        'experience': {
            'exists_proc': 0, # доля записей с указанием опыта
            'average': 0, # средний опыт в месяцах
        },
    },

    'vacancy': {
        'count': 0,
        'cities': [ # количество вакансий,
            {
                'name': '', # название города
                'proc': 0, # показатель доли вакансий в городе
            },
        ],
        'salary_from': {
            'exists_proc': 0, # доля записей с указанием нижней грани зарплаты
            'average': 0, # средняя нижняя грань зарплаты
        },
        'salary_to': {
            'exists_proc': 0, # доля записей с указанием верхней грани зарплаты
            'average': 0, # средняя верхняя грань зарплаты
        },
        'experience_from': {
            'exists_proc': 0, # доля записей с указанием нижней грани опыта
            'average': 0, # средняя нижняя грань опыта
        },
        'experience_to': {
            'exists_proc': 0, # доля записей с указанием верхней грани опыта
            'average': 0, # средняя верхняя грань опыта
        }
    }
}


def get_data(resumes, vacancies, professions, data):
    data['names'] = [profession.name for profession in professions]

    # статистика резюме
    if resumes:
        total_count_resumes = len(resumes)
        data['resume']['count'] = total_count_resumes

        set_object_cities(data, resumes, 'resume', total_count_resumes)

        male_count = len(list(filter(lambda item: item.sex == 'male', resumes)))
        female_count = len(list(filter(lambda item: item.sex == 'female', resumes)))
        data['resume']['gender']['male'] = male_count
        data['resume']['gender']['female'] = female_count
        data['resume']['gender']['exists_proc'] = round((male_count + female_count) / total_count_resumes * 100, 2)

        resume_average_age, exists_proc = get_average_fields(resumes, 'age', total_count_resumes)
        data['resume']['age']['exists_proc'] = exists_proc
        data['resume']['age']['average'] = resume_average_age

        resume_average_salary, exists_proc = get_average_fields(resumes, 'salary_from', total_count_resumes, True)
        data['resume']['salary']['exists_proc'] = exists_proc
        data['resume']['salary']['average'] = resume_average_salary

        resume_average_experience, exists_proc = get_average_fields(resumes, 'experience_months', total_count_resumes)
        data['resume']['experience']['exists_proc'] = exists_proc
        data['resume']['experience']['average'] = resume_average_experience

    # статистика вакансий
    if vacancies:
        total_count_vacancies = len(vacancies)
        data['vacancy']['count'] = total_count_vacancies

        set_object_cities(data, vacancies, 'vacancy', total_count_vacancies)

        vacancy_average_salary_from, exists_proc = get_average_fields(vacancies, 'salary_from', total_count_vacancies, True)
        data['vacancy']['salary_from']['exists_proc'] = exists_proc
        data['vacancy']['salary_from']['average'] = vacancy_average_salary_from

        vacancy_average_salary_to, exists_proc = get_average_fields(vacancies, 'salary_to', total_count_vacancies, True)
        data['vacancy']['salary_to']['exists_proc'] = exists_proc
        data['vacancy']['salary_to']['average'] = vacancy_average_salary_to

        vacancy_average_experience_from, exists_proc = get_average_fields(
            vacancies, 'experience_months_from', total_count_vacancies
        )
        data['vacancy']['experience_from']['exists_proc'] = exists_proc
        data['vacancy']['experience_from']['average'] = vacancy_average_experience_from

        vacancy_average_experience_to, exists_proc = get_average_fields(
            vacancies, 'experience_months_to', total_count_vacancies
        )
        data['vacancy']['experience_to']['exists_proc'] = exists_proc
        data['vacancy']['experience_to']['average'] = vacancy_average_experience_to

    return data


def set_object_cities(data, objects, object_name, total_count):
    data[object_name]['cities'] = []
    cities = {}
    for obj in objects:
        cities[obj.city.name] = cities.get(obj.city.name, 0) + 1
    cities_count_list = cities.items()

    for city in sorted(cities_count_list, key=lambda item: item[1], reverse=True)[:5]:
        data[object_name]['cities'].append(
            {
                'name': city[0],
                'proc': round(city[1] / total_count * 100, 2),
            }
        )


def get_average_fields(object_list, field_name, total_count, is_salary=False):
    additional_predicate = (lambda obj: obj.currency == 'RUB' if is_salary else True)

    obj_list = [
        getattr(
            object_, field_name
        ) for object_ in object_list if getattr(object_, field_name) is not None and additional_predicate(object_)
    ]
    if obj_list:
        obj_list_len = len(obj_list)
        average_obj = round(sum(obj_list) / obj_list_len, 2)
        exists_proc = round(obj_list_len / total_count * 100, 2)
    else:
        average_obj = 0
        exists_proc = 0
    return average_obj, exists_proc


def read_stat(text):
    professions = Profession.get_by_text(text)
    resumes = Resume.get_by_professions(professions)
    vacancies = Vacancy.get_by_professions(professions)
    data = get_data(resumes, vacancies, professions, DATA)
    return data


if __name__ == '__main__':
    text = 'тестовая профессия'

    professions = Profession.get_by_text(text)
    resumes = Resume.get_by_professions(professions)
    vacancies = Vacancy.get_by_professions(professions)
    data = get_data(resumes, vacancies, professions, DATA)
    pprint.pprint(data)
