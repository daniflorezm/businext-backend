from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime


class ProductBase(SQLModel):
    name: str
    price: float


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProductPublic(ProductBase):
    id: int


class ProductUpdate(ProductBase):
    name: Optional[str] = None
    price: Optional[float] = None
