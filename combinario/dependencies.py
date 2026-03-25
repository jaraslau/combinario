from typing import Annotated, AsyncGenerator
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from arq.connections import ArqRedis


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.session_factory() as session:
        yield session


async def get_arq(request: Request) -> ArqRedis:
    return request.app.state.arq_pool


SessionDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[ArqRedis, Depends(get_arq)]
