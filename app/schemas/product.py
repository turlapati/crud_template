# app/schemas/product.py
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

# Shared properties
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that name is not empty."""
        if not v or not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip()
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Validate that price is positive."""
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

# Properties to receive on item creation
class ProductCreate(ProductBase):
    pass

# Properties to receive on item update
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate that name is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip() if v else None
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        """Validate that price is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

# Properties to return to client
class Product(ProductBase):
    id: int
    # Use model_config instead of class Config for Pydantic v2
    model_config = ConfigDict(from_attributes=True)