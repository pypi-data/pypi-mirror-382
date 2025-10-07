"""EchoLog - lightweight logging library

Expose Logger and version metadata.
"""
from .logger import Logger, LogLevel

__all__ = ["Logger", "LogLevel"]
__version__ = "3.0.5"
