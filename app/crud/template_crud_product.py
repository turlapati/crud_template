from app.crud.template_base import TemplateCRUDBase


class TemplateCRUDProduct(TemplateCRUDBase):
    # You can add product-specific raw SQL queries here if needed.
    pass


# The table name must match the __tablename__ defined in the Product model
# The Product model defines __tablename__ = "products"
template_product = TemplateCRUDProduct(table_name="products")
