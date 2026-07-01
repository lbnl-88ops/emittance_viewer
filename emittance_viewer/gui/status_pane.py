from enum import auto, Enum
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from emittance_viewer.gui.controls.controls import FileListControls
from emittance_viewer.gui.style.constants import COLOR_INFO, COLOR_MUTED, COLOR_CAUTION
from emittance_viewer.gui.style.styles import MODE_INDICATOR_STYLE

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
        self.lblFileMode.setStyleSheet(MODE_INDICATOR_STYLE)
        
        self.lblStatus = QLabel()
        self.lblStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lblWarning = QLabel()
        self.lblWarning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblWarning.setStyleSheet(f"color: {COLOR_CAUTION}; font-weight: bold;")
        
        self.file_list_controls = FileListControls()
        
        self.layout.addWidget(self.lblFileMode)
        self.layout.addWidget(self.lblStatus)
        self.layout.addWidget(self.lblWarning)
        self.layout.addWidget(self.file_list_controls)

    def set_file_mode(self, mode: FileMode, info: str):
        match mode:
            case FileMode.REMOTE:
                file_mode = "Remote"
                color = COLOR_INFO
            case _:
                file_mode = "Local"
                color = COLOR_MUTED
        self.lblFileMode.setText(f"File mode: {file_mode}")
        self.lblFileMode.setStyleSheet(MODE_INDICATOR_STYLE + f"background-color: {color};")
        self.lblStatus.setText(info)
