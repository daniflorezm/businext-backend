from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime


class ReservationBase(SQLModel):
    customer_name: str
    in_charge: str | None
    reservation_start_date: datetime
    reservation_end_date: datetime
    time_per_reservation: int  # in minutes
    status: str
    service: str


class Reservation(ReservationBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReservationPublic(ReservationBase):
    id: int


class ReservationUpdate(ReservationBase):
    customer_name: Optional[str] = None
    in_charge: Optional[str] = None
    reservation_start_date: Optional[datetime] = None
    reservation_end_date: Optional[datetime] = None
    time_per_reservation: int  # in minutes
    status: Optional[str] = None
    service: Optional[str] = None
