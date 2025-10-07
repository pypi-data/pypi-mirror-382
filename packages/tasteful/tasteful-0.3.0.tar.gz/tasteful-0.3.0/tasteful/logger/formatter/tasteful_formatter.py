import logging

from typing import Any


class TastefulFormatter(logging.Formatter):
    """Add colors to logs like FastAPI."""

    LEVEL_COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[31;1m",  # Bold Red
    }

    FLAVOR_COLOR = "\033[35;1m"  # Bold Purple
    APP_NAME_COLOR = "\033[34m"  # Blue
    TIME_COLOR = "\033[90m"  # Gray

    RESET = "\033[0m"

    def __init__(
        self,
        fmt: str,
        datefmt: str = "%Y-%m-%d %H:%M:%S",
        **kwargs: Any,
    ) -> None:
        """Initialize the formatter with a precise timestamp format."""
        super().__init__(fmt=fmt, datefmt=datefmt, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        levelname = record.levelname
        message = super().format(record)

        time_str = getattr(record, "asctime", self.formatTime(record, self.datefmt))
        full_time = f"{time_str}.{int(record.msecs):03d}"
        colored_time = f"{self.TIME_COLOR}{full_time}{self.RESET}"
        message = message.replace(full_time, colored_time)

        if levelname in self.LEVEL_COLORS:
            color = self.LEVEL_COLORS[levelname]
            message = message.replace(levelname, f"{color}{levelname}{self.RESET}")

        if hasattr(record, "flavor"):
            flavor_tag = f"[{record.flavor}]"
            colored_flavor = f"{self.FLAVOR_COLOR}{flavor_tag}{self.RESET}"
            orig_msg = record.getMessage()
            message = message.replace(orig_msg, f"{colored_flavor} {orig_msg}")

        if hasattr(record, "tasteful_app"):
            tasteful_app_tag = f"[{record.tasteful_app}]"
            colored_tasteful_app = f"{self.APP_NAME_COLOR}{tasteful_app_tag}{self.RESET}"
            orig_msg = record.getMessage()
            message = message.replace(orig_msg, f"{colored_tasteful_app} {orig_msg}")

        return message
