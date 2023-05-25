import strawberry
from strawberry.dataloader import DataLoader
from schema.advisor import FinancialAdvisor
from typing import List
from financial.database.database import db


async def load_financial_advisors(keys: List[int]) -> List[FinancialAdvisor]:
    return [db.financial_advisors.find_one({id: key}) for key in keys]


loader = DataLoader(load_fn=load_financial_advisors)


@strawberry.type
class Query:
    @strawberry.field
    async def financial_advisors(self, id: int) -> FinancialAdvisor:
        return await loader.load(id)
