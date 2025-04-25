from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

# Optional: Define naming convention for constraints
# Helps keep migration names consistent
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

class Base(DeclarativeBase):
    metadata = metadata
    # You can add common columns or methods here if needed later
    # e.g., id: Mapped[int] = mapped_column(primary_key=True)