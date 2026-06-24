from pathlib import Path
import tkinter as tk
from typing import List
import ttkbootstrap as ttk

from ops.ecris.analysis.io.read_emittance_scan_file import _file_formatted_timestamp

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
        # Capture current scroll position and selection
        yview = self.file_listbox.yview()
        selection = self.file_listbox.curselection()

        self.files = file_list
        self.file_listbox.delete(0, tk.END)
        filenames = [
            _file_formatted_timestamp(f)
            for f in file_list
            if _file_formatted_timestamp(f) != "UNKNOWN"
        ]
        if not filenames:
            self.stringvar.set(["No files found"])
            self.file_listbox.configure(state=tk.DISABLED)
        else:
            self.stringvar.set(filenames)
            self.file_listbox.configure(state=tk.NORMAL)
            
            # Restore scroll position
            if yview:
                self.file_listbox.yview_moveto(yview[0])
            
            # Restore selection
            for idx in selection:
                if idx < len(filenames):
                    self.file_listbox.selection_set(idx)
