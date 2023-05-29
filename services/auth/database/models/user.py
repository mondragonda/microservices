from pydantic import BaseModel, Field
from datetime import date
from ....database import PyObjectId


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")  # Model id
    email: str
    password: str
    photo_url: str
    first_name: str
    last_name: str
    date_of_birth: date
    address: str
