"""Tests for API handlers using AAA pattern."""

from unittest.mock import MagicMock, patch

import pytest

from src.api.handlers import partners_data_loader
from src.queue.manager import Job, MockQueueManager, reset_queue_manager


class TestPartnersDataLoaderHandler:
    """Tests for partners_data_loader API handler."""

    def test_returns_job_id_and_200_status(self) -> None:
        """Test that handler returns job_id and 200 status code."""
        # Arrange
        reset_queue_manager()

        # Act
        response, status_code = partners_data_loader()

        # Assert
        assert status_code == 200
        assert "job_id" in response
        assert isinstance(response["job_id"], str)

    def test_passes_dates_to_queue(self) -> None:
        """Test that handler passes dates to the queue manager."""
        # Arrange
        reset_queue_manager()
        with patch("src.api.handlers.get_queue_manager") as mock_get_queue:
            mock_queue = MagicMock()
            mock_job = Job(id="test-job-123")
            mock_queue.enqueue.return_value = mock_job
            mock_get_queue.return_value = mock_queue

            # Act
            response, status_code = partners_data_loader(
                start_date="2025-01-15", finish_date="2025-01-16"
            )

            # Assert
            mock_queue.enqueue.assert_called_once()
            call_args = mock_queue.enqueue.call_args
            assert call_args[0][1] == "2025-01-15"
            assert call_args[0][2] == "2025-01-16"

    def test_returns_unique_job_ids(self) -> None:
        """Test that each call returns a unique job_id."""
        # Arrange
        reset_queue_manager()

        # Act
        response1, _ = partners_data_loader()
        response2, _ = partners_data_loader()

        # Assert
        assert response1["job_id"] != response2["job_id"]

    def test_handles_none_dates(self) -> None:
        """Test that handler handles None dates correctly."""
        # Arrange
        reset_queue_manager()

        # Act
        response, status_code = partners_data_loader(start_date=None, finish_date=None)

        # Assert
        assert status_code == 200
        assert "job_id" in response


class TestMockQueueManager:
    """Tests for MockQueueManager."""

    def test_enqueue_returns_job(self) -> None:
        """Test that enqueue returns a Job object."""
        # Arrange
        queue = MockQueueManager(mongo_host="mongodb://localhost", tag="test")

        async def dummy_task() -> str:
            return "done"

        # Act
        job = queue.enqueue(dummy_task)

        # Assert
        assert isinstance(job, Job)
        assert job.id is not None

    def test_get_job_returns_queued_job(self) -> None:
        """Test that get_job returns a previously queued job."""
        # Arrange
        queue = MockQueueManager(mongo_host="mongodb://localhost", tag="test")

        async def dummy_task() -> str:
            return "done"

        job = queue.enqueue(dummy_task)

        # Act
        retrieved_job = queue.get_job(job.id)

        # Assert
        assert retrieved_job is not None
        assert retrieved_job.id == job.id

    def test_get_job_returns_none_for_unknown_id(self) -> None:
        """Test that get_job returns None for unknown job ID."""
        # Arrange
        queue = MockQueueManager(mongo_host="mongodb://localhost", tag="test")

        # Act
        result = queue.get_job("unknown-job-id")

        # Assert
        assert result is None

    def test_get_queue_returns_self(self) -> None:
        """Test that get_queue returns the manager itself (compatibility)."""
        # Arrange
        queue = MockQueueManager(mongo_host="mongodb://localhost", tag="test")

        # Act
        result = queue.get_queue()

        # Assert
        assert result is queue

    @pytest.mark.asyncio
    async def test_job_executes_in_background(self) -> None:
        """Test that enqueued job executes in background."""
        # Arrange
        import asyncio

        queue = MockQueueManager(mongo_host="mongodb://localhost", tag="test")
        execution_flag = {"executed": False}

        async def set_flag() -> None:
            execution_flag["executed"] = True

        # Act
        job = queue.enqueue(set_flag)
        await asyncio.sleep(0.1)  # Give time for background task

        # Assert
        assert execution_flag["executed"] is True
        assert job.status in ("completed", "running")
