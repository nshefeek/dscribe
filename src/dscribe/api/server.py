from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

api = FastAPI(
    title="dScribe",
    description="Welcome to dScribe's API documentation! Here you will able to discover all of the ways you can interact with the dScribe API.",
    root_path="/api/v1",
    docs_url=None,
    openapi_url="/docs/openapi.json",
    redoc_url="/docs",
)
api.add_middleware(GZipMiddleware, minimum_size=1000)