from os import path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.types import ASGIApp, Receive, Scope, Send

from dscribe.core.config import Settings
from dscribe.api.server import api
from dscribe.webrtc.routes import webrtc_app


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

if settings.STATIC_DIR and path.isdir(settings.STATIC_DIR):
    frontend.mount("/", StaticFiles(directory=settings.STATIC_DIR), name="frontend")


class HTTPMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> Any:
        if scope["type"] == "http":
            request = Request(scope, receive=receive)
            response = await self.app(scope, receive, send)
            if response.status_code == 404:
                if settings.STATIC_DIR:
                    return await FileResponse(path.join(settings.STATIC_DIR, "index.html"))(scope, receive, send)
            return await response(scope, receive, send)
        await self.app(scope, receive, send)

frontend.add_middleware(HTTPMiddleware)

# @frontend.middleware("http")
# async def default_page(request, call_next):
#     response = await call_next(request)
#     if response.status_code == 404:
#         if settings.STATIC_DIR:
#             return FileResponse(path.join(settings.STATIC_DIR, "index.html"))
#     return response

app.mount("", app=frontend)
app.mount("/api/v1", app=api)
app.mount("/ws", app=webrtc_app)