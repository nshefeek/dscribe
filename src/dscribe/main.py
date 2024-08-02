import asyncio
import uvicorn
from os import path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse

from dscribe.core.config import Settings


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

frontend = FastAPI(openapi_url="")
frontend.add_middleware(GZipMiddleware, minimum_size=1000)


@frontend.middleware("http")
async def default_page(request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        if settings.STATIC_DIR:
            return FileResponse(path.join(settings.STATIC_DIR, "index.html"))
    return response

async def main():
    config = uvicorn.Config(app, port=8000, log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())