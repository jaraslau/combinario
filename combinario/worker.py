import logging
from typing import Any

from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from db import repository
from schemas import ItemSchema, ParentSchema
from models.model import OpenAI
from config import settings

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_task(
    ctx: dict[str, Any], prompt: str, first: int, second: int
) -> ItemSchema:
    openai_client = ctx["openai_client"]
    session_factory = ctx["session_factory"]

    logger.info(f"Generating {prompt}")
    result = await openai_client.generate(prompt)
    if not result:
        raise Exception("Empty LLM response")

    try:
        emoji, text = result.split(maxsplit=1)
    except ValueError:
        emoji = result[0]
        text = result[1:]

    item = ItemSchema(
        emoji=emoji, text=text, parents=[ParentSchema(first=first, second=second)]
    )

    async with session_factory() as session:
        item.id = await repository.add_item(session, item)

    return item


async def startup(ctx: dict[str, Any]) -> None:
    engine = create_async_engine(settings.db_url, echo=settings.debug_mode)
    ctx["engine"] = engine
    ctx["session_factory"] = async_sessionmaker(engine, expire_on_commit=False)
    ctx["openai_client"] = OpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.open_ai_api_key,
        max_tokens=settings.max_tokens,
        temperature=settings.model_temperature,
    )
    logger.info("ARQ worker started")


async def shutdown(ctx: dict[str, Any]) -> None:
    engine = ctx.get("engine")
    if engine:
        await engine.dispose()
    logger.info("ARQ worker shutdown")


class WorkerSettings:
    functions = [generate_task]
    on_startup = startup
    on_shutdown = shutdown

    redis_settings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
    )
