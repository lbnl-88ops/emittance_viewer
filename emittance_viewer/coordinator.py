from enum import Enum, auto
from logging import getLogger
from pathlib import Path
from typing import Any, List, Optional
import os
import time
from datetime import datetime

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from emittance_viewer.files.emittance_file import EmittanceScanFile
from emittance_viewer.status_bar import update_status_bar
from emittance_viewer.gui import (
    Tools,
    PlotControls,
    FileList,
    Plot,
    FileComparisonWindow,
)
from emittance_viewer.gui.single_scan_pane import SingleScanPane
from emittance_viewer.gui.status_pane import StatusPane, FileMode
from emittance_viewer.files.client import (
    list_files,
    download_file,
    clear_temp_files,
    API_URL,
    list_local_files,
    TEMP_FOLDER,
)

_log = getLogger(__name__)


class FileListType(Enum):
    TO_PLOT = auto()
    PLOTTED = auto()


class Coordinator:
    def __init__(self, root_window, objects: Any | List[Any], default_directory: Path):
        if not isinstance(objects, List):
            objects = [objects]
        self._root_window = root_window
        self.plotted_files = []
        self.active_file = None
        self.mode = FileMode.LOCAL
        self._last_updated = "N/A"
        self._files_available = 0
        self._current_directory = default_directory
        
        self._plot_controls = None
        self._file_list = None
        self._plotted_file_list = None
        self._plot = None
        self._status_pane = None
        self._tools = None
        self._single_scan_pane = None

        self.attach_objects(objects)

    @property
    def plotted_filepaths(self) -> List[Path]:
        return [file.path for file in self.plotted_files]

    def attach_objects(self, objects: List[Any]) -> None:
        for o in objects:
            self.attach(o)

    def attach(self, object: Any, key: Optional[Any] = None) -> None:
        if isinstance(object, PlotControls):
            self._plot_controls = object
        elif isinstance(object, FileList):
            if key == FileListType.PLOTTED:
                self._plotted_file_list = object
            else:
                self._file_list = object
        elif isinstance(object, Plot):
            self._plot = object
        elif isinstance(object, StatusPane):
            self._status_pane = object
        elif isinstance(object, Tools):
            self._tools = object
        elif isinstance(object, SingleScanPane):
            self._single_scan_pane = object
        else:
            # Skip if it doesn't match known types (could be during initialization)
            pass

    def _configure_objects(self) -> None:
        if self._file_list:
            self._file_list.selectionChanged.connect(self.update_active_scan)
            
        if self._status_pane:
            self._status_pane.file_list_controls.btRefresh.clicked.connect(self.refresh_file_lists)
            self._status_pane.file_list_controls.btChangeDirectory.clicked.connect(self.choose_directory)
            self._status_pane.file_list_controls.btChangeMode.clicked.connect(self.toggle_mode)
            
        if self._plot_controls:
            self._plot_controls.btClearPlot.clicked.connect(self.clear_plot)
            self._plot_controls.btRemoveFromPlot.clicked.connect(self.remove_from_plot)
            self._plot_controls.btPlotScan.clicked.connect(self.plot_active_file)
            
        if self._tools:
            self._tools.btOpenComparisonWindow.clicked.connect(self.open_comparison_window)

        if self._single_scan_pane:
            self._single_scan_pane.fittingChanged.connect(self.replot_active_scan)

    def replot_active_scan(self):
        if self.active_file:
            self.update_active_scan()

    def update_active_scan(self):
        file = self._file_list.get_selected_file()
        if file is not None:
            if self.mode == FileMode.REMOTE:
                emittance_file = download_file(file)
                if emittance_file is None:
                    return
            else:
                emittance_file = file
            
            file_size = os.path.getsize(emittance_file)
            if file_size < 1:
                return

            self.active_file = EmittanceScanFile(emittance_file, file_size)
            
            fitting_params = {}
            if self._single_scan_pane:
                fitting_params = self._single_scan_pane.get_fitting_params()
            
            rms_emittance = None
            if self._single_scan_pane:
                from emittance_viewer.plotting.plot_emittance_scan import calculate_extended_data
                data, rms_emittance = calculate_extended_data(self.active_file, **fitting_params)
                self._single_scan_pane.update_data(data, rms_emittance,
                                                   self.active_file)
            
            if self._plot:
                self._plot.plot([self.active_file], rms_emittance=rms_emittance)
        
        self.update_button_states()

    def plot_active_file(self):
        """Adds the active file to the plotted_files list for comparison"""
        if self.active_file:
            is_already_added = any(f.path == self.active_file.path for f in self.plotted_files)
            if not is_already_added:
                if len(self.plotted_files) >= 4:
                     QMessageBox.warning(self._root_window, "Warning", "Max 4 files for comparison.")
                     return
                self.plotted_files.append(self.active_file)
                self.update_button_states()
                update_status_bar(f"Added {self.active_file.filename} to comparison.")

    def open_comparison_window(self):
        if hasattr(self, "_comparison_window") and self._comparison_window.isVisible():
            self._comparison_window.raise_()
            self._comparison_window.activateWindow()
            return
            
        self._comparison_window = FileComparisonWindow(self._root_window)
        if self.mode == FileMode.REMOTE:
            files_to_compare = [
                Path(TEMP_FOLDER) / file.path.name for file in self.plotted_files
            ]
        else:
            files_to_compare = self.plotted_filepaths
        self._comparison_window.add_files(files_to_compare)

    def update_button_states(self):
        is_already_added = False
        if self.active_file:
            is_already_added = any(f.path == self.active_file.path for f in self.plotted_files)

        can_plot = self.active_file is not None and len(self.plotted_files) < 4 and not is_already_added
        can_remove = is_already_added
        
        if self._plot_controls:
            self._plot_controls.activate_buttons(can_plot, can_remove)
            
        if self._tools:
            count = len(self.plotted_files)
            self._tools.btOpenComparisonWindow.setText(f"Compare plotted files ({count})")
            self._tools.btOpenComparisonWindow.setEnabled(count > 0)

    def update_connection_status(self) -> None:
        if not self._status_pane:
            return
            
        update_status = (
            f"Last update {self._last_updated}, {self._files_available} files found"
        )
        if self.mode == FileMode.REMOTE:
            self._status_pane.set_file_mode(
                FileMode.REMOTE, f"Connected to {API_URL}\n{update_status}"
            )
            self._status_pane.file_list_controls.btChangeMode.setText(
                "Disconnect from remote"
            )
        if self.mode == FileMode.LOCAL:
            self._status_pane.set_file_mode(
                FileMode.LOCAL,
                f"Browsing directory {self._current_directory}\n{update_status}",
            )
            self._status_pane.file_list_controls.btChangeMode.setText(
                "Connect to remote"
            )

    def initialize(self) -> None:
        _log.info("Coordinator.initialize started")
        self._configure_objects()
        _log.info("Objects configured")
        self.update_connection_status()
        _log.info("Connection status updated")
        self.refresh_file_lists()
        _log.info("File lists refreshed")
        update_status_bar("Initialized")
        _log.info("Coordinator.initialize finished")

    def choose_directory(self):
        new_directory = QFileDialog.getExistingDirectory(
            self._root_window, "Choose a directory", str(self._current_directory)
        )
        if new_directory:
            try:
                self._current_directory = Path(new_directory)
                self.refresh_file_lists()
            except Exception as e:
                QMessageBox.critical(self._root_window, "Error", f"Failed to open directory: {e}")

    def toggle_mode(self):
        match self.mode:
            case FileMode.LOCAL:
                self.mode = FileMode.REMOTE
            case FileMode.REMOTE:
                self.mode = FileMode.LOCAL
        self.refresh_file_lists()
        self.update_connection_status()

    def clear_plot(self):
        self.plotted_files = []
        self.active_file = None
        self.refresh_file_lists()
        if self._plot:
            self._plot.plot([])
        clear_temp_files()
        if self._single_scan_pane:
            self._single_scan_pane.update_data({}, None, None)
        update_status_bar("Cleared.")

    def plot_file(self):
        if len(self.plotted_files) == 4:
            QMessageBox.critical(
                self._root_window,
                "Error",
                "Only four emittance scans can be shown at one time, please remove a plot.",
            )
            return
        file = self._file_list.get_selected_file()
        if file is not None:
            if self.mode == FileMode.REMOTE:
                emittance_file = download_file(file)
                if emittance_file is None:
                    QMessageBox.critical(
                        self._root_window,
                        "Error",
                        "Failed to download file from remote server.",
                    )
                    return
            else:
                emittance_file = file
            file_size = os.path.getsize(emittance_file)
            if file_size < 1:
                QMessageBox.critical(
                    self._root_window,
                    "File invalid",
                    "Invalid file: file size is 0. CSD may still be in progress.",
                )
                return
            file_obj = EmittanceScanFile(emittance_file, file_size)
            self.plotted_files.append(file_obj)
            if self._plot:
                self._plot.plot(self.plotted_files)
            self.refresh_file_lists()

    def remove_from_plot(self):
        if self.active_file:
            for plotted_file in self.plotted_files:
                if plotted_file.path == self.active_file.path:
                    self.plotted_files.remove(plotted_file)
                    update_status_bar(f"Removed {self.active_file.filename} from comparison.")
                    break
            self.update_button_states()

    def refresh_file_lists(self):
        _log.info(f"refresh_file_lists started, mode={self.mode}")
        current_time = time.time()
        dt_object = datetime.fromtimestamp(current_time)
        self._last_updated = dt_object.strftime("%Y-%m-%d %H:%M")
        match self.mode:
            case FileMode.REMOTE:
                _log.info("Fetching remote files...")
                found_files = list_files()
                _log.info(f"Found {len(found_files)} remote files")
                if not found_files:
                    _log.warning("No remote files found or connection failed")
                    # QMessageBox.critical(self._root_window, "Error", "Failed to connect to remote server.")
                    self.mode = FileMode.LOCAL
                    self.refresh_file_lists()
                    return
                else:
                    if self._status_pane:
                        self._status_pane.file_list_controls.btChangeDirectory.setEnabled(False)
            case _:
                _log.info(f"Listing local files in {self._current_directory}")
                found_files = list_local_files(self._current_directory)
                _log.info(f"Found {len(found_files)} local files")
                if self._status_pane:
                    self._status_pane.file_list_controls.btChangeDirectory.setEnabled(True)
        
        self._files_available = len(found_files)
        _log.info("Sorting files")
        files = list(reversed(sorted(found_files)))
        
        if self._file_list:
            _log.info("Filling file listbox")
            self._file_list.fill_list_box(files)
            
        self.update_connection_status()
        self.update_button_states()
        _log.info("refresh_file_lists finished")
