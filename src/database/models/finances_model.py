from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime


class FinancesBase(SQLModel):
    concept: str
    amount: float
    type: str
    creator: str


class Finances(FinancesBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FinancesPublic(FinancesBase):
    id: int
    created_at: datetime


class FinancesUpdate(FinancesBase):
    concept: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    creator: Optional[str] = None
