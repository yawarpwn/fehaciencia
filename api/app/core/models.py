from datetime import datetime
from sqlmodel import Field, SQLModel
from app.core.utils import utc_now


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime | None = Field(default=None)
