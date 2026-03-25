from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.tables import Item, Parent
from schemas import ItemSchema, ParentSchema


async def add_item(session: AsyncSession, item_data: ItemSchema) -> int:
    item = Item(emoji=item_data.emoji, text=item_data.text)
    for parent_data in item_data.parents:
        item.parents.append(Parent(first=parent_data.first, second=parent_data.second))
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item.id


async def add_parent(session: AsyncSession, parent_data: ParentSchema) -> bool:
    item = await session.get(Item, parent_data.item_id)
    if not item:
        return False
    item.parents.append(Parent(first=parent_data.first, second=parent_data.second))
    await session.commit()
    return True


async def get_item(session: AsyncSession, item_id: int) -> ItemSchema | None:
    item = await session.get(Item, item_id)
    if not item:
        return None
    return ItemSchema.model_validate(item)


async def get_item_by_parents(
    session: AsyncSession, parent: ParentSchema
) -> ItemSchema | None:
    stmt = (
        select(Item)
        .join(Item.parents)
        .where(Parent.first == parent.first, Parent.second == parent.second)
    )
    result = (await session.execute(stmt)).scalar_one_or_none()
    if not result:
        return None
    return ItemSchema.model_validate(result)
