import functools
import matplotlib
from cycler import cycler
from matplotlib import offsetbox
from matplotlib.axes import Axes
from matplotlib.axes._base import _AxesBase

# Set the backend to QtAgg
matplotlib.use("QtAgg")

def applyPatch():
    # cycles through line styles when colours start repeating
    colourCycler = matplotlib.rcParams["axes.prop_cycle"]
    lineCycler = cycler(linestyle=["-", "--", ":", "-."])
    matplotlib.rcParams["axes.prop_cycle"] = lineCycler * colourCycler

    # Non-GUI patches (keeping what's relevant)
    _AxesBase.clear = clear

original_clear = _AxesBase.clear

def clear(self, *args, **kwargs):
    if hasattr(self, "legend_") and self.legend_ is not None:
        self.legend_.axes = self.legend_.figure = None
    original_clear(self, *args, **kwargs)
