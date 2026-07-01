from enum import auto, Enum
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from emittance_viewer.gui.controls.controls import FileListControls

class FileMode(Enum):
    REMOTE = auto()
    LOCAL = auto()

class StatusPane(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.lblFileMode = QLabel()
        self.lblFileMode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblFileMode.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.lblStatus = QLabel()
        self.lblStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lblWarning = QLabel()
        self.lblWarning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblWarning.setStyleSheet("color: red;")
        
        self.file_list_controls = FileListControls()
        
        self.layout.addWidget(self.lblFileMode)
        self.layout.addWidget(self.lblStatus)
        self.layout.addWidget(self.lblWarning)
        self.layout.addWidget(self.file_list_controls)

    def set_file_mode(self, mode: FileMode, info: str):
        match mode:
            case FileMode.REMOTE:
                file_mode = "Remote"
            case _:
                file_mode = "Local"
        self.lblFileMode.setText(f"File mode: {file_mode}")
        self.lblStatus.setText(info)
