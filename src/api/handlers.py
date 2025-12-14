"""Connexion API handlers."""

import logging
from typing import Any

from src.config import get_settings
from src.core.data_loader import load_insert_data
from src.queue.manager import get_queue_manager

logger = logging.getLogger(__name__)


def partners_data_loader(
    start_date: str | None = None, finish_date: str | None = None
) -> tuple[dict[str, Any], int]:
    """
    API endpoint to enqueue partner data loading task.

    This is the connexion operationId handler for /load_data_partners/enqueue

    Args:
        start_date: Start date in YYYY-MM-DD format (optional)
        finish_date: End date in YYYY-MM-DD format (optional)

    Returns:
        Tuple of (response_dict, http_status_code)
    """
    settings = get_settings()
    queue = get_queue_manager(
        mongo_host=settings.mongodb_host,
        tag="load_insert_data",
        service="api",
    )

    job = queue.enqueue(load_insert_data, start_date, finish_date)

    logger.info(f"Enqueued partner data loading job: {job.get_id()}")

    return {"job_id": job.get_id()}, 200
