import logging
from typing import Any

import msgspec
from core.config import create_settings
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from services import errors

from web.api import v1_api_router
from web.middlewares import setup_middlewares

logger = logging.getLogger(__name__)


class MsgSpecJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return msgspec.json.encode(content)


def create_app() -> FastAPI:
    app: FastAPI = FastAPI(
        title="FastAPI test project",
        description="FastAPI test project",
        version="1.0.0",
        default_response_class=MsgSpecJSONResponse,
    )
    return app


def server() -> FastAPI:
    settings = create_settings()
    app: FastAPI = create_app()
    app.exception_handler(errors.AbstractError)(errors.global_exception_handler)
    setup_middlewares(app=app, settings=settings.cors)
    app.include_router(v1_api_router, prefix="/api")
    return app
