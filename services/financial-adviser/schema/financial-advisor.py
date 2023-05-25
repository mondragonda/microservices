import strawberry
from auth.schema.user import User


@strawberry.federation.type(keys=["id"], description="Financial advisers information")
class FinancialAdvisor:
    user: User
    contact_phone_number: str
