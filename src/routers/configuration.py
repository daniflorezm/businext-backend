from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from ..database.database import SessionDep
from ..database.models.business_conf_model import (
    BusinessConfigurationPublic,
    BusinessConfiguration,
    BusinessConfigurationBase,
    BusinessConfigurationUpdate,
)
from src.api.auth import get_current_user


router = APIRouter(
    prefix="/configuration",
    tags=["configuration"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[BusinessConfigurationPublic])
def get_configuration(
    session: SessionDep, business_id: str = Depends(get_current_user)
):
    configuration = session.exec(
        select(BusinessConfiguration).where(
            BusinessConfiguration.business_id == business_id
        )
    ).all()
    if not configuration:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return configuration


@router.post("/", response_model=BusinessConfigurationPublic)
def create_configuration(
    configuration: BusinessConfigurationBase,
    session: SessionDep,
    business_id: str = Depends(get_current_user),
):
    configuration_data = configuration.model_dump()
    configuration_data["business_id"] = business_id
    config_obj = BusinessConfiguration(**configuration_data)
    session.add(config_obj)
    session.commit()
    session.refresh(config_obj)
    return config_obj


@router.patch("/{configuration_id}", response_model=BusinessConfigurationPublic)
def update_configuration(
    configuration_id: int,
    configuration: BusinessConfigurationUpdate,
    session: SessionDep,
    business_id: str = Depends(get_current_user),
):
    configuration_db = session.get(BusinessConfiguration, configuration_id)
    if not configuration_db or configuration_db.business_id != business_id:
        raise HTTPException(status_code=404, detail="Configuration not found")
    configuration_data = configuration.model_dump(exclude_unset=True)
    configuration_db.sqlmodel_update(configuration_data)
    session.add(configuration_db)
    session.commit()
    session.refresh(configuration_db)
    return configuration_db


@router.delete("/{configuration_id}")
def delete_configuration(
    configuration_id: int,
    session: SessionDep,
    business_id: str = Depends(get_current_user),
):
    configuration_db = session.get(BusinessConfiguration, configuration_id)
    if not configuration_db or configuration_db.business_id != business_id:
        raise HTTPException(status_code=404, detail="Configuration not found")
    session.delete(configuration_db)
    session.commit()
    return {"Configuration deleted": True}
