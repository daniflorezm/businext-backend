from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from ..database.database import SessionDep
from ..database.models.product_model import (
    Product,
    ProductPublic,
    ProductBase,
    ProductUpdate,
)
from src.api.auth import get_current_user

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[ProductPublic])
def get_products(
    session: SessionDep,
    business_id: str = Depends(get_current_user),
):
    products = session.exec(
        select(Product).where(Product.business_id == business_id)
    ).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    return products


@router.get("/{product_id}", response_model=ProductPublic)
def get_product_by_id(
    product_id: int, session: SessionDep, business_id: str = Depends(get_current_user)
):
    product = session.get(Product, product_id)
    if not product or product.business_id != business_id:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductPublic)
def create_product(
    product: ProductBase,
    session: SessionDep,
    business_id: str = Depends(get_current_user),
):
    product_data = product.model_dump()
    product_data["business_id"] = business_id
    product_obj = Product(**product_data)
    session.add(product_obj)
    session.commit()
    session.refresh(product_obj)
    return product_obj


@router.patch("/{product_id}", response_model=ProductPublic)
def update_product(
    product_id: int,
    product: ProductUpdate,
    session: SessionDep,
    business_id: str = Depends(get_current_user),
):
    product_db = session.get(Product, product_id)
    if not product_db or product_db.business_id != business_id:
        raise HTTPException(status_code=404, detail="Product not found")
    product_data = product.model_dump(exclude_unset=True)
    product_db.sqlmodel_update(product_data)
    session.add(product_db)
    session.commit()
    session.refresh(product_db)
    return product_db


@router.delete("/{product_id}")
def delete_product(
    product_id: int, session: SessionDep, business_id: str = Depends(get_current_user)
):
    product = session.get(Product, product_id)
    if not product or product.business_id != business_id:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return {"Product deleted": True}
