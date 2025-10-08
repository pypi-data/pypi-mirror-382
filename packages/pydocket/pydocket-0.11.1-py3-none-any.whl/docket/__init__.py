"""
docket - A distributed background task system for Python functions.

docket focuses on scheduling future work as seamlessly and efficiently as immediate work.
"""

from importlib.metadata import version

__version__ = version("pydocket")

from .agenda import Agenda
from .annotations import Logged
from .dependencies import (
    ConcurrencyLimit,
    CurrentDocket,
    CurrentExecution,
    CurrentWorker,
    Depends,
    ExponentialRetry,
    Perpetual,
    Retry,
    TaskArgument,
    TaskKey,
    TaskLogger,
    Timeout,
)
from .docket import Docket
from .execution import Execution
from .worker import Worker

__all__ = [
    "__version__",
    "Agenda",
    "ConcurrencyLimit",
    "CurrentDocket",
    "CurrentExecution",
    "CurrentWorker",
    "Depends",
    "Docket",
    "Execution",
    "ExponentialRetry",
    "Logged",
    "Perpetual",
    "Retry",
    "TaskArgument",
    "TaskKey",
    "TaskLogger",
    "Timeout",
    "Worker",
]
