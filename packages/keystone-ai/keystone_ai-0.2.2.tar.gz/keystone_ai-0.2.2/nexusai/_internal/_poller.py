"""Task polling mechanism for async operations."""

import time
from typing import Dict, Any, Optional
from nexusai.error import APITimeoutError, APIError
from nexusai.models import Task
from nexusai.config import config
from nexusai.constants import (
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_PENDING,
    TASK_STATUS_QUEUED,
    TASK_STATUS_RUNNING,
)


class TaskPoller:
    """
    Polls async tasks until completion or failure.

    This class handles:
    - Periodic task status checking
    - Timeout management
    - Error handling for failed tasks
    """

    def __init__(
        self,
        client,  # Type: InternalClient (avoiding circular import)
        poll_interval: Optional[float] = None,
        poll_timeout: Optional[float] = None,
    ):
        """
        Initialize the task poller.

        Args:
            client: Internal HTTP client instance
            poll_interval: Seconds between polls (overrides config)
            poll_timeout: Maximum seconds to poll (overrides config)
        """
        self.client = client
        self.poll_interval = poll_interval if poll_interval is not None else config.poll_interval
        self.poll_timeout = poll_timeout if poll_timeout is not None else config.poll_timeout

    def poll(self, task_id: str) -> Dict[str, Any]:
        """
        Poll a task until it completes or fails.

        Args:
            task_id: Unique task identifier

        Returns:
            Final task data including output

        Raises:
            APITimeoutError: If polling exceeds timeout
            APIError: If task fails or encounters error
        """
        start_time = time.time()

        while True:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > self.poll_timeout:
                raise APITimeoutError(
                    f"Task {task_id} polling timeout after {self.poll_timeout:.1f} seconds"
                )

            # Query task status
            response = self.client.request("GET", f"/tasks/{task_id}")

            # Validate response with Pydantic
            try:
                task = Task(**response)
            except Exception as e:
                raise APIError(f"Invalid task response: {str(e)}")

            # Handle completed task
            if task.status == TASK_STATUS_COMPLETED:
                return response

            # Handle failed task
            elif task.status == TASK_STATUS_FAILED:
                error_info = task.error or {}
                error_message = error_info.get("message", "Task failed")
                error_code = error_info.get("code", "TASK_FAILED")
                raise APIError(
                    message=error_message,
                    error_code=error_code,
                )

            # Continue polling for pending/queued/running tasks
            elif task.status in [TASK_STATUS_PENDING, TASK_STATUS_QUEUED, TASK_STATUS_RUNNING]:
                # Wait before next poll
                time.sleep(self.poll_interval)

            # Unknown status
            else:
                raise APIError(f"Unknown task status: {task.status}")

    def poll_with_progress(
        self, task_id: str, progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Poll a task with optional progress callback.

        Args:
            task_id: Unique task identifier
            progress_callback: Optional callback function(progress: int)

        Returns:
            Final task data including output

        Raises:
            APITimeoutError: If polling exceeds timeout
            APIError: If task fails
        """
        start_time = time.time()

        while True:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > self.poll_timeout:
                raise APITimeoutError(
                    f"Task {task_id} polling timeout after {self.poll_timeout:.1f} seconds"
                )

            # Query task status
            response = self.client.request("GET", f"/tasks/{task_id}")
            task = Task(**response)

            # Call progress callback if provided
            if progress_callback and task.progress is not None:
                progress_callback(task.progress)

            # Check task status
            if task.status == TASK_STATUS_COMPLETED:
                return response
            elif task.status == TASK_STATUS_FAILED:
                error_info = task.error or {}
                raise APIError(
                    message=error_info.get("message", "Task failed"),
                    error_code=error_info.get("code", "TASK_FAILED"),
                )
            elif task.status in [TASK_STATUS_PENDING, TASK_STATUS_QUEUED, TASK_STATUS_RUNNING]:
                time.sleep(self.poll_interval)
            else:
                raise APIError(f"Unknown task status: {task.status}")
