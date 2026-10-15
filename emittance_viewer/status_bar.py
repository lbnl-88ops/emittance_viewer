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
        self._status = info
        self.status_changed.emit(info)

# The one and only instance
_singleton_instance = None

def StatusBarSingleton():
    global _singleton_instance
    if _singleton_instance is None:
        _singleton_instance = StatusBarSignalEmitter()
    return _singleton_instance

def update_status_bar(info: str) -> None:
    try:
        status_bar = StatusBarSingleton()
        status_bar.update_status(info)
    except Exception:
        pass
