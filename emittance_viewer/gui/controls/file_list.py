from pathlib import Path
import tkinter as tk
from typing import List
import ttkbootstrap as ttk

from emittance_viewer.files import CSDFile, get_files
from emittance_viewer.gui.info_frame import FileInfoPane
from emittance_viewer.files.client import list_files
from ops.ecris.analysis.io.read_csd_file import _file_formatted_timestamp

BLUE = "#5200FF"
WHITE = "#FFFFFF"


class FileList(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self.owner = owner

        # Listbox to display files
        self.directory_label = tk.Label(self)

        self.files: List[Path] = []
        self.stringvar = tk.Variable(value=[""])
        self.file_listbox = tk.Listbox(
            self, width=25, selectmode=tk.SINGLE, listvariable=self.stringvar
        )
        self.file_listbox.pack(side="left", fill="y")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical")
        self.scrollbar.config(command=self.file_listbox.yview)
        self.scrollbar.pack(side="left", fill="y")
        self.file_listbox.config(yscrollcommand=self.scrollbar.set)

    def get_selected_file(self) -> Path | None:
        for i in self.file_listbox.curselection():
            return self.files[i]

    def fill_list_box(self, file_list: List[Path]):
        self.files = file_list
        self.file_listbox.delete(0, tk.END)
        filenames = [
            _file_formatted_timestamp(f)
            for f in file_list
            if _file_formatted_timestamp(f) != "UNKNOWN"
        ]
        if not filenames:
            self.stringvar.set(["No CSD files found"])
            self.file_listbox.configure(state=tk.DISABLED)
        else:
            self.stringvar.set(filenames)
            self.file_listbox.configure(state=tk.NORMAL)
