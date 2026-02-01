from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1 import events, photos, me
from app.websockets import notifications
import os

app = FastAPI(
    title="IMG Project API",
    description="FastAPI application for image management",
    version="1.0.0",
)

# Create media directory if it doesn't exist
os.makedirs("media", exist_ok=True)

# Mount static files
app.mount("/media", StaticFiles(directory="media"), name="media")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events.router, prefix="/api/v1")
app.include_router(photos.router, prefix="/api/v1")
app.include_router(me.router, prefix="/api/v1")

# Include WebSocket routes
app.include_router(notifications.router)
from app.api.v1 import auth
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "IMG Project API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

