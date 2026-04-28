from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from ..database.database import SessionDep
from ..database.models.working_hours_model import (
    WorkingHours,
    WorkingHoursPublic,
    WorkingHoursBase,
)
from src.api.auth import AuthContext, require_active_member, require_owner

router = APIRouter(
    prefix="/working-hours",
    tags=["working-hours"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[WorkingHoursPublic])
def get_working_hours(
    session: SessionDep,
    auth: AuthContext = Depends(require_active_member),
):
    hours = session.exec(
        select(WorkingHours)
        .where(WorkingHours.business_id == auth.business_id)
        .order_by(WorkingHours.day_of_week)
    ).all()
    return hours


@router.put("/", response_model=list[WorkingHoursPublic])
def upsert_working_hours(
    entries: list[WorkingHoursBase],
    session: SessionDep,
    auth: AuthContext = Depends(require_owner),
):
    # Validate entries
    seen_days: set[int] = set()
    for entry in entries:
        if entry.day_of_week < 0 or entry.day_of_week > 6:
            raise HTTPException(
                status_code=422,
                detail=f"day_of_week must be 0-6, got {entry.day_of_week}",
            )
        if entry.day_of_week in seen_days:
            raise HTTPException(
                status_code=422,
                detail=f"Duplicate day_of_week: {entry.day_of_week}",
            )
        seen_days.add(entry.day_of_week)
        if entry.enabled and entry.start_time >= entry.end_time:
            raise HTTPException(
                status_code=422,
                detail=f"start_time must be before end_time for day {entry.day_of_week}",
            )

    # Upsert each entry
    for entry in entries:
        existing = session.exec(
            select(WorkingHours).where(
                WorkingHours.business_id == auth.business_id,
                WorkingHours.day_of_week == entry.day_of_week,
            )
        ).first()

        if existing:
            existing.start_time = entry.start_time
            existing.end_time = entry.end_time
            existing.enabled = entry.enabled
            session.add(existing)
        else:
            data = entry.model_dump()
            data["business_id"] = auth.business_id
            new_entry = WorkingHours(**data)
            session.add(new_entry)

    session.commit()

    # Return updated list
    hours = session.exec(
        select(WorkingHours)
        .where(WorkingHours.business_id == auth.business_id)
        .order_by(WorkingHours.day_of_week)
    ).all()
    return hours
