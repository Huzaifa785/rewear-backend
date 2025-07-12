from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import test_db_connection, test_redis_connection
import os

# Create FastAPI app
app = FastAPI(
    title="ReWear API",
    description="Community Clothing Exchange Platform",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    print("🚀 Starting ReWear API...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    
    # Test connections
    db_status = test_db_connection()
    redis_status = test_redis_connection()
    
    if not db_status:
        raise HTTPException(status_code=500, detail="Database connection failed")
    if not redis_status:
        print("⚠️  Redis connection failed, some features may not work")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "ReWear API is running!",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "environment": settings.ENVIRONMENT
    }
    
    try:
        # Test database
        if not test_db_connection():
            health_status["database"] = "disconnected"
            health_status["status"] = "unhealthy"
        
        # Test Redis
        if not test_redis_connection():
            health_status["redis"] = "disconnected"
            # Redis is not critical, so don't mark as unhealthy
            
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


# Import and include API routes (we'll add these next)
# from app.api.routes import auth, users, items, admin
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(items.router, prefix="/api/v1/items", tags=["Items"])
# app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )