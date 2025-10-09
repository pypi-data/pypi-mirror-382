import logging
import threading

from fiddler_evals.entities.experiment import Experiment
from fiddler_evals.pydantic_models.experiment import ExperimentItemResult

logger = logging.getLogger(__name__)


class ExperimentResultPublisher:
    """Internal publisher for batching and pushing experiment results to the backend.

    This class provides efficient result publishing by buffering experiment results
    and flushing them in configurable batches. It reduces network overhead by
    minimizing API calls while ensuring results are pushed in a timely manner.

    The publisher is thread-safe and designed for use in parallel processing
    scenarios where multiple threads may be publishing results simultaneously.

    Why Batching is Required:
        - **Network Efficiency**: Reduces API calls from N (one per item) to N/batch_size
        - **Performance**: Batch operations are significantly faster than individual calls
        - **Rate Limiting**: Prevents overwhelming the API with too many requests
    """

    def __init__(self, experiment: Experiment, batch_size: int = 10):
        """Initialize the result publisher.

        Args:
            experiment: The experiment instance to publish results to.
            batch_size: Number of results to buffer before auto-flushing.
        """
        self.experiment = experiment
        self._buffer: list[ExperimentItemResult] = []
        self._lock = threading.Lock()
        self._batch_size = batch_size

        logger.debug(
            "Initialized experiment result publisher for experiment %s with %d batch size",
            experiment.name,
            batch_size,
        )

    def publish(self, item: ExperimentItemResult) -> None:
        """Publish a single experiment result item.

        Adds the result to the internal buffer and automatically flushes
        when the batch size is reached. This method is thread-safe and
        can be called from multiple threads concurrently.

        Args:
            item: The experiment result item to publish.

        Note:
            The result is added to the buffer immediately. If the buffer
            reaches the configured batch size, it will be automatically
            flushed to the backend.
        """
        with self._lock:
            self._buffer.append(item)

            # Auto-flush when batch size is reached
            if len(self._buffer) >= self._batch_size:
                logger.debug(
                    "Flushing experiment result buffer of size %d", len(self._buffer)
                )
                self._flush_internal()

    def flush(self) -> None:
        """Manually flush all buffered results to the backend.

        Pushes all currently buffered results to the experiment and
        clears the buffer. This method is thread-safe and should be
        called at the end of processing to ensure all results are saved.

        Note:
            This method is safe to call even if the buffer is empty.
            It will simply perform no operation in that case.
        """
        with self._lock:
            self._flush_internal()

    def _flush_internal(self) -> None:
        """Internal method to flush buffer without acquiring lock.

        This method assumes the lock is already held by the caller.
        It pushes all buffered results to the experiment and clears
        the buffer.

        Note:
            This is an internal method and should not be called
            directly from outside the class.
        """
        if self._buffer:
            # Create a copy of the buffer to avoid reference issues
            self.experiment.add_results(items=self._buffer.copy())
            self._buffer.clear()
