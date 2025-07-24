from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    # Add any product-specific methods here, e.g., find_by_name
    def find_by_name(self, db: Session, name: str) -> Optional[Product]:
        return db.query(self.model).filter(self.model.name == name).first()
    

product = CRUDProduct(Product)