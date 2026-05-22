from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import health, auth, rsa, aes, kyber, messages
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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize database tables on startup.
    In production, use Alembic migrations instead.
    """
    # Import models here to ensure they are registered with Base
    # Models are already imported at module level
    # Base.metadata.create_all(bind=engine)
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on application shutdown.
    """
    pass


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(rsa.router, prefix="/api/v1/rsa", tags=["rsa"])
app.include_router(aes.router, prefix="/api/v1/aes", tags=["aes"])
app.include_router(kyber.router, prefix="/api/v1/kyber", tags=["kyber"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "message": "Post-Quantum Secure API is operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
