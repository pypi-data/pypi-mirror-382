"""Background task registration for the FastAPI Template application."""

from __future__ import annotations

from collections.abc import Callable, Coroutine

from .uptime import update_uptime


def get_tasks(*, enable_uptime_background_task: bool = True) -> list[Callable[[], Coroutine]]:
    tasks: list[Callable[[], Coroutine]] = []

    if enable_uptime_background_task:
        tasks.append(update_uptime)

    return tasks
