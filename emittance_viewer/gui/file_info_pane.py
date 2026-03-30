from typing import List
import ttkbootstrap as ttk

from ops.ecris.operations.emittance_scan.parameters import LinearScanParameters

from emittance_viewer.files.emittance_file import EmittanceScanFile


class FileInfoPane(ttk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._font = "TkDefaultFont"
        self._subtitle_font = (self._font, 12)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(
            self, text="Scan information", font=self._subtitle_font, justify="center"
        ).pack()
        self.info_table = ttk.Frame(self)
        self.info_table.pack()

    def list_information(self, files: List[EmittanceScanFile]):
        for i, file in enumerate(files):
            ttk.Label(self.info_table, text=file.timestamp).grid(column=i, row=0)
