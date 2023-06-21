import strawberry
from strawberry.types import Info
from typing import List
from ..database.database import db
from ..database.models.user import User as UserModel
from ...strawberryconf import PyObjectIdType
from ..authorization import authorization_service


@strawberry.experimental.pydantic.type(
    model=UserModel,
    description="User register information.",
    all_fields=False
)
class User:
    id: PyObjectIdType
    email: strawberry.auto
    photo_url: strawberry.auto
    first_name: strawberry.auto
    last_name: strawberry.auto
    date_of_birth: strawberry.auto
    address: strawberry.auto


async def load_users(info: Info) -> List[User]:
    logged_user_claims = authorization_service.get_access_token_claims(
        info.context["request"])
    users_cursor = db.users.find(
        {"email": logged_user_claims["sub"]} if logged_user_claims else {})
    users = await users_cursor.to_list(length=100)
    if users:
        return [User.from_pydantic(UserModel.parse_obj(user)) for user in users]
    else:
        return []


@strawberry.type
class Query:
    @strawberry.field
    async def users(self, info: Info) -> List[User]:
        return await load_users(info)


schema = strawberry.federation.Schema(
    query=Query,
    enable_federation_2=True,
)
