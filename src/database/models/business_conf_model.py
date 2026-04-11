from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime


class BusinessConfigurationBase(SQLModel):
    business_name: str


class BusinessConfiguration(BusinessConfigurationBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_id: str = Field(index=True, nullable=False, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BusinessConfigurationPublic(BusinessConfigurationBase):
    id: int


class BusinessConfigurationUpdate(BusinessConfigurationBase):
    business_name: Optional[str] = None
