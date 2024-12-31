from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.db import init_db
from app.api.main import router
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=None,
)


@app.get("/")
async def root():
    return {"message": "Hello World"}



if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        
    )

app.include_router(router, prefix=settings.API_V1_STR)


from app.initial_data import main
main()