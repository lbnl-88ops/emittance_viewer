import tkinter as tk
from typing import List

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ..plotting.plot_emittance_scan import create_figure, plot_file
from emittance_viewer.files import EmittanceScanFile


class Plot(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        tk.Frame.__init__(self, owner, relief=tk.RAISED, *args, **kwargs)
        self.create_widgets(n_plots=0)

    def create_widgets(self, n_plots: int):
        self._figure, self._axs = create_figure(n_plots)
        self.canvas = FigureCanvasTkAgg(self._figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def clear_plot(self):
        self.canvas.get_tk_widget().destroy()

    def plot(self, files: List[EmittanceScanFile]):
        self.clear_plot()
        self.create_widgets(len(files))
        for ax, file in zip(self._axs, files):
            plot_file(ax, file)
