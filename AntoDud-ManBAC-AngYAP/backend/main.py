from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import story, image, health
from app.config import settings
import uvicorn

app = FastAPI(
    title="Interactive Story Generator API",
    description="API for generating interactive stories with images",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(story.router, prefix="/api/v1", tags=["story"])
app.include_router(image.router, prefix="/api/v1", tags=["image"])

@app.get("/")
async def root():
    return {"message": "Interactive Story Generator API is running"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )