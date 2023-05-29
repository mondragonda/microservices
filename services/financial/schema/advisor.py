import strawberry
from auth.schema.user import User
from auth.database.database import db
from resolver.mutations.advisor import Mutation
from resolver.query.advisor import Query


def get_user(root: "FinancialAdvisor") -> User:
    return db.users.findOne({id: root.user})


@strawberry.federation.type(keys=["id"], description="Financial advisor information.")
class FinancialAdvisor:
    user: User = strawberry.field(resolver=get_user)
    contact_phone_number: str


schema = strawberry.federation.Schema(
    Query,
    Mutation,
    enable_federation_2=True,
)
