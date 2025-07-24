from typing import Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.crud.base import CRUDBase
from app.crud.template_base import TemplateCRUDBase
from app.schemas.product import ProductCreate, ProductUpdate

# Define a type hint for the CRUD object that can be either implementation
CRUDObject = Union[CRUDBase, TemplateCRUDBase]


class ProductService:
    def __init__(self, db_session: Session, product_crud: CRUDObject):
        self.db_session = db_session
        self.product_crud = product_crud

    def get_product_by_id(self, product_id: int):
        db_product = self.product_crud.get(self.db_session, id=product_id)
        if db_product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return db_product

    def get_all_products(self, skip: int, limit: int):
        return self.product_crud.get_multi(self.db_session, skip=skip, limit=limit)

    def create_product(self, product: ProductCreate):
        try:
            if isinstance(self.product_crud, TemplateCRUDBase):
                # The template implementation expects a dictionary
                obj_in_data = product.model_dump(exclude_unset=True)
                return self.product_crud.create(self.db_session, obj_in=obj_in_data)
            else:
                # The ORM implementation expects the Pydantic model directly
                return self.product_crud.create(self.db_session, obj_in=product)
        except IntegrityError as e:
            # Handle database constraint violations (e.g., unique constraints)
            if "UNIQUE constraint failed" in str(e) or "already exists" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with name '{product.name}' already exists"
                )
            else:
                # Re-raise other integrity errors
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Database constraint violation"
                )

    def update_product(self, product_id: int, product_update: ProductUpdate):
        # Ensure the object exists first (also handles the 404 case)
        db_obj = self.get_product_by_id(product_id)

        try:
            if isinstance(self.product_crud, TemplateCRUDBase):
                # The template implementation expects a dictionary of update values
                update_data = product_update.model_dump(exclude_unset=True)
                return self.product_crud.update(self.db_session, id=product_id, obj_in=update_data)
            else:
                # The ORM implementation expects the Pydantic model for the update data
                return self.product_crud.update(self.db_session, db_obj=db_obj, obj_in=product_update)
        except IntegrityError as e:
            # Rollback the session to prevent PendingRollbackError
            self.db_session.rollback()
            
            # Handle database constraint violations
            if "NOT NULL constraint failed" in str(e):
                # Extract the field name from the error message
                # SQLite format: "NOT NULL constraint failed: products.field_name"
                error_str = str(e)
                field_name = "field"
                
                # Try to extract field name from error message
                if "products." in error_str:
                    try:
                        # Find the part after "products." and before any space or special character
                        start_idx = error_str.find("products.") + len("products.")
                        remaining = error_str[start_idx:]
                        # Extract field name (stop at first non-alphanumeric character except underscore)
                        field_name = ""
                        for char in remaining:
                            if char.isalnum() or char == "_":
                                field_name += char
                            else:
                                break
                        if not field_name:
                            field_name = "field"
                    except Exception:
                        field_name = "field"
                
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Required field '{field_name}' cannot be null or empty"
                )
            elif "UNIQUE constraint failed" in str(e) or "already exists" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product with this name already exists"
                )
            else:
                # Re-raise other integrity errors
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Database constraint violation"
                )

    def delete_product(self, product_id: int):
        # Ensure the object exists first (also handles the 404 case)
        self.get_product_by_id(product_id)
        return self.product_crud.remove(self.db_session, id=product_id)