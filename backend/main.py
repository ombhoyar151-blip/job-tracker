import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import get_settings
from core.database import engine, Base
from api.routes import routers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.upload_dir, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

origins = [
    o.strip() for o.strip() in settings.cors_origins.split(",") if o.strip()
] if settings.cors_origins != "*" else ["*"]

if "*" not in origins and "http://localhost:5173" not in origins:
    origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)

# Ensure uploads directory exists before StaticFiles tries to mount it
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/")
async def root():
    return {"message": "Welcome to Job Tracker API", "version": settings.app_version, "status": "ok"}


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.app_version}
