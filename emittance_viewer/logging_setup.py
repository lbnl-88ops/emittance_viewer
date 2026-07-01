"""Centralized logging configuration.

The app is built with --noconsole on Windows, meaning stdout/stderr and
any console-based logging.StreamHandler output go nowhere. Without a file
handler, an unhandled exception on startup is completely invisible to the
user and to anyone trying to debug a support ticket after the fact.

This module sets up a log file under the OS-appropriate per-user log
directory (via appdirs), rotated so it can't grow unbounded, and installs
sys.excepthook so that ANY unhandled exception anywhere in the app --- not
just at startup --- gets written to that file.
"""

import logging
import logging.handlers
import sys
from pathlib import Path

from appdirs import user_log_dir

APP_NAME = "emittance_viewer"
APP_AUTHOR = "lbnl_88ops"

LOG_DIRECTORY = Path(user_log_dir(APP_NAME, APP_AUTHOR))
LOG_FILEPATH = LOG_DIRECTORY / "emittance_viewer.log"

_configured = False


def configure_logging(level=logging.INFO):
    """Set up console + rotating file logging and a global excepthook.

    Safe to call more than once; only configures handlers the first time.
    """
    global _configured
    if _configured:
        return
    _configured = True

    LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILEPATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)

    # In --console debug builds (or when run from a terminal), also echo to
    # stdout/stderr. In --noconsole release builds, sys.stdout/sys.stderr
    # may be None, so guard against that instead of crashing on the
    # StreamHandler itself trying to write.
    if sys.stdout is not None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    logging.getLogger("ops").info(
        "Logging initialized. Log file: %s", LOG_FILEPATH
    )

    _install_excepthook()


def _install_excepthook():
    """Ensure unhandled exceptions anywhere in the app are logged, not just
    swallowed silently (which is what happens by default under
    --noconsole)."""

    def _log_unhandled_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.getLogger("ops").critical(
            "Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = _log_unhandled_exception
