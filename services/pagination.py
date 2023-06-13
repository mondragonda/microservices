from typing import TypeVar, Generic
import strawberry
from abc import ABC

T = TypeVar("T")


@strawberry.type
class PaginationWindow(Generic[T]):
    items: list[T] = strawberry.field(
        description="The list of items in this pagination window."
    )

    total_items_count: int = strawberry.field(
        description="Total number of items in the filtered dataset."
    )


async def get_pagination_window(
        ItemType,
        ModelType,
        collection,
        limit: int,
        offset: int = 0) -> PaginationWindow:

    records_count = await collection.estimated_document_count()

    if limit <= 0 or limit > 100:
        raise Exception(f'limit ({limit}) must be between 0-100')

    if offset != 0 and not 0 <= offset < records_count:
        raise Exception(f'offset ({offset}) is out of range '
                        f'(0-{records_count - 1})')

    items_cursor = collection.find()

    items_cursor.limit(limit)
    items_cursor.skip(offset)

    items = await items_cursor.to_list(None)

    items = [ItemType.from_pydantic(ModelType.parse_obj(x)) for x in items]

    return PaginationWindow(
        items=items,
        total_items_count=records_count
    )
