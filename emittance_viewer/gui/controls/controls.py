from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt

class FileListControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.btChangeDirectory = QPushButton("Choose directory")
        self.btRefresh = QPushButton("Refresh file list")
        self.btChangeMode = QPushButton("")
        
        self.layout.addWidget(self.btChangeDirectory)
        self.layout.addWidget(self.btRefresh)
        self.layout.addWidget(self.btChangeMode)

class PlotControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.btPlotScan = QPushButton("Plot scan")
        self.btRemoveFromPlot = QPushButton("Remove from plot")
        self.btRemoveFromPlot.setEnabled(False)
        self.btClearPlot = QPushButton("Clear Plot")
        
        self.layout.addWidget(self.btPlotScan)
        self.layout.addWidget(self.btRemoveFromPlot)
        self.layout.addWidget(self.btClearPlot)

    def activate_buttons(self, can_plot: bool = False, can_remove: bool = False):
        self.btPlotScan.setEnabled(can_plot)
        self.btRemoveFromPlot.setEnabled(can_remove)

class Tools(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("Tools")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.btOpenComparisonWindow = QPushButton("Compare plotted files")
        self.btOpenComparisonWindow.setEnabled(False)
        
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.btOpenComparisonWindow)
