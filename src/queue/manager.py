"""Queue manager interface and mock implementation."""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Job:
    """Represents a queued job."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    result: Any = None
    error: str | None = None

    def get_id(self) -> str:
        """Get job ID."""
        return self.id


class QueueManager(ABC):
    """Abstract queue manager interface."""

    @abstractmethod
    def enqueue(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Job:
        """Enqueue a function for async execution."""
        ...

    @abstractmethod
    def get_job(self, job_id: str) -> Job | None:
        """Get job by ID."""
        ...


class MockQueueManager(QueueManager):
    """
    Mock queue manager for testing and development.

    This is a replacement for qmanager.q that cannot be installed from pypi.
    In production, this would be replaced with the real qmanager implementation.
    """

    def __init__(self, mongo_host: str = "", tag: str = "", **kwargs: Any) -> None:  # noqa: ARG002
        """Initialize mock queue manager."""
        self._jobs: dict[str, Job] = {}
        self._mongo_host = mongo_host
        self._tag = tag
        self._background_tasks: set[asyncio.Task] = set()

    def enqueue(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Job:
        """
        Enqueue an async function for background execution.

        In the mock implementation, this schedules the coroutine to run
        in the background without blocking.
        """
        job = Job()
        self._jobs[job.id] = job

        async def run_job() -> None:
            try:
                job.status = "running"
                logger.info(f"Job {job.id} started: {func.__name__}")
                job.result = await func(*args, **kwargs)
                job.status = "completed"
                logger.info(f"Job {job.id} completed")
            except Exception as e:
                job.status = "failed"
                job.error = str(e)
                logger.error(f"Job {job.id} failed: {e}")

        # Schedule the job to run in background
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(run_job())
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
        except RuntimeError:
            # No running loop - for sync context, just mark as pending
            logger.warning(f"Job {job.id} queued but not started (no event loop)")

        return job

    def get_job(self, job_id: str) -> Job | None:
        """Get job by ID."""
        return self._jobs.get(job_id)

    def get_queue(self) -> "MockQueueManager":
        """Compatibility method - returns self."""
        return self


# Global queue manager instance
_queue_manager: QueueManager | None = None


def get_queue_manager(mongo_host: str = "", tag: str = "", service: str = "api") -> QueueManager:
    """
    Get or create queue manager instance.

    This function mimics the original queue() function from common.queue.
    """
    global _queue_manager

    if _queue_manager is None:
        # In production, this would initialize the real qmanager
        # For now, we use the mock implementation
        _queue_manager = MockQueueManager(mongo_host=mongo_host, tag=f"{service}/{tag}")

    return _queue_manager


def reset_queue_manager() -> None:
    """Reset queue manager (useful for testing)."""
    global _queue_manager
    _queue_manager = None
