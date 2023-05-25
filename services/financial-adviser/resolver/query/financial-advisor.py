from typing import Optional
import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def financial_advisors(self) -> Optional[Thing]:
        return Thing(id=id, name="Thing")
