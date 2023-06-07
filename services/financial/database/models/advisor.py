from pydantic import BaseModel, Field, PrivateAttr
from ....database import PyObjectId
from typing import Optional


class Advisor(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user: PyObjectId = Field(default_factory=PyObjectId)
    user_id: Optional[PyObjectId]
    contact_phone_number: str

    def __init__(self, **data):
        super().__init__(**data)
        self.user_id = data["user"]  # type: ignore
