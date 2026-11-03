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
from emittance_viewer.files.client import clear_temp_files
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
from emittance_viewer.logging_setup import configure_logging

from .gui import (
    Tools,
    FileList,
    PlotControls,
    Plot,
    AppMenu,
    DiagnosticWindow,
    SingleScanPane
)
from .gui.style.constants import COLOR_BG, COLOR_TEXT
from .gui.style.styles import MENU_STYLE, TITLE_LABEL_STYLE, add_label

__version__ = "0.1.0"

# Initialize logging and matplotlib settings
configure_logging()
matplotlib.rc("font", size=14)
applyPatch()

logger = logging.getLogger("ops")

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
        logger.info("create_widgets started")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Upper Area: Plot and Data
        self.upper_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.upper_splitter, stretch=3)

        self.plot = Plot()
        self.upper_splitter.addWidget(self.plot)

        self.single_scan_pane = SingleScanPane()
        self.single_scan_scroll = QScrollArea()
        self.single_scan_scroll.setWidgetResizable(True)
        self.single_scan_scroll.setWidget(self.single_scan_pane)
        self.upper_splitter.addWidget(self.single_scan_scroll)
        
        self.upper_splitter.setStretchFactor(0, 3)
        self.upper_splitter.setStretchFactor(1, 1)

        # Lower Area: Lists and Controls
        self.lower_container = QWidget()
        self.lower_layout = QHBoxLayout(self.lower_container)
        self.main_layout.addWidget(self.lower_container, stretch=1)

        # File lists
        self.available_files_layout = QVBoxLayout()
        add_label(self.available_files_layout, "Available Scans", TITLE_LABEL_STYLE).setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_list = FileList()
        self.available_files_layout.addWidget(self.file_list)
        self.lower_layout.addLayout(self.available_files_layout, stretch=1)

        self.comparison_files_layout = QVBoxLayout()
        add_label(self.comparison_files_layout, "Comparison List", TITLE_LABEL_STYLE).setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plotted_file_list = FileList()
        self.comparison_files_layout.addWidget(self.plotted_file_list)
        self.lower_layout.addLayout(self.comparison_files_layout, stretch=1)

        # Controls column
        self.controls_column = QVBoxLayout()
        
        self.status_pane = StatusPane()
        self.controls_column.addWidget(self.status_pane)

        self.plot_controls = PlotControls()
        self.controls_column.addWidget(self.plot_controls)

        self.tools = Tools()
        self.controls_column.addWidget(self.tools)
        
        self.controls_column.addStretch()
        self.lower_layout.addLayout(self.controls_column)

        # Coordinator
        logger.info("Initializing Coordinator")
        self.coordinator = Coordinator(
            self,
            [
                self.plot_controls,
                self.plot,
                self.tools,
                self.status_pane,
                self.single_scan_pane
            ],
            self.configuration.default_directory,
        )
        self.coordinator.attach(self.file_list, FileListType.TO_PLOT)
        self.coordinator.attach(self.plotted_file_list, FileListType.PLOTTED)
        
        logger.info("Calling coordinator.initialize")
        self.coordinator.initialize()
        logger.info("create_widgets finished")

    def diagnostic_mode(self):
        if hasattr(self, "_diagnostic_window") and self._diagnostic_window.isVisible():
            self._diagnostic_window.raise_()
            self._diagnostic_window.activateWindow()
            return
        self._diagnostic_window = DiagnosticWindow(self)

    def quit(self):
        clear_temp_files()
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
        clear_temp_files()
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
    import logging
    logger = logging.getLogger("ops")
    logger.info("Initializing QApplication...")
    app = QApplication(sys.argv)
    logger.info("Loading configuration...")
    configuration = load_configuration()
    logger.info("Creating EmittanceViewer window...")
    viewer = EmittanceViewer(configuration)
    logger.info("Showing window...")
    viewer.show()
    logger.info("Starting event loop.")
    sys.exit(app.exec())

if __name__ == "__main__":
    emittance_viewer()
