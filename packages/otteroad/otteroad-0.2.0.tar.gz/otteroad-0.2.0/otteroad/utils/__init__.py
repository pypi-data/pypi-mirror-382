"""
This package provides shared utilities and abstractions used across the Kafka client library:

- LoggerProtocol: Runtime-checkable protocol for injecting custom loggers.
- (Future utilities can be added here, e.g., metrics, error classes, common helpers.)

Usage example:

    from otteroad.utils import LoggerProtocol

    def my_function(logger: LoggerProtocol):
        logger.info("This is a log message")

Exports:
    - LoggerAdapter: Universal adapter for logging, loguru and structlog.
    - LoggerProtocol: Protocol for a standard logging interface, compatible with Python's logging.Logger.
"""

from .logger import LoggerAdapter, LoggerProtocol

__all__ = [
    "LoggerAdapter",
    "LoggerProtocol",
]
