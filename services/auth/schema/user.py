import strawberry
import datetime
import bson
from ..resolver.mutations.user import Mutation
from typing import List
from strawberry.dataloader import DataLoader
import strawberry
from ..database.database import db


@strawberry.federation.type(keys=["_id"], description="User register information.")
class User:
    _id: bson.ObjectId
    email: str
    password: strawberry.Private[str]
    photo_url: str
    first_name: str
    last_name: str
    date_of_birth: datetime.date
    address: str

    def __init__(self, _id: bson.ObjectId, email: str, photo_url: str, first_name: str, last_name: str, date_of_birth: datetime.date, address: str):
        self._id = _id
        self.email = email
        self.photo_url = photo_url
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.address = address


async def load_users() -> List[User]:
    return [User(
        _id=user._id,
        email=user.email,
        photo_url=user.photo_url,
        first_name=user.first_name,
        last_name=user.last_name,
        date_of_birth=user.date_of_birth,
        address=user.address
    ) async for user in db.users.find()]


# loader = DataLoader(load_fn=load_users)

@strawberry.type
class Query:
    @strawberry.field
    async def users(self, _id: str) -> List[User]:
        return await load_users()


schema = strawberry.federation.Schema(
    query=Query,
    enable_federation_2=True,
)
