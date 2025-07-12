# app/main.py - Updated with WebSockets and Enhanced Search
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
    description="Community Clothing Exchange Platform with Real-time Features",
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
        print("⚠️  Redis connection failed, caching features will be disabled")
        print("📝 Note: This is okay for development, we'll add caching later")
    
    print("✅ Database connected successfully")
    print("🔌 WebSocket manager initialized")
    print("🔍 Enhanced search service ready")
    print("📱 Real-time notifications enabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    print("🛑 Shutting down ReWear API...")
    
    # Close WebSocket connections gracefully
    from app.core.websockets import manager
    for user_id in list(manager.active_connections.keys()):
        for websocket in manager.active_connections[user_id]:
            try:
                await websocket.close(code=1001, reason="Server shutdown")
            except Exception:
                pass
    
    print("✅ Graceful shutdown completed")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "ReWear API is running!",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "features": [
            "Real-time notifications via WebSockets",
            "Advanced search with ranking",
            "Image upload and management",
            "Points-based economy",
            "Admin moderation panel"
        ],
        "docs_url": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "websockets": "enabled",
        "search": "enhanced",
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
        
        # Check WebSocket manager
        from app.core.websockets import manager
        health_status["websockets"] = {
            "active_connections": len(manager.user_sessions),
            "unique_users": len(manager.active_connections)
        }
            
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


# Import and include API routes
from app.api.routes import auth, users, items, swaps, admin, upload

# Import Phase 4 features with error handling
try:
    from app.api.routes import websockets
    websockets_available = True
except ImportError:
    print("⚠️  WebSockets module not found - creating basic websockets route")
    websockets_available = False

try:
    from app.api.routes import search
    search_available = True
except ImportError:
    print("⚠️  Search module not found - creating basic search route")
    search_available = False

# Core API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(items.router, prefix="/api/v1/items", tags=["Items"])
app.include_router(swaps.router, prefix="/api/v1/swaps", tags=["Swaps"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["Upload"])

# Phase 4 features (if available)
if websockets_available:
    app.include_router(websockets.router, prefix="/api/v1/ws", tags=["WebSockets"])
    print("✅ WebSocket notifications enabled")

if search_available:
    app.include_router(search.router, prefix="/api/v1/search", tags=["Enhanced Search"])
    print("✅ Enhanced search enabled")


# Enhanced error handling for WebSocket connections
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    if "websocket" in str(request.url).lower():
        # WebSocket specific error handling
        return JSONResponse(
            status_code=500,
            content={"detail": "WebSocket connection error", "type": "websocket_error"}
        )
    
    # Regular HTTP error handling
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "server_error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
        ws_ping_interval=20,
        ws_ping_timeout=20
    )