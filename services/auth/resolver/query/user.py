import strawberry
from typing import Optional
from schema.user import User


@strawberry.type
class Query:
    @strawberry.field
    def users(self):
        if False:
            return [Thing(id=id, name="Thing")]
        return []

    def user(self, id: strawberry.ID):
        return None
