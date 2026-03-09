from enum import Enum, auto
from logging import getLogger
from pathlib import Path
from tkinter import filedialog
from typing import Any, List, Optional
import tkinter as tk
from tkinter import messagebox
import os
import time
from datetime import datetime

from emittance_viewer.files.emittance_file import EmittanceScanFile
from emittance_viewer.status_bar import update_status_bar
from emittance_viewer.gui import (
    Tools,
    FileListControls,
    PlotControls,
    FileList,
    Plot,
    FileComparisonWindow,
)
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


# TODO: roll this into WidgetType
class FileListType(Enum):
    TO_PLOT = auto()
    PLOTTED = auto()


class Coordinator:
    def __init__(self, root_window, objects: Any | List[Any], default_directory: Path):
        if not isinstance(objects, List):
            objects = [objects]
        self._root_window = root_window
        self.attach_objects(objects)
        self.plotted_files = []
        self.mode = FileMode.LOCAL
        self._last_updated = "N/A"
        self._files_available = 0
        self._current_directory = default_directory

    @property
    def plotted_filepaths(self) -> List[Path]:
        return [file.path for file in self.plotted_files]

    def attach_objects(self, objects: List[Any]) -> None:
        for o in objects:
            self.attach(o)

    def attach(self, object: Any, key: Optional[Any] = None) -> None:
        match object:
            case PlotControls():
                self._plot_controls = object
            case FileList():
                match key:
                    case FileListType.PLOTTED:
                        self._plotted_file_list = object
                    case _:
                        self._file_list = object
            case FileListControls():
                self._file_list_controls = object
            case Plot():
                self._plot = object
            case StatusPane():
                self._status_pane = object
            case Tools():
                self._tools = object
            case _:
                raise RuntimeError(f"Coordinator passed bad object {object}")

    def _configure_objects(self) -> None:
        self._file_list.file_listbox.bind(
            "<<ListboxSelect>>", self.update_button_states
        )
        self._plotted_file_list.file_listbox.bind(
            "<<ListboxSelect>>", self.update_button_states
        )
        self._status_pane.file_list_controls.btRefresh.config(
            command=self.refresh_file_lists
        )
        self._status_pane.file_list_controls.btChangeDirectory.config(
            command=self.choose_directory
        )
        self._plot_controls.btClearPlot.config(command=self.clear_plot)
        self._plot_controls.btRemoveFromPlot.config(command=self.remove_from_plot)
        self._plot_controls.btPlotScan.config(command=self.plot_file)
        self._status_pane.file_list_controls.btChangeMode.config(
            command=self.toggle_mode
        )
        self._tools.btOpenComparisonWindow.config(command=self.open_comparison_window)

    def open_comparison_window(self, *_):
        self._comparison_window = FileComparisonWindow(self._root_window)
        if self.mode == FileMode.REMOTE:
            files_to_compare = [
                Path(TEMP_FOLDER) / file.name for file in self.plotted_filepaths
            ]
        else:
            files_to_compare = self.plotted_filepaths
        self._comparison_window.add_files(files_to_compare)

    def update_button_states(self, *_):
        if self._file_list.file_listbox.curselection() and len(self.plotted_files) < 4:
            self._plot_controls.activate_buttons(True, False)  # Can plot
        elif self._plotted_file_list.file_listbox.curselection():
            self._plot_controls.activate_buttons(False, True)  # Can remove
        else:
            self._plot_controls.activate_buttons(False, False)

    def update_connection_status(self) -> None:
        update_status = (
            f"Last update {self._last_updated}, {self._files_available} files found"
        )
        if self.mode == FileMode.REMOTE:
            self._status_pane.set_file_mode(
                FileMode.REMOTE, f"Connected to {API_URL}\n{update_status}"
            )
            self._status_pane.file_list_controls.btChangeMode.config(
                text="Disconnect from remote"
            )
        if self.mode == FileMode.LOCAL:
            self._status_pane.set_file_mode(
                FileMode.LOCAL,
                f"Browsing directory {self._current_directory}\n{update_status}",
            )
            self._status_pane.file_list_controls.btChangeMode.config(
                text="Connect to remote"
            )

    def initialize(self) -> None:
        self._configure_objects()
        self.update_connection_status()
        self.refresh_file_lists()
        update_status_bar("Initialized")

    def choose_directory(self, *_):
        new_directory = filedialog.askdirectory(
            title="Choose a directory", mustexist=True
        )
        try:
            self._current_directory = Path(new_directory)
            self.refresh_file_lists()
        except Exception as e:
            messagebox.showerror("Failed to open directory: e")

    def toggle_mode(self, *_):
        match self.mode:
            case FileMode.LOCAL:
                self.mode = FileMode.REMOTE
            case FileMode.REMOTE:
                self.mode = FileMode.LOCAL
        self.refresh_file_lists()
        self.update_connection_status()

    def clear_plot(self, *_):
        self.plotted_files = []
        self.refresh_file_lists()
        self._plot.plot([])
        clear_temp_files()
        update_status_bar("Plot cleared.")

    def plot_file(self):
        if len(self.plotted_files) == 4:
            messagebox.showerror(
                "Error",
                "Only four emittance scans can be shown at one time, please remove a plot.",
            )
            return
        file = self._file_list.get_selected_file()
        if file is not None:
            if self.mode == FileMode.REMOTE:
                emittance_file = download_file(file)
            else:
                emittance_file = file
            file_size = os.path.getsize(emittance_file)
            if file_size < 1:
                messagebox.showerror(
                    "File invalid",
                    "Invalid file: file size is 0. CSD may still be in progress.",
                )
                return
            file = EmittanceScanFile(emittance_file, file_size)
            self.plotted_files.append(file)
            self._plot.plot(self.plotted_files)
            self.refresh_file_lists()

    def remove_from_plot(self, *_):
        file = self._plotted_file_list.get_selected_file()
        if file is not None:
            for plotted_file in self.plotted_files:
                if plotted_file.path == file:
                    self.plotted_files.remove(plotted_file)
                    break
            self._plot.plot(self.plotted_files)
            self.refresh_file_lists()

    def refresh_file_lists(self, *_):
        current_time = time.time()
        dt_object = datetime.fromtimestamp(current_time)
        self._last_updated = dt_object.strftime("%Y-%m-%d %H:%M")
        match self.mode:
            case FileMode.REMOTE:
                found_files = list_files()
                if not found_files:
                    messagebox.showerror("Error", "Failed to connect to remote server.")
                    self.mode = FileMode.LOCAL
                    self.refresh_file_lists()
                    return
                else:
                    self._status_pane.file_list_controls.btChangeDirectory.config(
                        state=tk.DISABLED
                    )
            case _:
                found_files = list_local_files(self._current_directory)
                self._status_pane.file_list_controls.btChangeDirectory.config(
                    state=tk.ACTIVE
                )
        self._files_available = len(found_files)
        files = [
            f for f in reversed(sorted(found_files)) if f not in self.plotted_filepaths
        ]
        self._file_list.fill_list_box(files)
        self._plotted_file_list.fill_list_box(self.plotted_filepaths)
        if self.plotted_filepaths:
            self._tools.btOpenComparisonWindow.config(state=tk.ACTIVE)
        else:
            self._tools.btOpenComparisonWindow.config(state=tk.DISABLED)
        self.update_connection_status()
        self.update_button_states()
        update_status_bar("File list refreshed.")
