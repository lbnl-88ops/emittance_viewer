from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from emittance_viewer.gui.style.styles import BUTTON_STYLE, ACTION_BUTTON_STYLE, TITLE_LABEL_STYLE, add_button

class FileListControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.btChangeDirectory = add_button(self.layout, "Choose directory")
        self.btRefresh = add_button(self.layout, "Refresh file list")
        self.btChangeMode = add_button(self.layout, "")

class PlotControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.btPlotScan = add_button(self.layout, "Plot scan")
        self.btPlotScan.setStyleSheet(ACTION_BUTTON_STYLE)
        self.btRemoveFromPlot = add_button(self.layout, "Remove from plot")
        self.btRemoveFromPlot.setEnabled(False)
        self.btClearPlot = add_button(self.layout, "Clear Plot")
        
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
        self.title_label.setStyleSheet(TITLE_LABEL_STYLE)
        
        self.btOpenComparisonWindow = QPushButton("Compare plotted files")
        self.btOpenComparisonWindow.setStyleSheet(BUTTON_STYLE)
        self.btOpenComparisonWindow.setEnabled(False)
        
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.btOpenComparisonWindow)
