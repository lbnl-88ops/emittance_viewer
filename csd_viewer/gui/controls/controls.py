import tkinter as tk

import ttkbootstrap as ttk


class FileListControls(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self.pad = 3.0
        self.create_widgets()

    def create_widgets(self):
        self.btChangeDirectory = ttk.Button(
            self, text="Choose directory", bootstyle="primary"
        )
        self.btRefresh = ttk.Button(
            self, text="Refresh file list", bootstyle="primary-outline"
        )
        self.btChangeMode = ttk.Button(self, text="", bootstyle="primary-outline")

        for loc, widget in {
            (0, 0): self.btChangeDirectory,
            (0, 1): self.btRefresh,
            (0, 2): self.btChangeMode,
        }.items():
            widget.grid(
                row=loc[0], column=loc[1], padx=self.pad, pady=self.pad, sticky="nsew"
            )


class PlotControls(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self.pad = 3.0
        self.big_button_size = 2
        self._font = "TkDefaultFont"
        self._subtitle_font = (self._font, 12)
        self.create_widgets()

    def create_widgets(self):
        self.widgets = []
        self.btPlotCSD = ttk.Button(self, text="Plot CSD", bootstyle="success")
        self.btAutoScale = ttk.Button(
            self, text="Reset Scale", bootstyle="success-outline"
        )
        self.btRemoveFromPlot = ttk.Button(
            self, text="Remove from plot", state="disabled", bootstyle="outline+danger"
        )
        self.btClearPlot = ttk.Button(self, text="Clear Plot", bootstyle="outline")
        for loc, widget in {
            (0, 0): self.btPlotCSD,
            (0, 1): self.btAutoScale,
            (0, 2): self.btRemoveFromPlot,
            (0, 3): self.btClearPlot,
        }.items():
            widget.grid(
                row=loc[0], column=loc[1], padx=self.pad, pady=self.pad, sticky="nsew"
            )

    def activate_buttons(self, can_plot: bool = False, can_remove: bool = False):
        if can_plot:
            self.btPlotCSD.config(state="normal")  # Enable Plot button
        else:
            self.btPlotCSD.config(state="disabled")
        if can_remove:
            self.btRemoveFromPlot.config(state="normal")  # Enable Remove button
        else:
            self.btRemoveFromPlot.config(state="disabled")


class Tools(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(owner, *args, **kwargs)
        self._owner = owner
        self._font = "TkDefaultFont"
        self._subtitle_font = (self._font, 12)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Tools", font=self._subtitle_font, justify="center").pack()
        self.button_frame = tk.Frame(self)
        self.button_frame.pack()
        self.btOpenComparisonWindow = ttk.Button(
            self.button_frame,
            text="Compare plotted files",
            bootstyle="outline+success",
            state=tk.DISABLED,
        )
        self.btOpenComparisonWindow.pack()
