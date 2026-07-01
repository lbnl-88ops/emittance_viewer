import functools
import matplotlib
from cycler import cycler
from matplotlib.axes._base import _AxesBase
from emittance_viewer.gui.style.constants import (
    COLOR_BG, COLOR_PLOT_BG, COLOR_GRID, COLOR_TEXT, FONT_SANS
)

# Set the backend to QtAgg
matplotlib.use("QtAgg")

def applyPatch():
    # cycles through line styles when colours start repeating
    colourCycler = matplotlib.rcParams["axes.prop_cycle"]
    lineCycler = cycler(linestyle=["-", "--", ":", "-."])
    matplotlib.rcParams["axes.prop_cycle"] = lineCycler * colourCycler

    matplotlib.rcParams.update({
        "figure.facecolor": COLOR_BG,
        "axes.facecolor": COLOR_PLOT_BG,
        "axes.edgecolor": COLOR_GRID,
        "axes.labelcolor": COLOR_TEXT,
        "axes.grid": True,
        "grid.color": COLOR_GRID,
        "grid.linestyle": "--",
        "grid.alpha": 0.5,
        "text.color": COLOR_TEXT,
        "xtick.color": COLOR_TEXT,
        "ytick.color": COLOR_TEXT,
        "font.family": "sans-serif",
        "font.sans-serif": [f.strip() for f in FONT_SANS.split(",")],
        "font.size": 14,
    })

    # Non-GUI patches (keeping what's relevant)
    _AxesBase.clear = clear


original_clear = _AxesBase.clear

def clear(self, *args, **kwargs):
    if hasattr(self, "legend_") and self.legend_ is not None:
        self.legend_.axes = self.legend_.figure = None
    original_clear(self, *args, **kwargs)
