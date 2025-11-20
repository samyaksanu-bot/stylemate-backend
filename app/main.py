from fastapi import FastAPI
from app.api.v1.upload import router as upload_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.auth import router as auth_router
from app.tasks.cleanup import start_scheduler

app = FastAPI(title="Stylemate Backend")

# Register API routes
app.include_router(upload_router, prefix="/api/v1/upload", tags=["upload"])
app.include_router(recommendations_router, prefix="/api/v1/recommendations", tags=["recommendations"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

@app.on_event("startup")
def startup():
    # Start scheduled cleanup job
    start_scheduler()

@app.get("/")
def root():
    return {"message": "Stylemate backend is working"}

