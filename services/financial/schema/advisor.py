import strawberry
from typing import List
from ...auth.schema.user import User
from ...auth.database.models.user import User as UserModel
from ...auth.database.database import db as auth_db
from ..database.database import db
from ..database.models.advisor import Advisor as AdvisorModel
from ...strawberryconf import PyObjectIdType


# WORKAROUND TO FIX LATER
async def get_user(root: "Advisor") -> "User":
    return User.from_pydantic(UserModel.parse_obj(
        await auth_db.users.find_one({"_id": root.user_id})  # type: ignore
    ))


@strawberry.experimental.pydantic.type(
    model=AdvisorModel,
    description="Financial advisor information.",
    all_fields=False
)
class Advisor:
    id: PyObjectIdType
    contact_phone_number: strawberry.auto
    user_id: PyObjectIdType
    user: User = strawberry.field(resolver=get_user)


async def load_financial_advisors() -> List[Advisor]:
    advisors_cursor = db.advisors.find()
    advisors = await advisors_cursor.to_list(length=100)
    if advisors:
        return [Advisor.from_pydantic(AdvisorModel.parse_obj(advisor)) for advisor in advisors]
    else:
        return []


@strawberry.type
class Query:
    @strawberry.field
    async def advisors(self) -> List[Advisor]:
        return await load_financial_advisors()


schema = strawberry.federation.Schema(
    Query,
    enable_federation_2=True,
)
