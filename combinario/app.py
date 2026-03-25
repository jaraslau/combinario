import logging
import orjson
from arq import create_pool
from arq.jobs import Job, JobStatus
from arq.connections import RedisSettings, ArqRedis
from typing import AsyncGenerator, Union, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db import repository
from schemas import ItemSchema, ParentSchema, JobSchema
from config import settings


logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    engine = create_async_engine(settings.db_url, echo=settings.debug_mode)

    async with engine.begin() as conn:
        from db.tables import Base

        await conn.run_sync(Base.metadata.create_all)

    app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)

    redis_conn = RedisSettings(host=settings.redis_host, port=settings.redis_port)
    app.state.arq_pool: ArqRedis = await create_pool(redis_conn)  # type: ignore

    try:
        yield
    finally:
        await app.state.arq_pool.close()
        await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    json_loads=orjson.loads,
    default_response_class=ORJSONResponse,
    debug=settings.debug_mode,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.session_factory() as session:
        yield session


async def get_arq(request: Request) -> ArqRedis:
    return request.app.state.arq_pool


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/items/{first}/{second}", response_model=Union[ItemSchema, JobSchema])
async def fetch_item(
    first: int,
    second: int,
    session: AsyncSession = Depends(get_session),
    arq_pool: ArqRedis = Depends(get_arq),
) -> Union[ItemSchema, JobSchema]:
    if first < 1 or second < 1:
        raise HTTPException(status_code=422, detail="IDs must be >= 1")

    parent = ParentSchema(first=first, second=second)
    existing = await repository.get_item_by_parents(session, parent)
    if existing:
        return existing

    first_item = await repository.get_item(session, first)
    second_item = await repository.get_item(session, second)
    if not first_item or not second_item:
        raise HTTPException(status_code=404, detail="Item not found")

    prompt = f"{first_item.text} + {second_item.text}"
    job = await arq_pool.enqueue_job("generate_task", prompt, first, second)
    if not job:
        raise HTTPException(status_code=500, detail="Failed to enqueue job")

    return JobSchema(enqueued=job.job_id)


@app.get("/task/{job_id}")
async def fetch_task(
    job_id: str, arq_pool: ArqRedis = Depends(get_arq)
) -> dict[str, Any]:
    job = Job(job_id=job_id, redis=arq_pool)
    status = await job.status()

    if status == JobStatus.not_found:
        raise HTTPException(status_code=404, detail="Job not found")

    if status == JobStatus.complete:
        try:
            return {"status": "complete", "result": await job.result()}
        except Exception as e:
            logger.error("Failed to retrieve result for job %s: %s", job_id, e)
            raise HTTPException(status_code=500, detail="Job failed")

    return {"status": status.value}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
