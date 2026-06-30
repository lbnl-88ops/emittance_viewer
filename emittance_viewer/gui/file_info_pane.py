from typing import List
import ttkbootstrap as ttk

import numpy as np

from ops.ecris.operations.emittance_scan.parameters import LinearScanParameters

from emittance_viewer.files.emittance_file import EmittanceScanFile


class FileInfoPane(ttk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._font = "TkDefaultFont"
        self._subtitle_font = (self._font, 12)
        self.file_labels = []
        self.file_frames = []
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(
            self, text="Scan information", font=self._subtitle_font, justify="center"
        ).pack()
        self.info_table = ttk.Frame(self)
        self.info_table.pack()

    def clear_info(self):
        [label.forget() for label in self.file_labels]
        [frame.forget() for frame in self.file_frames]

    def add_file_info(self, files: List[EmittanceScanFile]):
        self.clear_info()
        for file in files:
            file_label = ttk.Label(self, text=file.formatted_datetime)
            file_label.pack()
            self.file_labels.append(file_label)
            file_info = ttk.Frame(self)
            multiplier_label = ttk.Label(file_info, text="Voltage Amplifer setting:")
            multiplier_label.grid(row=0, column=0)
            
            try:
                mult = file.emittance_scan.extra_metadata[ "emittance_keithley_multiplier" ]
                multiplier_value = ttk.Label(
                    file_info,
                    text=mult
                )

                ttk.Label(file_info, text="Max current").grid(row=1, column=0)
                ttk.Label(file_info, text=f"{np.max(file.emittance_scan.data):.2e} A").grid(
                    row=1, column=1
                )
                utilization = 100*(np.max(file.emittance_scan.data)*10**mult)/10
                ttk.Label(file_info, text="Voltmeter range utilization").grid(row=2, column=0)
                ttk.Label(file_info, text=f"{utilization:.0f}%").grid(
                    row=2, column=1
                )
                if utilization < 10:
                    ttk.Label(file_info, text=f"Raising voltmeter amplifier to {mult + 1} enables use of {utilization*10:.0f}%").grid(row=3,column=0, columnspan=2)
            except KeyError:
                multiplier_value = ttk.Label(file_info, text="No data")
            multiplier_value.grid(row=0, column=1)

            file_info.pack()
            self.file_frames.append(file_info)
