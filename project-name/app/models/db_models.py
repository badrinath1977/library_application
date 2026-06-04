from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class SampleDBModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CustomerDBModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
