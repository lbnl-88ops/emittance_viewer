from logging import info, debug
import tkinter as tk
from typing import Dict, List
from pathlib import Path

from matplotlib.artist import Artist
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Cursor
from ..plotting.plot_csd import create_figure, plot_file, Rescale
from emittance_viewer.files import EmittanceScanFile


class Plot(tk.Frame):
    def __init__(self, owner, *args, **kwargs):
        tk.Frame.__init__(self, owner, relief=tk.RAISED, *args, **kwargs)
        self._is_empty = True
        self._bg = None
        self.use_blitting = tk.BooleanVar(value=False)
        self._file_artists: Dict[str, List[Artist]] = {}
        self.create_widgets()

    def create_widgets(self):
        self._figure = create_figure()
        self.canvas = FigureCanvasTkAgg(self._figure, master=self)
        self.canvas.mpl_connect("draw_event", self.on_draw)
        self.canvas.mpl_connect("resize_event", self.update)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        # self.canvas.get_tk_widget().pack()
        self.cursor = Cursor(
            self._figure.gca(), useblit=True, color="blue", linewidth=0.5
        )

    def remove_file(self, file: Path):
        self._remove_files([file])

    def _remove_files(self, files: List[Path] | List[str]):
        ax = self.canvas.figure.gca()
        for to_remove in files:
            if isinstance(to_remove, Path):
                to_remove = to_remove.name
            try:
                artists = self._file_artists.pop(to_remove)
            except KeyError:
                info(f"Cannot remove file, not found: {to_remove}")
                info(self._file_artists)
                continue
            for a in artists:
                a.remove()
        if not self._file_artists:
            if ax.get_legend() is not None:
                ax.get_legend().remove()
            ax.set_prop_cycle(None)
        self.update()

    def clear_plot(self):
        self._remove_files(list(self._file_artists.keys()))

    def plot(self, file: EmittanceScanFile, rescaling_methods: List[Rescale]):
        debug(f"Plotting file {file.path}")
        artists = [
            a
            for a in [
                plot_file(self._figure.gca(), file, method)
                for method in rescaling_methods
            ]
            if a is not None
        ]
        if artists:
            debug("Artist was returned")
            self._file_artists[file.path.name] = artists
            self.update()

    def autoscale(self):
        ax = self._figure.gca()
        ax.relim(visible_only=True)
        ax.autoscale()
        ax.set_ybound(lower=0)
        self.update()

    def on_draw(self, event):
        self._bg = self.canvas.copy_from_bbox(self.canvas.figure.bbox)
        self._draw_animated()

    def _draw_animated(self, rescale: bool = False):
        fig = self.canvas.figure
        ax = fig.gca()
        for artists in self._file_artists.values():
            for artist in artists:
                fig.draw_artist(artist)

        # Determine how many elements are visible
        handles, labels = ax.get_legend_handles_labels()
        if handles and any(not l.startswith("_") for l in labels):
            ax.legend(handles, labels, fontsize=10)
        ax.set_ybound(lower=0)

    def update(self, *_):
        if self._bg is None:
            self.on_draw(None)
        else:
            self.canvas.restore_region(self._bg)
            self._draw_animated()
            if self.use_blitting.get():
                self.canvas.blit(self.canvas.figure.gca().clipbox)
            else:
                self.canvas.draw()
        self.canvas.flush_events()
