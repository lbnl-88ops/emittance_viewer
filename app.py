"""PyInstaller entry point.

This file is intentionally kept minimal and defensive. It is the first
thing that runs in the frozen --noconsole build, which means: if anything
below raises before a GUI exists, the user sees NOTHING (no console, no
dialog, no clue). To avoid silent failures, we:

  1. Set up file logging FIRST, before importing anything from
     emittance_viewer (a hidden-import or DLL problem will raise during
     that import).
  2. Wrap the import + app launch in a try/except that writes the full
     traceback to the log file AND attempts to show a native message box
     so the person doing the install knows the app failed and where to
     find the log.

See emittance_viewer/logging_setup.py for the log file location logic.
"""

import sys
import traceback


def _show_fatal_error_dialog(log_path, error_text):
    """Best-effort native error dialog. Must not depend on Qt, since Qt
    itself may be the thing that failed to import."""
    try:
        if sys.platform == "win32":
            import ctypes
            message = (
                f"Emittance Viewer failed to start.\n\n"
                f"Details were written to:\n{log_path}\n\n"
                f"{error_text[-800:]}"
            )
            # MB_OK | MB_ICONERROR
            ctypes.windll.user32.MessageBoxW(0, message, "Emittance Viewer - Startup Error", 0x10)
        else:
            # No guaranteed GUI toolkit available on non-Windows without
            # Qt; fall back to stderr, which is visible when run from a
            # terminal (covers Linux/macOS dev use).
            print(f"Emittance Viewer failed to start. See log: {log_path}", file=sys.stderr)
            print(error_text, file=sys.stderr)
    except Exception:
        # If even the fallback fails, there is nothing more we can do.
        pass


def main():
    # Even the logging setup itself can fail (e.g. a missing hidden import
    # for `appdirs`, or an unwritable log directory on a locked-down
    # machine). Fall back to a hardcoded, best-effort log path so we still
    # have somewhere to write the traceback and something to point the
    # user at.
    fallback_log_path = "emittance_viewer_startup_error.log"
    try:
        from emittance_viewer.logging_setup import configure_logging, LOG_FILEPATH
        configure_logging()
        log_path = LOG_FILEPATH
    except Exception:
        error_text = traceback.format_exc()
        try:
            with open(fallback_log_path, "a", encoding="utf-8") as f:
                f.write(error_text)
        except Exception:
            pass
        _show_fatal_error_dialog(fallback_log_path, error_text)
        sys.exit(1)

    try:
        import logging
        logger = logging.getLogger("ops")
        logger.info("Importing emittance_viewer.app...")
        from emittance_viewer.app import emittance_viewer
        logger.info("Import successful.")
    except Exception:
        error_text = traceback.format_exc()
        import logging
        logging.getLogger("ops").critical(
            "Fatal error importing emittance_viewer.app:\n%s", error_text
        )
        _show_fatal_error_dialog(log_path, error_text)
        sys.exit(1)

    try:
        emittance_viewer()
    except Exception:
        error_text = traceback.format_exc()
        import logging
        logging.getLogger("ops").critical(
            "Fatal error running emittance_viewer():\n%s", error_text
        )
        _show_fatal_error_dialog(log_path, error_text)
        sys.exit(1)


if __name__ == "__main__":
    main()
