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
        ).pack(fill="x", pady=5)
        self.info_table = ttk.Frame(self)
        self.info_table.pack(fill="both", expand=True)

    def clear_info(self):
        for widget in self.info_table.winfo_children():
            widget.destroy()
        self.file_labels = []
        self.file_frames = []

    def add_file_info(self, files: List[EmittanceScanFile]):
        self.clear_info()
        n_files = len(files)
        if n_files == 0:
            return

        n_cols = 2 if n_files > 1 else 1
        self.info_table.columnconfigure(0, weight=1)
        if n_cols > 1:
            self.info_table.columnconfigure(1, weight=1)
        else:
            self.info_table.columnconfigure(1, weight=0)

        for i, file in enumerate(files):
            row = i // n_cols
            col = i % n_cols
            self.info_table.rowconfigure(row, weight=1)

            # Determine if utilization is low
            is_low_utilization = False
            mult = None
            max_current = None
            utilization = None
            try:
                mult = file.emittance_scan.extra_metadata["emittance_keithley_multiplier"]
                max_current = np.max(file.emittance_scan.data)
                utilization = 100 * (max_current * 10**mult) / 10
                if utilization < 10:
                    is_low_utilization = True
            except (KeyError, AttributeError, TypeError):
                pass

            # Style for the square
            bootstyle = "danger" if is_low_utilization else "default"
            
            # Container for each file's info (the "square")
            outer_frame = ttk.Frame(self.info_table, bootstyle=bootstyle, padding=10)
            outer_frame.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            self.file_frames.append(outer_frame)

            # Title: Timestamp
            title_style = "inverse-danger" if is_low_utilization else "secondary"
            ttk.Label(
                outer_frame, 
                text=file.formatted_datetime, 
                font=(self._font, 10, "bold"),
                bootstyle=title_style,
                anchor="center"
            ).pack(fill="x", pady=(0, 5))

            content_frame = ttk.Frame(outer_frame, bootstyle=bootstyle)
            content_frame.pack(fill="both", expand=True)

            if mult is not None:
                label_style = "inverse-danger" if is_low_utilization else "default"
                
                # Gain
                gain_frame = ttk.Frame(content_frame, bootstyle=bootstyle)
                gain_frame.pack(fill="x")
                ttk.Label(gain_frame, text="Gain:", bootstyle=label_style).pack(side="left")
                ttk.Label(gain_frame, text=f"10^{mult}", bootstyle=label_style).pack(side="right")

                # Max Current
                current_frame = ttk.Frame(content_frame, bootstyle=bootstyle)
                current_frame.pack(fill="x")
                ttk.Label(current_frame, text="Max I:", bootstyle=label_style).pack(side="left")
                ttk.Label(current_frame, text=f"{max_current:.2e} A", bootstyle=label_style).pack(side="right")

                # Utilization
                util_frame = ttk.Frame(content_frame, bootstyle=bootstyle)
                util_frame.pack(fill="x")
                ttk.Label(util_frame, text="Util:", bootstyle=label_style).pack(side="left")
                ttk.Label(util_frame, text=f"{utilization:.0f}%", bootstyle=label_style).pack(side="right")

                if is_low_utilization:
                    rec_text = f"Suggest: 10^{mult + 1} ({utilization * 10:.0f}%)"
                    ttk.Label(
                        outer_frame, 
                        text=rec_text, 
                        bootstyle="inverse-danger",
                        font=(self._font, 9, "italic"),
                        anchor="center"
                    ).pack(fill="x", pady=(5, 0))
            else:
                ttk.Label(
                    content_frame, 
                    text="No data", 
                    bootstyle="warning",
                    anchor="center"
                ).pack(fill="both", expand=True)
