from PyQt6.QtCore import QObject, pyqtSignal
import logging

_log = logging.getLogger(__name__)

class StatusBarSingleton(QObject):
    status_changed = pyqtSignal(str)
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            _log.info("Creating StatusBarSingleton instance")
            cls._instance = super(StatusBarSingleton, cls).__new__(cls)
            # We will initialize in __init__ instead of here
        return cls._instance

    def __init__(self):
        # This will be called every time StatusBarSingleton() is called,
        # but QObject.__init__ should only be called once.
        if not hasattr(self, "_initialized"):
            _log.info("Initializing StatusBarSingleton QObject")
            super().__init__()
            self._status = "Starting up..."
            self._initialized = True

    def get_status(self) -> str:
        return self._status

    def update_status(self, info: str) -> None:
        _log.info(f"Updating status bar: {info}")
        self._status = info
        try:
            self.status_changed.emit(info)
            _log.info("Status signal emitted")
        except Exception as e:
            _log.error(f"Error emitting status signal: {e}")


def update_status_bar(info: str) -> None:
    _log.info(f"update_status_bar called with: {info}")
    try:
        status_bar = StatusBarSingleton()
        status_bar.update_status(info)
    except Exception as e:
        _log.error(f"Failed to update status bar: {e}")
