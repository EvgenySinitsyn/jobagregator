from datetime import timezone

from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from whatsapp_api_client_python import API

from api_hh import HHParser
from api_superjob import SuperjobParser
from typing import Optional, Annotated
from job_stat import read_stat
from login import router, User, get_current_active_user

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
    hh_data = hh_parser.get_resumes(
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
    sj_data = sj_parser.get_resumes(
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
    hh_data = hh_parser.get_vacancies(
        city=city,
        create_tm=create_tm,
        experience_from=experience_from,
        salary=salary,
        text=text,
        page=page,
    )
    sj_data = sj_parser.get_vacancies(
        city=city,
        create_tm=create_tm,
        experience_from=experience_from,
        salary=salary,
        text=text,
        page=page,
    )
    res = hh_data + sj_data
    return res


@app.get('/stat')
async def get_stat(current_user: Annotated[User, Depends(get_current_active_user)], text: Optional[str] = ''):
    res = read_stat(text)
    return res
