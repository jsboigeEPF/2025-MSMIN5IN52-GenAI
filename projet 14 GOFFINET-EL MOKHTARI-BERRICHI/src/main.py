from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.routers.route_agent import router

app = FastAPI(
    title="Structured Content Generator",
    description="API for generating structured documents (CVs, Invoices, Reports) in PDF format",
    version="1.0.0",
)

# ✅ Middleware pour limiter la taille des requêtes (20 Mo ici)
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    body = await request.body()
    max_size = 20 * 1024 * 1024  # 20 Mo
    size = len(body)
    if size > max_size:
        print(f"❌ Requête trop volumineuse ({size / 1024 / 1024:.2f} Mo)")
        return JSONResponse(
            status_code=413,
            content={"error": f"Requête trop volumineuse : {size / 1024 / 1024:.2f} Mo (max {max_size / 1024 / 1024:.0f} Mo)"}
        )
    # 🔎 Log facultatif
    print(f"✅ Requête reçue ({size / 1024:.1f} Ko)")
    request._body = body  # remettre le corps dans la requête pour le reste de FastAPI
    return await call_next(request)

# 🌐 CORS (pour ton frontend React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Routes de ton application
app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
