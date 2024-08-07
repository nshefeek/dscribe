from os import path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from dscribe.core.config import Settings
from dscribe.api.routes import api_router
from dscribe.webrtc.routes import webrtc_router


settings = Settings()
    
app = FastAPI(openapi_url="")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: Exception):
    if settings.STATIC_DIR and not request.url.path.startswith(("/api", "/ws")):
        return FileResponse(path.join(settings.STATIC_DIR, "index.html"))
    return JSONResponse(status_code=404, content={"message": "Not Found"})

frontend = FastAPI(root_path="")
frontend.add_middleware(GZipMiddleware, minimum_size=1000)

# class DefaultPageMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next: Any) -> Any:
#         response = await call_next(request)
#         if response.status_code == 404:
#             if settings.STATIC_DIR:
#                 return FileResponse(path.join(settings.STATIC_DIR, "index.html"))
#         return response

if settings.STATIC_DIR and path.isdir(settings.STATIC_DIR):
    frontend.mount("/", StaticFiles(directory=settings.STATIC_DIR), name="app")
        
@frontend.middleware("http")
async def default_page(request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        if settings.STATIC_DIR:
            return FileResponse(path.join(settings.STATIC_DIR, "index.html"))
    return response

api = FastAPI(
    title="dScribe",
    description="Welcome to dScribe's API documentation! Here you will able to discover all of the ways you can interact with the dScribe API.",
    root_path="/api/v1",
    docs_url=None,
    openapi_url="/docs/openapi.json",
    redoc_url="/docs",
)
api.add_middleware(GZipMiddleware, minimum_size=1000)
api.include_router(api_router)

app.include_router(webrtc_router)

app.mount("/api/v1", app=api)
app.mount("/", app=frontend)
