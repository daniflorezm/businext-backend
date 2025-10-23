from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select
from ..database.database import SessionDep
from ..database.models.reservation_model import (
    Reservation,
    ReservationPublic,
    ReservationBase,
    ReservationUpdate,
)
from src.api.auth import get_current_user

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[ReservationPublic])
def get_reservations(
    session: SessionDep,
    business_id: str = Depends(get_current_user),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    reservations = session.exec(
        select(Reservation)
        .where(Reservation.business_id == business_id)
        .offset(offset)
        .limit(limit)
    ).all()
    if not reservations:
        raise HTTPException(status_code=404, detail="No reservations found")
    return reservations


@router.get("/{reservation_id}", response_model=ReservationPublic)
def get_reservation_by_id(
    reservation_id: int,
    session: SessionDep,
    business_id: str = Depends(get_current_user),
):
    reservation = session.get(Reservation, reservation_id)
    if not reservation or reservation.business_id != business_id:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


@router.post("/", response_model=ReservationPublic)
def create_reservation(
    reservation: ReservationBase,
    session: SessionDep,
    business_id: str = Depends(get_current_user),
):
    reservation_data = reservation.model_dump()
    reservation_data["business_id"] = business_id
    reservation_obj = Reservation(**reservation_data)
    session.add(reservation_obj)
    session.commit()
    session.refresh(reservation_obj)
    return reservation_obj


@router.patch("/{reservation_id}", response_model=ReservationPublic)
def update_reservation(
    reservation_id: int,
    reservation: ReservationUpdate,
    session: SessionDep,
    business_id: str = Depends(get_current_user),
):
    reservation_db = session.get(Reservation, reservation_id)
    if not reservation_db or reservation_db.business_id != business_id:
        raise HTTPException(status_code=404, detail="Reservation not found")
    reservation_data = reservation.model_dump(exclude_unset=True)
    reservation_db.sqlmodel_update(reservation_data)
    session.add(reservation_db)
    session.commit()
    session.refresh(reservation_db)
    return reservation_db


@router.delete("/{reservation_id}")
def delete_reservation(
    reservation_id: int,
    session: SessionDep,
    business_id: str = Depends(get_current_user),
):
    reservation = session.get(Reservation, reservation_id)
    if not reservation or reservation.business_id != business_id:
        raise HTTPException(status_code=404, detail="Reservation not found")
    session.delete(reservation)
    session.commit()
    return {"Reservation deleted": True}
