import logging
from typing import Any

from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from schemas.item import ItemSchema
from schemas.parent import ParentSchema

from core.db.repositories.item import ItemRepository

from core.llm.model import OpenAI

from core.db.settings import db_settings
from core.llm.settings import llm_settings
from core.redis.settings import redis_settings

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_task(
    ctx: dict[str, Any],
    prompt: str,
    first: int,
    second: int,
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
        repository = ItemRepository(session)
        item.id = await repository.add_item(
            emoji=item.emoji, text=item.text, parents=[(first, second)]
        )

    return item


async def startup(ctx: dict[str, Any]) -> None:
    engine = create_async_engine(str(db_settings.db_url), echo=db_settings.debug_mode)
    ctx["engine"] = engine
    ctx["session_factory"] = async_sessionmaker(engine, expire_on_commit=False)
    ctx["openai_client"] = OpenAI(
        base_url=llm_settings.llm_base_url,
        api_key=llm_settings.open_ai_api_key,
        max_tokens=llm_settings.max_tokens,
        temperature=llm_settings.model_temperature,
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
        host=redis_settings.redis_host,
        port=redis_settings.redis_port,
    )
