from pydantic import BaseModel, Field, EmailStr, SecretStr
from ....database import PyObjectId
from datetime import date


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    password: SecretStr
    photo_url: str
    first_name: str
    last_name: str
    # date_of_birth: PastDate
    date_of_birth: date
    address: str
