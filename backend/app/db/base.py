"""
SQLAlchemy declarative base and base model configuration.
"""

from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy naming convention for constraints
# This helps with migrations and constraint naming
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

# SQLAlchemy declarative base
Base = declarative_base(metadata=metadata) 