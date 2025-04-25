from celery import Celery
from app.config import settings

# Initialize Celery
celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"] # Point to where tasks will be defined
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Add other Celery settings if needed
)

# Example placeholder task module structure
# Create an empty app/tasks/__init__.py and app/tasks/example.py later