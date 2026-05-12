from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models import Item, Parent
from core.db.exceptions import ItemDoesNotExistError


class ItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_item(
        self, emoji: str, text: str, parents: list[tuple[int, int]]
    ) -> int:
        try:
            item = Item(emoji=emoji, text=text)
            for first, second in parents:
                item.parents.append(Parent(first=first, second=second))
            self.session.add(item)
            await self.session.commit()
            await self.session.refresh(item, ["parents"])
        except IntegrityError:
            await self.session.rollback()
            item = await self.get_item_by_text(text=text)
            for first, second in parents:
                item.parents.append(Parent(first=first, second=second))
            await self.session.commit()
            await self.session.refresh(item, ["parents"])
        return item.id

    async def get_item_by_text(self, text: str) -> Item:
        stmt = select(Item).where(Item.text == text)
        result = (await self.session.execute(stmt)).scalar_one_or_none()
        if result is None:
            raise ItemDoesNotExistError("Item does not exist")
        return result

    async def get_item(self, item_id: int) -> Item | None:
        result = await self.session.get(Item, item_id)
        if result is None:
            raise ItemDoesNotExistError("Item does not exist")
        return result

    async def get_item_by_parents(self, first_id: int, second_id: int) -> Item | None:
        stmt = (
            select(Item)
            .join(Item.parents)
            .where(Parent.first == first_id, Parent.second == second_id)
        )
        result = (await self.session.execute(stmt)).scalar_one_or_none()
        if result is None:
            raise ItemDoesNotExistError("Item does not exist")
        return result
