from fastapi import FastAPI
from app.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include API routers
from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)