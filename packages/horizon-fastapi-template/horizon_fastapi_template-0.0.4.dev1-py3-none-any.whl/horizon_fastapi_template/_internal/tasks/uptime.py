"""Uptime metric background task."""

import asyncio
import time

from prometheus_client import Gauge

UPTIME = Gauge("app_uptime_seconds", "Application uptime in seconds")

_start_time = time.time()


def _current_uptime() -> float:
    return time.time() - _start_time


async def update_uptime() -> None:
    while True:
        UPTIME.set(_current_uptime())
        await asyncio.sleep(1)
