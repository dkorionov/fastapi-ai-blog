from core.config import CORSSettings
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


def setup_middlewares(
        *,
        app: FastAPI,
        settings: CORSSettings,
) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGIN,
        allow_credentials=settings.ALLOW_CREDENTIALS,
        allow_methods=settings.ALLOW_METHODS,
        allow_headers=settings.ALLOW_HEADERS,
    )
