"""
Thread pool executor that preserves context variables across threads.

This module provides a specialized ThreadPoolExecutor that ensures context variables
are properly propagated to worker threads, maintaining execution context across
multi-threaded operations.
"""

import contextvars
from concurrent.futures import ThreadPoolExecutor
from typing import Any


class ContextThreadPoolExecutor(ThreadPoolExecutor):
    """Thread pool executor that preserves context variables across threads.

    This specialized ThreadPoolExecutor ensures that context variables (contextvars)
    are properly propagated to worker threads, maintaining execution context across
    multi-threaded operations. This is essential for maintaining state consistency
    in concurrent applications.

    Key Features:
        - **Context Preservation**: Automatically copies and restores context variables
        - **Thread Safety**: Ensures each worker thread has the correct context
        - **Transparent Usage**: Drop-in replacement for ThreadPoolExecutor
        - **Custom Initializers**: Supports custom thread initialization functions

    Why Context Preservation is Required:
        Context variables (contextvars) are thread-local by design and are not
        automatically inherited by new threads. When using ThreadPoolExecutor,
        worker threads start with empty context, losing important execution state
        such as:
        - Request IDs and correlation IDs for tracing
        - Connection context

    Without context preservation, multi-threaded operations lose critical context
    information, leading to:
        - Broken request tracing and debugging
        - Loss of user authentication in worker threads
        - Inconsistent logging and monitoring
        - Difficult-to-debug concurrency issues

    Args:
        *args: Positional arguments passed to ThreadPoolExecutor.
        **kwargs: Keyword arguments passed to ThreadPoolExecutor. The 'initializer'
                 parameter is handled specially to preserve context.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the context-aware thread pool executor.

        Captures the current context variables and sets up the executor to
        propagate them to worker threads.

        Args:
            *args: Positional arguments passed to ThreadPoolExecutor.
            **kwargs: Keyword arguments passed to ThreadPoolExecutor.
                     The 'initializer' parameter is handled specially to
                     preserve context while still allowing custom initialization.

        Note:
            The context is captured at executor creation time, not at task
            submission time. This ensures consistent context across all tasks
            submitted to this executor.
        """
        self.context = contextvars.copy_context()
        self._kwargs_initializer = kwargs.pop("initializer", None)
        super().__init__(*args, initializer=self._custom_initializer, **kwargs)

    def _custom_initializer(self, *args: Any, **kwargs: Any) -> None:
        """Initialize worker thread with preserved context.

        This method is called for each worker thread to restore the context
        variables that were captured when the executor was created. It also
        calls any custom initializer function if provided.

        Args:
            *args: Arguments passed to the custom initializer function.
            **kwargs: Keyword arguments passed to the custom initializer function.

        Note:
            This method is called automatically by ThreadPoolExecutor for
            each worker thread. It should not be called directly.
        """
        self._set_child_context()

        if self._kwargs_initializer:
            self._kwargs_initializer(*args, **kwargs)

    def _set_child_context(self) -> None:
        """Set context variables in the current worker thread.

        Restores all context variables that were captured when the executor
        was created. This ensures that worker threads have access to the
        same context as the main thread.

        Note:
            This method is called automatically by _initializer() for each
            worker thread. It should not be called directly.
        """
        for var, value in self.context.items():
            var.set(value)
