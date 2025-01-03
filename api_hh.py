import requests
from config import CONFIG
from pprint import pprint
from base import Resume

api_url = CONFIG.get('hh_api_url')
url = api_url + '/resumes'

headers = {
    'Authorization': f'Bearer {CONFIG.get("hh_user_authorization_code")}'
}

response = requests.get(
    url=url,
    headers=headers,
).json()

pprint(response['items'][5]['age'])

keys = ['last_name', 'first_name', 'middle_name', 'title', 'created_at', 'updated_at', 'area', 'age', 'gender',
        'salary', 'photo', 'total_experience', 'certificate', 'owner', 'can_view_full_info', 'negotiations_history',
        'hidden_fields', 'actions', 'url', 'alternate_url', 'id', 'download', 'platform', 'education', 'experience',
        'favorited', 'viewed', 'marked', 'last_negotiation']

print(Resume.get_resume_count())
