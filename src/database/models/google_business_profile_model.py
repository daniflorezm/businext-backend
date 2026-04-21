from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime


class GoogleBusinessProfileBase(SQLModel):
    source_url: str
    google_id: str


class GoogleBusinessProfile(GoogleBusinessProfileBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_id: str = Field(index=True, nullable=False)
    name: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    phone: Optional[str] = None
    rating: Optional[float] = None
    total_reviews: int = Field(default=0)
    reviews_per_score: Optional[str] = None  # JSON string: {"1": 5, "2": 3, ...}
    location_link: Optional[str] = None
    validation_status: str = Field(default="pending")  # "pending" | "locked"
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    last_review_timestamp: int = Field(default=0)
    ai_summary: Optional[str] = None  # JSON string
    ai_summary_generated_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GoogleBusinessProfilePublic(GoogleBusinessProfileBase):
    id: int
    name: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    phone: Optional[str] = None
    rating: Optional[float] = None
    total_reviews: int = 0
    reviews_per_score: Optional[str] = None
    location_link: Optional[str] = None
    validation_status: str = "pending"
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    last_review_timestamp: int = 0
    ai_summary: Optional[str] = None
    ai_summary_generated_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GoogleBusinessProfileUpdate(SQLModel):
    validation_status: Optional[str] = None
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    ai_summary: Optional[str] = None
    ai_summary_generated_at: Optional[datetime] = None
