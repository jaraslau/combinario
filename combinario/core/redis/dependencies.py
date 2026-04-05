from typing import Annotated
from fastapi import Request, Depends
from arq.connections import ArqRedis


async def get_arq(request: Request) -> ArqRedis:
    return request.app.state.arq_pool


RedisDep = Annotated[ArqRedis, Depends(get_arq)]
