import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import and_, func, case
from sqlmodel import select
from ..database.database import SessionDep
from ..database.models.finances_model import (
    Finances,
    FinancesPublic,
    FinancesBase,
    FinancesUpdate,
)
from src.api.auth import AuthContext, require_manager_or_owner, require_subscription


router = APIRouter(
    prefix="/finances",
    tags=["finances"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[FinancesPublic])
def get_finances(
    session: SessionDep,
    auth: AuthContext = Depends(require_manager_or_owner),
):
    finances = session.exec(
        select(Finances).where(Finances.business_id == auth.business_id)
    ).all()
    if not finances:
        raise HTTPException(status_code=404, detail="No finances found")
    return finances


@router.get("/{finances_id}", response_model=FinancesPublic)
def get_finances_by_id(
    finances_id: int, session: SessionDep, auth: AuthContext = Depends(require_manager_or_owner)
):
    finances = session.get(Finances, finances_id)
    if not finances or finances.business_id != auth.business_id:
        raise HTTPException(status_code=404, detail="Finances not found")
    return finances


@router.get("/annual_finances/{year}")
def get_annual_finances(
    session: SessionDep, year: int, auth: AuthContext = Depends(require_manager_or_owner)
):
    start = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)

    rows = session.exec(
        select(
            func.extract("month", Finances.created_at).label("month"),
            func.sum(
                case((Finances.type == "INCOME", Finances.amount), else_=0)
            ).label("incomes"),
            func.sum(
                case((Finances.type == "EXPENSE", Finances.amount), else_=0)
            ).label("expenses"),
        ).where(
            and_(
                Finances.created_at >= start,
                Finances.created_at <= end,
                Finances.business_id == auth.business_id,
            )
        ).group_by(func.extract("month", Finances.created_at))
    ).all()

    totals = {int(row.month): (row.incomes or 0, row.expenses or 0) for row in rows}

    return [
        {
            "month": month,
            "balance": totals.get(month, (0, 0))[0] - totals.get(month, (0, 0))[1],
        }
        for month in range(1, 13)
    ]


@router.post("/", response_model=FinancesPublic)
def create_finances(
    finances: FinancesBase,
    session: SessionDep,
    auth: AuthContext = Depends(require_subscription),
):
    finances_data = finances.model_dump()
    finances_data["business_id"] = auth.business_id
    finances_obj = Finances(**finances_data)
    session.add(finances_obj)
    session.commit()
    session.refresh(finances_obj)
    return finances_obj


@router.patch("/{finances_id}", response_model=FinancesPublic)
def update_finances(
    finances_id: int,
    finances: FinancesUpdate,
    session: SessionDep,
    auth: AuthContext = Depends(require_manager_or_owner),
):
    finances_db = session.get(Finances, finances_id)
    if not finances_db or finances_db.business_id != auth.business_id:
        raise HTTPException(status_code=404, detail="Finances not found")
    finances_data = finances.model_dump(exclude_unset=True)
    finances_db.sqlmodel_update(finances_data)
    session.add(finances_db)
    session.commit()
    session.refresh(finances_db)
    return finances_db


@router.delete("/{finances_id}", response_model=dict)
def delete_finances(
    finances_id: int, session: SessionDep, auth: AuthContext = Depends(require_manager_or_owner)
):
    finances_db = session.get(Finances, finances_id)
    if not finances_db or finances_db.business_id != auth.business_id:
        raise HTTPException(status_code=404, detail="Finances not found")
    if finances_db.reservation_id is not None:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar un registro vinculado a una reserva. Revierte la reserva primero.",
        )
    session.delete(finances_db)
    session.commit()
    return {"Finances record deleted": True}
