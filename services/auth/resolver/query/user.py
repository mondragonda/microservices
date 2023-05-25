import strawberry
from strawberry.dataloader import DataLoader
from schema.user import User
from typing import List
from auth.database.database import db


async def load_users(keys: List[int]) -> List[User]:
    return [db.users.find_one({id: key}) for key in keys]


loader = DataLoader(load_fn=load_users)


@strawberry.type
class Query:
    @strawberry.field
    async def users(self, id: int) -> User:
        return await loader.load(id)
