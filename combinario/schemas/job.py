from pydantic import BaseModel, Field


class JobSchema(BaseModel):
    enqueued: str = Field(..., min_length=1)
