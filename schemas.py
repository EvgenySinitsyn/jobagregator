# Модель пользователя
from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None




# Модель для входа
class UserInDB(User):
    hashed_password: str
