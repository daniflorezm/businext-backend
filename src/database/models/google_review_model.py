from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime


class GoogleReviewBase(SQLModel):
    review_id: str = Field(unique=True)
    author_title: Optional[str] = None
    author_image: Optional[str] = None
    review_text: Optional[str] = None
    review_rating: int
    review_timestamp: int
    review_datetime_utc: Optional[str] = None
    review_link: Optional[str] = None
    owner_answer: Optional[str] = None
    owner_answer_timestamp: Optional[int] = None


class GoogleReview(GoogleReviewBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_id: str = Field(index=True, nullable=False)
    profile_id: int = Field(foreign_key="googlebusinessprofile.id", nullable=False, index=True)
    ai_generated_response: Optional[str] = None
    ai_response_generated_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GoogleReviewPublic(GoogleReviewBase):
    id: int
    profile_id: int
    ai_generated_response: Optional[str] = None
    ai_response_generated_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GoogleReviewUpdate(SQLModel):
    ai_generated_response: Optional[str] = None
    ai_response_generated_at: Optional[datetime] = None
