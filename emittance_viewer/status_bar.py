from PyQt6.QtCore import QObject, pyqtSignal
import logging

_log = logging.getLogger(__name__)

class StatusBarSignalEmitter(QObject):
    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._status = "Starting up..."

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

# The one and only instance
_singleton_instance = None

def StatusBarSingleton():
    global _singleton_instance
    if _singleton_instance is None:
        _log.info("Creating StatusBarSignalEmitter singleton instance")
        _singleton_instance = StatusBarSignalEmitter()
    return _singleton_instance

def update_status_bar(info: str) -> None:
    _log.info(f"update_status_bar called with: {info}")
    try:
        status_bar = StatusBarSingleton()
        status_bar.update_status(info)
    except Exception as e:
        _log.error(f"Failed to update status bar: {e}")
