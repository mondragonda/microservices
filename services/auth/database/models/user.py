from pydantic import BaseModel, Field, EmailStr, PastDate, SecretStr
from ....database import PyObjectId
from datetime import date


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")  # Model id
    email: EmailStr
    password: SecretStr
    photo_url: str
    first_name: str
    last_name: str
    # date_of_birth: PastDate
    date_of_birth: date
    address: str
