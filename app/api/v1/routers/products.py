from typing import List
from fastapi import APIRouter, Depends, Query
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.api import deps
from app.services.product_service import ProductService

router = APIRouter()

@router.post("/", response_model=Product, status_code=201)
def create_product(product_in: ProductCreate, service: ProductService = Depends(deps.get_product_service)):
    return service.create_product(product=product_in)

@router.get("/", response_model=List[Product])
def read_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of products to return"),
    service: ProductService = Depends(deps.get_product_service)
):
    return service.get_all_products(skip=skip, limit=limit)

@router.get("/{product_id}", response_model=Product)
def read_product(product_id: int, service: ProductService = Depends(deps.get_product_service)):
    return service.get_product_by_id(product_id=product_id)

@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, product_in: ProductUpdate, service: ProductService = Depends(deps.get_product_service)):
    return service.update_product(product_id=product_id, product_update=product_in)

@router.delete("/{product_id}", response_model=Product)
def delete_product(product_id: int, service: ProductService = Depends(deps.get_product_service)):
    return service.delete_product(product_id=product_id)