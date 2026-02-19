import logging
import sys

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.exceptions import (
    AppError,
    ConflictError,
    InsufficientStockError,
    InvalidStatusTransitionError,
    NotFoundError,
)
from app.api.v1 import products as products_router
from app.api.v1 import orders as orders_router

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description=(
            "Inventory & Order Management API. "
            "Transactional order creation with SELECT FOR UPDATE to prevent overselling."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(products_router.router, prefix="/api/v1")
    app.include_router(orders_router.router, prefix="/api/v1")

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        logger.warning("Not found: %s", exc.message)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message},
        )

    @app.exception_handler(InsufficientStockError)
    async def insufficient_stock_handler(
        request: Request, exc: InsufficientStockError
    ) -> JSONResponse:
        logger.warning("Insufficient stock: %s", exc.message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": exc.message,
                "product_id": exc.product_id,
                "requested": exc.requested,
                "available": exc.available,
            },
        )

    @app.exception_handler(InvalidStatusTransitionError)
    async def invalid_transition_handler(
        request: Request, exc: InvalidStatusTransitionError
    ) -> JSONResponse:
        logger.warning("Invalid status transition: %s", exc.message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(
        request: Request, exc: ConflictError
    ) -> JSONResponse:
        logger.warning("Conflict: %s", exc.message)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message},
        )

    @app.exception_handler(AppError)
    async def generic_app_error_handler(
        request: Request, exc: AppError
    ) -> JSONResponse:
        logger.error("Unhandled app error: %s", exc.message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("Request validation error: %s", exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.get("/", tags=["Root"], include_in_schema=False)
    async def root() -> dict[str, str]:
        return {
            "message": "Welcome to the Inventory & Order Management API",
            "docs": "/docs",
            "version": settings.app_version,
        }

    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "version": settings.app_version}

    logger.info("Application started: %s v%s", settings.app_title, settings.app_version)
    return app


app = create_app()
