from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.api.v1.api import api_router

# Import models to ensure they are registered with SQLAlchemy
from app.models import product  # noqa: F401

app = FastAPI(title=settings.PROJECT_NAME)

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Favicon route
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}