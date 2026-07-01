"""Main emittance Viewer App"""

import logging
from pathlib import Path
import sys
import platform
import os
import subprocess

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QScrollArea, QLabel, QFrame
)
from PyQt6.QtCore import Qt

import matplotlib
import matplotlib.pyplot as plt

from .coordinator import Coordinator, FileListType
from emittance_viewer.files.configuration import (
    AppConfiguration,
    create_configuration,
    save_configuration,
    load_configuration,
    CONFIG_FILEPATH,
)
from emittance_viewer.gui.style.patchMatplotlib import applyPatch
from emittance_viewer.gui.status_pane import StatusPane
from emittance_viewer.status_bar import StatusBarSingleton

from .gui import (
    Tools,
    FileList,
    PlotControls,
    Plot,
    AppMenu,
    DiagnosticWindow,
    FileInfoPane
)
from .gui.style.constants import COLOR_BG, COLOR_TEXT
from .gui.style.styles import MENU_STYLE, TITLE_LABEL_STYLE, add_label

__version__ = "0.1.0"

matplotlib.rc("font", size=14)
applyPatch()

logger = logging.getLogger("ops")
logger.addHandler(logging.StreamHandler())
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

class EmittanceViewer(QMainWindow):
    def __init__(self, configuration: AppConfiguration | None):
        super().__init__()
        self.configuration = configuration
        if self.configuration is None:
            self.configuration = create_configuration()

        self.setWindowTitle(f"Emittance Viewer (v{__version__})")
        self.resize(self.configuration.window_width, self.configuration.window_height)
        
        if self.configuration.window_x is not None and self.configuration.window_y is not None:
            self.move(self.configuration.window_x, self.configuration.window_y)

        self.setStyleSheet(f"background: {COLOR_BG}; color: {COLOR_TEXT};" + MENU_STYLE)
        self.create_widgets()
        self.create_menu()
        self.setMinimumSize(800, 600)

        # Connect status bar singleton to our status bar
        StatusBarSingleton().status_changed.connect(self.statusBar().showMessage)
        self.statusBar().showMessage(StatusBarSingleton().get_status())

    def create_menu(self):
        self.app_menu = AppMenu(self)
        self.app_menu.populate_menu(self.menuBar())

    def create_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # Plot area
        self.plot = Plot()
        self.splitter.addWidget(self.plot)

        # Control pane (scrollable)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.control_pane = QWidget()
        self.control_layout = QVBoxLayout(self.control_pane)
        self.scroll_area.setWidget(self.control_pane)
        self.splitter.addWidget(self.scroll_area)

        # Set initial splitter sizes
        if self.configuration.sash_position is not None:
            self.splitter.setSizes([self.configuration.sash_position, self.width() - self.configuration.sash_position])
        else:
            self.splitter.setStretchFactor(0, 3)
            self.splitter.setStretchFactor(1, 1)

        # Components in control pane
        self.status_pane = StatusPane()
        self.control_layout.addWidget(self.status_pane)

        # File lists
        self.file_list_container = QWidget()
        self.file_list_grid = QHBoxLayout(self.file_list_container)
        
        self.available_files_layout = QVBoxLayout()
        add_label(self.available_files_layout, "Available Files", TITLE_LABEL_STYLE).setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_list = FileList()
        self.available_files_layout.addWidget(self.file_list)
        self.file_list_grid.addLayout(self.available_files_layout)

        self.plotted_files_layout = QVBoxLayout()
        add_label(self.plotted_files_layout, "Plotted Files", TITLE_LABEL_STYLE).setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plotted_file_list = FileList()
        self.plotted_files_layout.addWidget(self.plotted_file_list)
        self.file_list_grid.addLayout(self.plotted_files_layout)

        self.control_layout.addWidget(self.file_list_container)

        self.plot_controls = PlotControls()
        self.control_layout.addWidget(self.plot_controls)

        self.tools = Tools()
        self.control_layout.addWidget(self.tools)

        self.file_info_pane = FileInfoPane()
        self.control_layout.addWidget(self.file_info_pane)

        self.control_layout.addStretch()

        # Coordinator
        self.coordinator = Coordinator(
            self,
            [
                self.plot_controls,
                self.plot,
                self.tools,
                self.file_info_pane,
                self.status_pane
            ],
            self.configuration.default_directory,
        )
        self.coordinator.attach(self.file_list, FileListType.TO_PLOT)
        self.coordinator.attach(self.plotted_file_list, FileListType.PLOTTED)
        self.coordinator.initialize()

    def diagnostic_mode(self):
        if hasattr(self, "_diagnostic_window") and self._diagnostic_window.isVisible():
            self._diagnostic_window.raise_()
            self._diagnostic_window.activateWindow()
            return
        self._diagnostic_window = DiagnosticWindow(self)

    def quit(self):
        plt.close("all")
        self.close()

    def closeEvent(self, event):
        # Save geometry
        self.configuration.window_width = self.width()
        self.configuration.window_height = self.height()
        self.configuration.window_x = self.x()
        self.configuration.window_y = self.y()
        
        # Save splitter positions
        sizes = self.splitter.sizes()
        if sizes:
            # We don't have a direct 'sash_position' in QSplitter but we can save the first size
            self.configuration.sash_position = sizes[0]

        save_configuration(self.configuration)
        plt.close("all")
        event.accept()

    def open_data_directory(self):
        self._open_directory(self.configuration.default_directory)

    def open_config_directory(self):
        self._open_directory(CONFIG_FILEPATH)

    def _open_directory(self, path):
        path = str(path)
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", path])

def emittance_viewer():
    app = QApplication(sys.argv)
    configuration = load_configuration()
    viewer = EmittanceViewer(configuration)
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    emittance_viewer()
