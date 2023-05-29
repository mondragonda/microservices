import motor.motor_asyncio
from bson import ObjectId
from os import getenv


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


client = motor.motor_asyncio.AsyncIOMotorClient(
    f'mongodb+srv://{getenv("MONGO_USERNAME")}:{getenv("MONGO_PASSWORD")}@{getenv("MONGO_HOSTNAME")}/?retryWrites=true&w=majority',
    getenv("MONGO_PORT", default=27017)
)
