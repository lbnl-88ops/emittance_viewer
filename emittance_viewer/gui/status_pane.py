from enum import Enum, auto

import ttkbootstrap as ttk
import tkinter as tk

from emittance_viewer.gui.controls.controls import FileListControls

_FONT = "TkDefaultFont"
_MODE_FONT = (_FONT, 12, "bold")


class FileMode:
    REMOTE = auto()
    LOCAL = auto()


class StatusPane(ttk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self.strWarning = ttk.StringVar(value="")
        self.strStatus = tk.StringVar(value="")
        self.strFileMode = tk.StringVar(value="")
        self.create_widgets()

    def create_widgets(self):
        self.lblFileMode = ttk.Label(
            self, textvariable=self.strFileMode, font=_MODE_FONT
        )
        self.lblFileMode.pack()
        self.lblStatus = ttk.Label(self, textvariable=self.strStatus)
        self.lblStatus.pack()
        self.lblWarning = ttk.Label(self, textvariable=self.strWarning)
        self.lblWarning.pack()
        self.file_list_controls = FileListControls(self)
        self.file_list_controls.pack()

    def set_file_mode(self, mode: FileMode, info: str):
        match mode:
            case FileMode.REMOTE:
                file_mode = "Remote"
            case _:
                file_mode = "Local"
        self.strFileMode.set(f"File mode: {file_mode}")
        self.strStatus.set(info)
