import strawberry
from ..resolver.mutations.user import Mutation
from typing import List
import strawberry
from ..database.database import db
from ..database.models.user import User as UserModel
from ...strawberryconf import PyObjectIdType


@strawberry.experimental.pydantic.type(model=UserModel)
@strawberry.federation.type(keys=["_id"], description="User register information.")
class User:
    id: PyObjectIdType
    email: strawberry.auto
    # password: strawberry.Private[strawberry.auto]
    photo_url: strawberry.auto
    first_name: strawberry.auto
    last_name: strawberry.auto
    date_of_birth: strawberry.auto
    address: strawberry.auto


async def load_users() -> List[User]:
    users_cursor = db.users.find()
    users = await users_cursor.to_list(length=100)
    if users:
        return [User.from_pydantic(UserModel.parse_obj(user)) for user in users]
    else:
        return []


@strawberry.type
class Query:
    @strawberry.field
    async def users(self) -> List[User]:
        return await load_users()


schema = strawberry.federation.Schema(
    query=Query,
    enable_federation_2=True,
)
