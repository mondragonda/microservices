import strawberry
from typing import List
from ...auth.schema.user import User
from ...auth.database.database import db as auth_db
from ..database.database import db
from ..database.models.advisor import Advisor as AdvisorModel
from ...strawberryconf import PyObjectIdType


@strawberry.experimental.pydantic.type(model=AdvisorModel)
@strawberry.federation.type(keys=["id"], description="Financial advisor information.")
class Advisor:
    id: PyObjectIdType
    user: User
    contact_phone_number: str


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
