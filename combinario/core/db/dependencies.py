from typing import Annotated, AsyncGenerator
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.repositories.item import ItemRepository


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_repository(session: SessionDep) -> ItemRepository:
    return ItemRepository(session=session)


ItemRepoDep = Annotated[ItemRepository, Depends(get_repository)]
