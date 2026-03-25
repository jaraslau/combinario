import asyncio
import logging
import os
from typing import TypedDict

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from db import repository
from schemas import ItemSchema

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseElement(TypedDict):
    id: int
    emoji: str
    text: str


BASE_ELEMENTS: list[BaseElement] = [
    {"id": 1, "emoji": "💧", "text": "Water"},
    {"id": 2, "emoji": "🔥", "text": "Fire"},
    {"id": 3, "emoji": "🌍", "text": "Earth"},
    {"id": 4, "emoji": "🌬️", "text": "Wind"},
]


async def prepopulate() -> None:
    db_url = os.getenv("DB_URL")
    if not db_url:
        logger.error("Could not find DB_URL in env")
        raise ValueError("DB_URL is not set")

    logger.info(f"Prepopulating {db_url} with default elements.")

    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with session_factory() as session:
            for element in BASE_ELEMENTS:
                if not await repository.get_item(session, element["id"]):
                    item = ItemSchema(
                        id=element["id"],
                        emoji=element["emoji"],
                        text=element["text"],
                        parents=[],
                    )
                    item_id = await repository.add_item(session, item)
                    logger.info(f"Prepopulated with item {item_id}")
                else:
                    logger.info(f"Item {element['id']} already present, skipping")
    finally:
        await engine.dispose()

    logger.info("Finished")


if __name__ == "__main__":
    asyncio.run(prepopulate())
