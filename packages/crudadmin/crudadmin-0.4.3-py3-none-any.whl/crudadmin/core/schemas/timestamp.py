from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field, field_serializer

UTC = timezone.utc


class TimestampSchema(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = Field(default=None)

    @field_serializer("created_at")
    def serialize_dt(self, created_at: Optional[datetime], _info: Any) -> Optional[str]:
        if created_at is not None:
            return created_at.isoformat()
        return None

    @field_serializer("updated_at")
    def serialize_updated_at(
        self, updated_at: Optional[datetime], _info: Any
    ) -> Optional[str]:
        if updated_at is not None:
            return updated_at.isoformat()
        return None
