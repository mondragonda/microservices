import strawberry
from typing import List, Dict, Any

from services.database import PyObjectId
from ...auth.schema.user import User
from ...auth.database.models.user import User as UserModel
from ...auth.database.database import db as auth_db
from ..database.database import db
from ..database.models.advisor import Advisor as AdvisorModel
from ...strawberryconf import PyObjectIdType
from ..database.database import db
from ...pagination import PaginationWindow, get_pagination_window

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
    @strawberry.field(description="Get a list of advisors.")
    async def advisors(self, limit: int = 100, offset: int = 0) -> PaginationWindow[Advisor]:
        return await get_pagination_window(
            ItemType=Advisor,  # type: ignore
            ModelType=AdvisorModel,
            collection=db.advisors,
            limit=limit,
            offset=offset
        )


@strawberry.type
class UserForAdvisorNotExistsError:
    user: str


@strawberry.type
class AdvisorAlreadyExistsError:
    user: str


MutationResponse = strawberry.union(
    "AddAdvisorResponse", [UserForAdvisorNotExistsError,
                           AdvisorAlreadyExistsError, Advisor]
)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def add_advisor(self, user: str, contact_phone_number: str) -> MutationResponse:  # type: ignore
        advisor_obj = {"user": PyObjectId(
            user), "contact_phone_number": contact_phone_number}
        valid_advisor = AdvisorModel.validate(advisor_obj)
        if valid_advisor:
            user_exists = await auth_db.users.find_one({"_id": advisor_obj["user"]})
            if not user_exists:
                return UserForAdvisorNotExistsError(
                    user=user
                )
            existing_advisor_for_user = await db.advisors.find_one({"user": advisor_obj["user"]})
            if existing_advisor_for_user:
                return AdvisorAlreadyExistsError(user=user)
            created_advisor_result = await db.advisors.insert_one(advisor_obj)
            if created_advisor_result:
                created_advisor_record = await db.advisors.find_one({"_id": PyObjectId(created_advisor_result.inserted_id)})
                return Advisor.from_pydantic(AdvisorModel.parse_obj(created_advisor_record))


schema = strawberry.federation.Schema(
    Query,
    Mutation,
    enable_federation_2=True,
)
