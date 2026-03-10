from asyncio import Semaphore
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from multiprocessing import get_context

from fastapi import FastAPI

from app.api.routes.report import router as report_router
from app.core.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.process_pool = ProcessPoolExecutor(
        max_workers=settings.process_pool_workers,
        mp_context=get_context("spawn"),
    )
    app.state.export_semaphore = Semaphore(settings.max_concurrent_exports)

    try:
        yield
    finally:
        app.state.process_pool.shutdown(wait=True, cancel_futures=True)


app = FastAPI(lifespan=lifespan)
app.include_router(report_router)
