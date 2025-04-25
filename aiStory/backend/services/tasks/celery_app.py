"""Celery application configuration for async tasks."""
import os
from celery import Celery

# Configure Celery app
celery_app = Celery(
    "ai_story",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["backend.services.tasks.ai_processing_tasks"]
)

# Configure Celery settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_concurrency=os.environ.get("CELERY_CONCURRENCY", 2),
)

# This allows importing this file from other modules
if __name__ == "__main__":
    celery_app.start()