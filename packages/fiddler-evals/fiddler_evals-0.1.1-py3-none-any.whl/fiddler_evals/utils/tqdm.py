from typing import Any, Callable

import tqdm
import tqdm.notebook
from tqdm.autonotebook import tqdm
from tqdm.contrib.concurrent import _executor_map

from fiddler_evals.runner.executor import ContextThreadPoolExecutor


def thread_map(fn: Callable, *iterables: Any, **tqdm_kwargs: Any) -> list:
    """
    Equivalent of `list(map(fn, *iterables))` driven by `concurrent.futures.ThreadPoolExecutor`.

    """
    tqdm_class = tqdm_kwargs.pop("tqdm_class", tqdm)
    return _executor_map(
        ContextThreadPoolExecutor,
        fn,
        *iterables,
        tqdm_class=tqdm_class,
        **tqdm_kwargs,
    )
