from pydantic import BaseModel, Field
from ....database import PyObjectId


class Advisor(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user: PyObjectId = Field(default_factory=PyObjectId)
    contact_phone_number: str
