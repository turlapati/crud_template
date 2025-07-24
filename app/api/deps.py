import os
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.product_service import ProductService

# --- Implementation Switching Logic ---
CRUD_IMPL = os.getenv("CRUD_IMPL", "orm").lower()

if CRUD_IMPL == "template":
    # NOTE: Pydantic models might fail validation when returning dicts instead of ORM objects.
    # This implementation is for benchmarking purposes and may require adjustments in the router.
    from app.crud.template_crud_product import template_product as crud_product

    print("--- Using TEMPLATE SQL CRUD implementation ---")
else:
    from app.crud.crud_product import product as crud_product

    print("--- Using ORM CRUD implementation ---")
# -------------------------------------


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """
    Dependency provider for the ProductService.

    It injects the appropriate CRUD implementation (ORM or template)
    based on the CRUD_IMPL environment variable.
    """
    return ProductService(db_session=db, product_crud=crud_product)