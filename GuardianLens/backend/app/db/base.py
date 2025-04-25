# Import all models here to ensure they are registered with Base
# This allows Alembic to detect them
from app.db.base_class import Base
from app.models.user import ParentUser # Example: uncomment when models exist
from app.models.profile import ChildProfile # Import ChildProfile for Alembic migrations
from app.models.linked_account import LinkedAccount # Import LinkedAccount for Alembic migrations