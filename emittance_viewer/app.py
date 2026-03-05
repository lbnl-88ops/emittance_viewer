"""Main emittance Viewer App"""

import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk as ttk_main
from tkinter import messagebox
from tkinter import filedialog
import matplotlib
import platform
import os
import subprocess

import ttkbootstrap as ttk


from .coordinator import Coordinator, FileListType
from emittance_viewer.files.emittance_file import CSDFile, export_to_file
from emittance_viewer.files.configuration import (
    AppConfiguration,
    create_configuration,
    save_configuration,
    CONFIG_FILEPATH,
)
from emittance_viewer.gui.style.patchMatplotlib import applyPatch
from emittance_viewer.files.client import clear_temp_files
from emittance_viewer.gui.status_pane import StatusPane
from emittance_viewer.status_bar import StatusBarSingleton

from .gui import (
    Tools,
    FileList,
    PlotControls,
    Plot,
    FileListControls,
    AppMenu,
    DiagnosticWindow,
    FileInfoPane,
)
from .gui.windows.vertical_scroll_frame import VerticalScrolledFrame


__version__ = "0.1.0"

matplotlib.rc("font", size=14)
applyPatch()

logger = logging.getLogger("ops")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class EmittanceViewer(ttk.Window):
    def __init__(self, configuration: AppConfiguration | None):
        super().__init__()
        self.configuration = configuration
        if self.configuration is None:
            self.configuration = create_configuration()

        if (
            self.configuration.window_x is not None
            and self.configuration.window_y is not None
        ):
            self.geometry(
                f"{self.configuration.window_width}x{self.configuration.window_height}+{self.configuration.window_x}+{self.configuration.window_y}"
            )
        else:
            self.geometry(
                f"{self.configuration.window_width}x{self.configuration.window_height}"
            )

        self.title(f"Emittance Viewer (v{__version__})")
        self.pad = 5.0
        self.create_widgets()
        self.create_menu()
        self._info_visible = False
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.update()
        if self.configuration.sash_position is not None:
            try:
                self.paned_window.sashpos(0, self.configuration.sash_position)
            except Exception as e:
                logging.error(f"Error setting sash position: {e}")
        self.minsize(800, 600)

    def quit(self):
        # Save geometry
        self.configuration.window_width = self.winfo_width()
        self.configuration.window_height = self.winfo_height()
        self.configuration.window_x = self.winfo_x()
        self.configuration.window_y = self.winfo_y()

        try:
            self.configuration.sash_position = self.paned_window.sashpos(0)
        except Exception as e:
            logging.error(f"Error getting sash position: {e}")

        save_configuration(self.configuration)

        clear_temp_files()
        self.plot.destroy()
        self.destroy()

    def create_menu(self):
        self.menu = AppMenu(
            self, self.plot.use_blitting, self.coordinator.rescale_using_oxygen
        )
        self.config(menu=self.menu)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.status_bar = ttk.Frame(self)
        self.status_bar.pack(side=tk.TOP, fill=tk.X, expand=False)

        self.status_label = ttk.Label(
            self.status_bar,
            textvariable=StatusBarSingleton().get_status_var(),
            bootstyle="secondary",
            anchor=tk.W,
        )

        self.status_label.pack(side=tk.LEFT)
        self.paned_window = ttk.Panedwindow(
            self.main_frame,
            orient=tk.HORIZONTAL,
            # bootstyle="secondary",
        )

        self.paned_window.pack(fill=tk.BOTH, expand=True)
        ttk_main.Style().configure(
            "Sash",
            sashthickness=10,
            gripcount=4,
        )

        self.plot = Plot(self.paned_window)
        self.control_pane = VerticalScrolledFrame(self.paned_window)

        self.paned_window.add(self.plot, weight=3)
        self.paned_window.add(self.control_pane, weight=1)  # , minsize=400)
        # self.btToggleFileInfo.pack(fill="y", side="left")

        self.status_pane = StatusPane(self.control_pane.interior)
        self.file_list_pane = ttk.Frame(self.control_pane.interior)

        self.file_list = FileList(self.file_list_pane)
        self.plotted_file_list = FileList(self.file_list_pane)

        self.plot_controls = PlotControls(self.control_pane.interior)
        self.tools = Tools(self.control_pane.interior)

        self.status_pane.pack()
        self.file_list_pane.pack()
        ttk.Label(self.file_list_pane, text="Available Files", justify="center").grid(
            row=0, column=0, sticky="n"
        )
        ttk.Label(self.file_list_pane, text="Plotted Files", justify="center").grid(
            row=0, column=1, sticky="n"
        )
        self.file_list.grid(row=1, column=0, sticky="n", padx=10, pady=(0, 10))
        self.plotted_file_list.grid(row=1, column=1, sticky="n", padx=10, pady=(0, 10))
        self.plot_controls.pack()
        self.tools.pack()
        self.strToggleInfoText = ttk.StringVar(value=">>")

        self.coordinator = Coordinator(
            self,
            [
                self.plot_controls,
                self.plot,
                self.tools,
            ],
            self.configuration.default_directory,
        )
        self.coordinator.attach(self.file_list, FileListType.TO_PLOT)
        self.coordinator.attach(self.plotted_file_list, FileListType.PLOTTED)
        self.coordinator.attach(self.status_pane)
        self.coordinator.initialize()

    def export_data(self):
        # if len(self.plot.plotted_files()) > 1:
        # messagebox.showerror('Error', 'Can only export a single file. Please remove all but one datafile from the plot.')
        # return
        if len(self.plot.plotted_files()) == 0:
            messagebox.showerror("Error", "No plotted data to export.")
            return
        else:
            export_file = filedialog.asksaveasfile(
                title="Save exported data as",
                defaultextension=".csv",
                filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
                initialdir=self.configuration.default_directory,
            )
            if export_file is not None:
                try:
                    export_to_file(export_file, self.plot.plotted_files())
                    messagebox.showinfo("Success", "Export successful.")
                except ValueError as e:
                    messagebox.showerror("Error", f"Error exporting: {e}")

    def diagnostic_mode(self):
        self._diagnostic_window = DiagnosticWindow(self)

    def toggle_rescale(self):
        if not self.coordinator.rescale_using_oxygen.get():
            logging.info("Turning off oxygen rescaling")
            self.status_pane.strWarning.set("⚠️ Warning: Not rescaling!")
            self.status_pane.lblWarning.config(bootstyle="inverse-danger")
        else:
            logging.info("Turning on oxygen rescaling")
            self.status_pane.strWarning.set("")
            self.status_pane.lblWarning.config(bootstyle="danger")

    def toggle_blitting(self):
        logging.info(self.plot.use_blitting.get())
        if self.plot.use_blitting.get():
            if not messagebox.askokcancel(
                "Warning",
                """Activating blitting may cause some plot elements to not update automatically unless resized, are you sure you want to do this?""",
            ):
                self.plot.use_blitting.set(False)

    def _open_directory(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", path])
        else:
            messagebox.showerror(
                "Error", "Cannot open directory: unsupported operating system"
            )

    def open_config_directory(self):
        self._open_directory(CONFIG_FILEPATH)

    def open_data_directory(self):
        self._open_directory(self.default_path)
