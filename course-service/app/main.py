import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.exc import OperationalError

from app.db import Base, engine
from app.routers import courses


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# Blue/green settings, set by the Kubernetes Deployment of each colour.
# COLOUR and APP_VERSION let the pipeline (and me) see which copy answered.
COLOUR = os.getenv("COLOUR", "none")
APP_VERSION = os.getenv("APP_VERSION", "dev")

# Fault injection for the Task 10.3HD demo. It is always "none" unless the
# production workflow is started by hand with a demo fault selected.
#   broken-api  : every API call returns 500 (the smoke test should catch it)
#   late-errors : API calls work at first, then return 500 after
#                 FAULT_AFTER_REQUESTS calls (only the watch after the swap
#                 can catch it)
# /health, / and /metrics are never broken, so Kubernetes still thinks the
# pods are healthy. That is the point: probes alone would not save us.
DEMO_FAULT = os.getenv("DEMO_FAULT", "none")
FAULT_AFTER_REQUESTS = int(os.getenv("FAULT_AFTER_REQUESTS", "25"))
UNFAULTED_PATHS = {"/", "/health", "/metrics"}
api_request_count = 0


def initialise_database() -> None:
    maximum_attempts = 10
    retry_delay_seconds = 5

    for attempt in range(1, maximum_attempts + 1):
        try:
            Base.metadata.create_all(bind=engine)

            logger.info(
                "Database connection established successfully."
            )

            return

        except OperationalError:
            logger.warning(
                "Database connection failed. Attempt %s of %s.",
                attempt,
                maximum_attempts,
            )

            if attempt == maximum_attempts:
                logger.exception(
                    "Unable to connect to the database."
                )
                raise

            time.sleep(retry_delay_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialise_database()
    yield


app = FastAPI(
    title="KoalaTech University Course Service",
    description=(
        "Manages courses and lecturer assignments "
        "for KoalaTech University."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(courses.router)


# This middleware is added BEFORE the Prometheus instrumentator on purpose.
# Starlette runs the last added middleware first, so the instrumentator wraps
# this one and the simulated 500 errors are counted in http_requests_total.
@app.middleware("http")
async def demo_fault_injection(request: Request, call_next):
    global api_request_count

    if DEMO_FAULT != "none" and request.url.path not in UNFAULTED_PATHS:
        api_request_count += 1

        broken = DEMO_FAULT == "broken-api" or (
            DEMO_FAULT == "late-errors"
            and api_request_count > FAULT_AFTER_REQUESTS
        )

        if broken:
            logger.error(
                "Simulated fault '%s' on %s (request %s)",
                DEMO_FAULT,
                request.url.path,
                api_request_count,
            )
            return JSONResponse(
                status_code=500,
                content={"detail": f"Simulated fault: {DEMO_FAULT}"},
            )

    return await call_next(request)


# Expose Prometheus metrics (request count, latency, status codes) on /metrics
Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    return {
        "message": (
            "KoalaTech University Course Service is running."
        )
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "course-service",
        "colour": COLOUR,
        "version": APP_VERSION,
    }