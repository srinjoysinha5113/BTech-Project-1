from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import health, auth, rsa, aes, kyber, messages, benchmarks
from app.models import User, Message, BenchmarkResult, Log

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Post-Quantum Secure Web API using Lattice-Based Cryptography",
    debug=settings.DEBUG
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(rsa.router, prefix="/api/v1/rsa", tags=["rsa"])
app.include_router(aes.router, prefix="/api/v1/aes", tags=["aes"])
app.include_router(kyber.router, prefix="/api/v1/kyber", tags=["kyber"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])
app.include_router(benchmarks.router, prefix="/api/v1/benchmarks", tags=["benchmarks"])

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "message": "Post-Quantum Secure API is operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
