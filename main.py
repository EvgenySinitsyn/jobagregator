import pprint
from datetime import timezone

from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from whatsapp_api_client_python import API
import asyncio

from api_hh import HHParser
from api_superjob import SuperjobParser
from typing import Optional, Annotated

from green_api import GreenApi
from job_stat import read_stat
from login import router, User, get_current_active_user
from base import WhatsappMessage, User as UserDB, WhatsappInstance, WhatsappUserSubscriber, WhatsappSubscriber

app = FastAPI()
app.include_router(router)

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Origin", "Access-Control-Allow-Headers",
                   "Authorization",
                   "Access-Control-Allow-Credentials"],
    expose_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Origin", "Access-Control-Allow-Headers",
                    "Access-Authorization", "Access-Control-Allow-Credentials", "Authorization"]
)
hh_parser = HHParser()
sj_parser = SuperjobParser()


def ensure_aware(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)  # или используйте нужную вам временную зону
    return dt


def filter_params(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


@app.get("/resumes")
async def get_resumes(
        current_user: Annotated[User, Depends(get_current_active_user)],
        city: Optional[str] = None,
        gender: Optional[str] = None,
        create_tm: Optional[str] = None,
        experience_from: Optional[int] = None,
        position: Optional[str] = None,
        education: Optional[str] = None,
        age_from: Optional[int] = None,
        age_to: Optional[int] = None,
        page: Optional[int] = None,
):
    params = filter_params(
        city=city,
        gender=gender,
        create_tm=create_tm,
        experience_from=experience_from,
        text=position,
        education=education,
        age_from=age_from,
        age_to=age_to,
        page=page,
    )

    hh_task = asyncio.create_task(hh_parser.get_resumes(**params))
    sj_task = asyncio.create_task(sj_parser.get_resumes(**params))

    hh_data, sj_data = await asyncio.gather(hh_task, sj_task)
    res = hh_data + sj_data
    return res


@app.get("/vacancies", )
async def get_vacancies(
        current_user: Annotated[User, Depends(get_current_active_user)],
        city: Optional[str] = None,
        create_tm: Optional[str] = None,
        experience_from: Optional[int] = None,
        salary: Optional[int] = None,
        text: Optional[str] = None,
        page: Optional[int] = 0,
):
    print('get vac')
    params = filter_params(
        city=city,
        create_tm=create_tm,
        experience_from=experience_from,
        salary=salary,
        text=text,
        page=page,
    )
    hh_task = asyncio.create_task(hh_parser.get_vacancies(**params))
    sj_task = asyncio.create_task(sj_parser.get_vacancies(**params))
    hh_data, sj_data = await asyncio.gather(hh_task, sj_task)

    res = hh_data + sj_data
    return res


@app.get('/stat')
async def get_stat(current_user: Annotated[User, Depends(get_current_active_user)], text: Optional[str] = ''):
    res = read_stat(text)
    return res


def get_chat_data(chat, subscriber_phone):
    result = []
    name = subscriber_phone
    subscriber = WhatsappSubscriber.get_by_phone(subscriber_phone)
    if subscriber and subscriber.name:
        name = subscriber.name
    for message in reversed(chat):
        if message.get('typeMessage') == 'textMessage':
            message_data = {
                'type': message.get('type'),
                'subscriber_name': name,
                'text': message.get('textMessage'),
            }
            result.append(message_data)
    return result


@app.get('/get_chat')
async def get_stat(
        current_user: Annotated[User, Depends(get_current_active_user)],
        subscriber_phone: str = '',
):
    user_db = UserDB.get_by_username(current_user.username)
    whatsapp_instance = WhatsappInstance.get_by_user_id(user_id=user_db.id)
    if not whatsapp_instance:
        return

    green_api = GreenApi(whatsapp_instance.instance_id, whatsapp_instance.instance_token)
    chat = await green_api.get_chat(subscriber_phone)
    chat_data = get_chat_data(chat, subscriber_phone)
    pprint.pprint(chat_data)

    return chat_data


@app.get('/get_subscribers')
async def get_subscribers(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    user = UserDB.get_by_username(current_user.username)
    subscribers = WhatsappUserSubscriber.get_subscriber_list(user.id)
    pprint.pprint(subscribers)
    return subscribers
