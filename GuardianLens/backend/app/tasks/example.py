from app.celery_app import celery_app

@celery_app.task
def add(x: int, y: int) -> int:
    """Simple task that adds two numbers."""
    return x + y

# You might add other example tasks here later