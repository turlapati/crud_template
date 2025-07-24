# app/db/base.py

from sqlalchemy.orm import declarative_base

# Create the Base class that all models will inherit from
Base = declarative_base()

# NOTE: Do not import models here to avoid circular imports.
# Models should be imported in the application startup or where needed.
# The models will be registered with Base when they are imported elsewhere.