import time

from fastapi import FastAPI, Request, logger
from fastapi.staticfiles import StaticFiles
from fastapi_versioning import VersionedFastAPI

from app.api.routers import api_router
from app.core.config import get_settings
from app.core.db import init_db

settings = get_settings()

logger.logger.setLevel(level=settings.LOG_LEVEL)

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(api_router)
app = VersionedFastAPI(app, version_format="{major}", prefix_format="/api/v{major}")
app.mount(
    settings.MEDIA_URL,
    StaticFiles(directory=settings.MEDIA_ROOT),
    name=settings.MEDIA_URL,
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Request-Time"] = f"{str(round(process_time, 2) * 1000)} ms"
    return response


init_db(app)
