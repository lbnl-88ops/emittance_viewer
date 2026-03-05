import tkinter as tk
import ttkbootstrap as ttk
from typing import List

from emittance_viewer.files import CSDFile

from .csd_info import CSDInfoFrame
from .info_to_display import _FRAMES, _COLUMNS, _INFO_ROWS

_FONT = "TkDefaultFont"
_COLUMN_FONT = (_FONT, 10)


class FileInfoPane(ttk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self._font = "TkDefaultFont"
        self._title_font = (self._font, 14)
        self._subtitle_font = (self._font, 12)
        self._info_widgets = []
        self._file_info = {}
        self._csd_info_frames: List[CSDInfoFrame] = []
        self.visible = tk.BooleanVar(value=False)
        self.visible.trace_add("write", self.set_visible)

        self.create_widgets()

    def toggle_visibility(self):
        self.visible.set(not self.visible.get())

    def set_visible(self, *args, **kwargs):
        if not self.visible.get():
            self.pack_forget()
            self._owner.strToggleInfoText.set(">>")
        else:
            self.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            self._owner.strToggleInfoText.set("<<")

    def create_widgets(self):
        self.canvas = ttk.Canvas(self)
        tk.Label(self.canvas, text="File Info", font=self._title_font).pack()
        self._info_frame = ttk.Frame(self.canvas)
        for i, (name, attribute) in enumerate(
            zip(["Filename", "Time Stamp"], ["filename", "timestamp"])
        ):
            self._file_info[attribute] = tk.StringVar(value="No file selected")
            frInfo = ttk.Frame(self.canvas)
            ttk.Label(frInfo, text=name).pack(side="left")
            ttk.Label(frInfo, textvariable=self._file_info[attribute]).pack(
                side="right"
            )
            frInfo.pack(fill="x")
        self._info_frame.pack()

        tk.Label(self.canvas, text="CSD Info", font=self._title_font).pack()

        for title, csd_info_rows, column_titles in zip(_FRAMES, _INFO_ROWS, _COLUMNS):
            self._csd_info_frames.append(
                CSDInfoFrame(self.canvas, title, csd_info_rows, column_titles)
            )
            self._csd_info_frames[-1].pack(fill="x")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical")
        self.canvas.pack(side="left", fill="both", padx=10)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        self._controls_frame = ttk.Frame(self)

        self._controls_frame.pack()

    def update_info(self, file: CSDFile | None = None):
        if file is None:
            for attribute, variable in self._file_info.items():
                variable.set("No file selected")
            for frame in self._csd_info_frames:
                frame.update_csd_info()
        elif not file.valid:
            for attribute, variable in self._file_info.items():
                variable.set("Invalid file")
            for frame in self._csd_info_frames:
                frame.update_csd_info()
        else:
            for attribute, variable in self._file_info.items():
                variable.set(getattr(file, attribute))
            csd = file.csd
            for frame in self._csd_info_frames:
                frame.update_csd_info(csd)
