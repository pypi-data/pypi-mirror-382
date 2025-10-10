"""
AsyncFlow: Async execution library with concurrent.futures-style API and advanced pipelines.
"""

from ._version import __version__
from .exceptions import (
    AsyncFlowError,
    ExecutorShutdownError,
    PipelineError,
    StageValidationError,
    TaskFailedError,
)
from .executor import AsyncExecutor, AsyncFuture, WaitStrategy
from .pipeline import Pipeline, Stage
from .types import (
    CallbackFunc,
    OrderedResult,
    PipelineStats,
    TaskCallbackFunc,
    TaskFunc,
)

__all__ = [
    "__version__",
    "AsyncExecutor",
    "AsyncFuture",
    "AsyncFlowError",
    "CallbackFunc",
    "ExecutorShutdownError",
    "OrderedResult",
    "Pipeline",
    "PipelineError",
    "PipelineStats",
    "Stage",
    "StageValidationError",
    "TaskCallbackFunc",
    "TaskFailedError",
    "TaskFunc",
    "WaitStrategy",
]
