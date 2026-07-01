from PyQt6.QtCore import QObject, pyqtSignal

class StatusBarSingleton(QObject):
    _instance = None
    status_changed = pyqtSignal(str)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StatusBarSingleton, cls).__new__(cls)
            QObject.__init__(cls._instance)
            cls._instance._status = "Starting up..."
            cls._instance._initialized = True
        return cls._instance

    def __init__(self):
        # Prevent QObject.__init__ from being called multiple times
        pass

    def get_status(self) -> str:
        return self._status

    def update_status(self, info: str) -> None:
        self._status = info
        self.status_changed.emit(info)


def update_status_bar(info: str) -> None:
    status_bar = StatusBarSingleton()
    status_bar.update_status(info)
