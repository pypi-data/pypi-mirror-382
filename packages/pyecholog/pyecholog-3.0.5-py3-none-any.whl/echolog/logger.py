"""EchoLog logger implementation.

Moved and slightly refactored from the original single-file script.
"""
from __future__ import annotations

import datetime
import os
from enum import Enum
from typing import Optional, Callable, List

try:
    from colorama import init, Fore
    init(autoreset=True)
except Exception:  # colorama is optional for file-only logging
    class _Dummy:
        RESET = ""
        LIGHTBLACK_EX = ""
    Fore = _Dummy()

# Default logs directory (relative to current working directory)
LOGS_FOLDER = os.environ.get("ECHOLOG_LOGS_FOLDER", "logs")

if not os.path.exists(LOGS_FOLDER):
    try:
        os.makedirs(LOGS_FOLDER, exist_ok=True)
    except OSError:
        # If the directory can't be created, fall back to current directory
        LOGS_FOLDER = "."


class LogLevel(Enum):
    DEBUG = ("CYAN", "[DEBUG]")
    INFO = ("GREEN", "[INFO]")
    NOTICE = ("BLUE", "[NOTICE]")
    WARNING = ("YELLOW", "[WARNING]")
    ERROR = ("RED", "[ERROR]")
    CRITICAL = ("MAGENTA", "[CRITICAL]")
    SMTP = ("LIGHTCYAN_EX", "[SMTP SERVER]")
    AUDIT = ("LIGHTBLUE_EX", "[AUDIT]")

    @property
    def color(self) -> str:
        # Return a colorama Fore attribute if available
        return getattr(Fore, self.value[0], "")

    @property
    def text(self) -> str:
        return self.value[1]


def get_log_file_name() -> str:
    """Return log file path for current date."""
    return os.path.join(LOGS_FOLDER, f"{datetime.datetime.now().date().isoformat()}.log")


def add_line(text: str) -> None:
    """Append a line to the daily log file."""
    path = get_log_file_name()
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(text + "\n")


def get_time() -> str:
    return datetime.datetime.now().strftime("%F %T")


class Logger:
    """Simple logger that writes to a daily file and prints to console.

    Contract:
    - Inputs: message text (str), log level (LogLevel), optional print_only flag
    - Outputs: writes to file unless print_only, always prints to stdout
    - Error modes: if file writing fails, still print to console
    """

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name
        self._custom_format: Optional[Callable[[str, LogLevel], str]] = None

    def set_custom_format(self, formatter: Callable[[str, LogLevel], str]) -> None:
        self._custom_format = formatter

    def _log(self, level: LogLevel, text: str, print_only: bool = False) -> None:
        timestamp = get_time()
        color = level.color
        level_text = level.text

        name_part = f" [{self.name}]" if self.name else ""

        if self._custom_format:
            console_output = self._custom_format(text, level)
            file_output = f"[{timestamp}] {level_text} {text}"
        else:
            console_output = f"{Fore.LIGHTBLACK_EX}{timestamp} {color}{level_text}{Fore.RESET}{name_part} {text}"
            file_output = f"[{timestamp}] {level_text}{name_part} {text}"

        # write to file
        if not print_only:
            try:
                add_line(file_output)
            except Exception:
                # fallback: print error but continue
                print(f"[EchoLog] Failed to write to log file: {get_log_file_name()}")

        print(console_output)

    def get_logs(self) -> List[str]:
        try:
            with open(get_log_file_name(), "r", encoding="utf-8") as fh:
                return fh.readlines()
        except FileNotFoundError:
            return []

    def file_name(self) -> str:
        return get_log_file_name()

    def debug(self, text: str, print_only: bool = False) -> None:
        self._log(LogLevel.DEBUG, text, print_only)

    def info(self, text: str) -> None:
        self._log(LogLevel.INFO, text)

    def notice(self, text: str) -> None:
        self._log(LogLevel.NOTICE, text)

    def warning(self, text: str) -> None:
        self._log(LogLevel.WARNING, text)

    def error(self, text: str) -> None:
        self._log(LogLevel.ERROR, text)

    def critical(self, text: str) -> None:
        self._log(LogLevel.CRITICAL, text)

    def smtp(self, text: str) -> None:
        self._log(LogLevel.SMTP, text)

    def audit(self, text: str) -> None:
        self._log(LogLevel.AUDIT, text)
