from pydantic import BaseModel, ConfigDict, Field, model_validator


class ParentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first: int = Field(..., ge=1)
    second: int = Field(..., ge=1)
    item_id: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def normalize(self) -> "ParentSchema":
        if self.first > self.second:
            self.first, self.second = self.second, self.first
        return self
