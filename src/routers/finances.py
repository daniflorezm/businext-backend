import calendar
import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import and_
from sqlmodel import select
from ..database.database import SessionDep
from ..database.models.finances_model import (
    Finances,
    FinancesPublic,
    FinancesBase,
    FinancesUpdate,
)
from src.api.auth import get_current_user


router = APIRouter(
    prefix="/finances",
    tags=["finances"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[FinancesPublic])
def get_finances(
    session: SessionDep,
    business_id: str = Depends(get_current_user),
):
    finances = session.exec(
        select(Finances).where(Finances.business_id == business_id)
    ).all()
    if not finances:
        raise HTTPException(status_code=404, detail="No finances found")
    return finances


@router.get("/{finances_id}", response_model=FinancesPublic)
def get_finances_by_id(
    finances_id: int, session: SessionDep, business_id: str = Depends(get_current_user)
):
    finances = session.get(Finances, finances_id)
    if not finances or finances.business_id != business_id:
        raise HTTPException(status_code=404, detail="Finances not found")
    return finances


@router.get("/anual_finances/{year}")
def get_monthly_finances(
    session: SessionDep, year: int, business_id: str = Depends(get_current_user)
):
    balances = []
    for month in range(1, 13):
        num_days = calendar.monthrange(year, month)[1]
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, num_days)

        registers_by_month = session.exec(
            select(Finances).filter(
                and_(
                    Finances.created_at >= start_date,
                    Finances.created_at <= end_date,
                    Finances.business_id == business_id,
                )
            )
        ).all()
        incomes = sum(
            register.amount
            for register in registers_by_month
            if register.type == "INCOME"
        )
        expenses = sum(
            register.amount
            for register in registers_by_month
            if register.type == "EXPENSE"
        )

        balance = incomes - expenses
        balances.append({"month": month, "balance": balance})

    return balances


@router.post("/", response_model=FinancesPublic)
def create_finances(
    finances: FinancesBase,
    session: SessionDep,
    business_id: str = Depends(get_current_user),
):
    finances_data = finances.model_dump()
    finances_data["business_id"] = business_id
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
    business_id: str = Depends(get_current_user),
):
    finances_db = session.get(Finances, finances_id)
    if not finances_db or finances_db.business_id != business_id:
        raise HTTPException(status_code=404, detail="Finances not found")
    finances_data = finances.model_dump(exclude_unset=True)
    finances_db.sqlmodel_update(finances_data)
    session.add(finances_db)
    session.commit()
    session.refresh(finances_db)
    return finances_db


@router.delete("/{finances_id}", response_model=dict)
def delete_finances(
    finances_id: int, session: SessionDep, business_id: str = Depends(get_current_user)
):
    finances_db = session.get(Finances, finances_id)
    if not finances_db or finances_db.business_id != business_id:
        raise HTTPException(status_code=404, detail="Finances not found")
    session.delete(finances_db)
    session.commit()
    return {"Finances record deleted": True}
