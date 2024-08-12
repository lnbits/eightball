import asyncio

from fastapi import APIRouter
from loguru import logger

from .crud import db
from .tasks import wait_for_paid_invoices
from .views import eightball_generic_router
from .views_api import eightball_api_router
from .views_lnurl import eightball_lnurl_router

eightball_ext: APIRouter = APIRouter(prefix="/eightball", tags=["EightBall"])
eightball_ext.include_router(eightball_generic_router)
eightball_ext.include_router(eightball_api_router)
eightball_ext.include_router(eightball_lnurl_router)

eightball_static_files = [
    {
        "path": "/eightball/static",
        "name": "eightball_static",
    }
]

scheduled_tasks: list[asyncio.Task] = []


def eightball_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def eightball_start():
    from lnbits.tasks import create_permanent_unique_task

    task = create_permanent_unique_task("ext_eightball", wait_for_paid_invoices)
    scheduled_tasks.append(task)


__all__ = [
    "db",
    "eightball_ext",
    "eightball_static_files",
    "eightball_start",
    "eightball_stop",
]
