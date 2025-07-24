from fastapi import APIRouter
from .routers import products # Import the new router

api_router = APIRouter()
api_router.include_router(products.router, prefix="/products", tags=["products"])