from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers.route_agent import router

app = FastAPI(
    title="Structured Content Generator",
    description="API for generating structured documents (CVs, Invoices, Reports) in PDF format",
    version="1.0.0",
)

# Allow all CORS (for local frontend or tests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
