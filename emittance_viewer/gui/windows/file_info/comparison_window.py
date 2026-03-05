from pathlib import Path
import tkinter as tk
from typing import List
from logging import info

import numpy as np
import ttkbootstrap as ttk

from ops.ecris.drivers.venus_plc import VENUS_PLC_DATA_DEFINITIONS, GAS_NAMES
from emittance_viewer.files import EmittanceScanFile
from emittance_viewer.gui.windows.vertical_scroll_frame import VerticalScrolledFrame


class FileComparisonWindow(tk.Toplevel):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, takefocus=True, *args, **kwargs)
        self._font = "TkDefaultFont"
        self._subtitle_font = (self._font, 12)
        self.title("CSD File Comparison")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.files: List[EmittanceScanFile] = []
        self.geometry(owner.winfo_geometry())
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._scrolling_frame = VerticalScrolledFrame(self)
        self._scrolling_frame.grid(column=0, row=0, sticky="nsew")
        self._info_frame = self._scrolling_frame.interior
        self._info_frame.columnconfigure(0, weight=1)
        self._info_frame.rowconfigure(0, weight=1)
        self.tree_view = ttk.Treeview(self._info_frame, height=100)
        self.tree_view.grid(column=0, row=0, sticky="nsew")

    def add_files(self, paths: List[Path]) -> None:
        info(f"Adding files {paths} to comparison window")
        self.files.extend([EmittanceScanFile(p, 1) for p in paths])
        self._render_data()

    def add_file(self, path: Path) -> None:
        info(f"Adding file {path} to comparison window")
        self.files.append(EmittanceScanFile(path, 1))
        self._render_data()

    def _render_data(self) -> None:
        labels_by_category = VENUS_PLC_DATA_DEFINITIONS.labels_by_category
        for category in labels_by_category:
            self.tree_view.insert("", "end", category, text=category)
        self.files = sorted(
            self.files,
            key=lambda file: file.raw_timestamp
            if file.raw_timestamp is not None
            else 0,
            reverse=True,
        )
        self.tree_view["columns"] = [file.raw_timestamp for file in self.files]

        for file in self.files:
            if file.raw_timestamp is None:
                column_id = str(file.path.name)
            else:
                column_id = str(file.raw_timestamp)
            self.tree_view.column(column_id, anchor=tk.E)
            self.tree_view.heading(column_id, text=file.formatted_datetime)
        csds = [file.csd for file in self.files]
        for category, labels in labels_by_category.items():
            for label in labels:

                def get_value(settings_dict):
                    if label.key not in settings_dict:
                        return ""
                    value = settings_dict[label.key]
                    if label.units == "boolean":
                        value = str(bool(value))
                    if label.key.startswith("gas_name"):
                        value = GAS_NAMES[int(value)]
                    return value

                units = f"({label.units})" if label.units != "nan" else ""
                values = [get_value(csd.settings) for csd in csds if csd is not None]

                self.tree_view.insert(
                    category,
                    "end",
                    text=f"{label.label} {units}",
                    values=values,
                    tags="values",
                )
        return

    def on_close(self):
        self.destroy()
