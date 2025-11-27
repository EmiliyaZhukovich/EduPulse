from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from core.database import engine, Base
from core.config import settings
from app.api import auth, curator, admin, reports, surveys
from services.auth_service import init_keycloak_auth

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    # Initialize Keycloak authentication
    init_keycloak_auth(
        settings.keycloak_url,
        settings.keycloak_realm,
        settings.keycloak_client_id
    )

    yield

app = FastAPI(
    title="Social-Psychological Monitoring System",
    description="Anonymous survey system for university social-psychological monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(curator.router, prefix="/api/curator", tags=["curator"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(surveys.router, prefix="/api/surveys", tags=["surveys"])

@app.get("/")
async def root():
    return {"message": "Social-Psychological Monitoring System API", "version": "1.0.0"}

@app.get("/api/health")
async def health():
    return {"status": "ok"}
