from typing import Optional
from sqlmodel import Field, SQLModel, UniqueConstraint
from datetime import date, datetime


class WeeklySummaryBase(SQLModel):
    week_start: date
    week_end: date
    narrative: str
    kpis: str  # JSON string
    client_narrative: Optional[str] = None


class WeeklySummary(WeeklySummaryBase, table=True):
    __table_args__ = (
        UniqueConstraint("business_id", "week_start", name="uq_business_week"),
    )

    id: int | None = Field(default=None, primary_key=True)
    business_id: str = Field(index=True, nullable=False)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class WeeklySummaryPublic(WeeklySummaryBase):
    id: int
    business_id: str
    generated_at: datetime
