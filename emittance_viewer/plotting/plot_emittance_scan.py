import numpy as np

from logging import info, error
import matplotlib.pyplot as plt
from ops.ecris.devices.motor_controller_specification import Axis
from emittance_viewer.files import EmittanceScanFile

from ops.ecris.analysis.plot.emittance_scan import plot_file as plot_emittance
from ops.ecris.analysis.emittance_scan.rms_emittance import (
    RMSEmittance,
    calculate_rms_emittance,
)

VENUS_OFFSET = 3.5

def create_figure(n_subplots: int = 0):
    match n_subplots:
        case 0 | 1:
            layout = (1, 1)
        case 2:
            layout = (1, 2)
        case 3 | 4:
            layout = (2, 2)
        case _:
            raise RuntimeError(f"Unsupported n_subplots: {n_subplots}")
    fig, axs = plt.subplots(layout[0], layout[1], squeeze=False)
    axs = list(axs.flatten())
    for ax in axs:
        font_size = 10
        ax.tick_params(labelsize=font_size)
        ax.set_xlabel(f"Position [mm]")
        ax.set_ylabel(f"Divergence [mrad]")
        # ax.colorbar(label="Current [nA]")
    return fig, axs


def plot_file(ax, file: EmittanceScanFile, offset: bool = True, sigma_clip = True):
    emittance_scan = file.emittance_scan

    if emittance_scan is None:
        info(f"File object: {file.path} has no emittance scan.")
        return None

    if file.corrected:
        offset = False
        sigma_clip = False
    try:
        plot_emittance(ax, emittance_scan, offset=offset, sigma_clip=sigma_clip)
    except RuntimeError:
        plot_emittance(ax, emittance_scan, offset=offset, sigma_clip = False)
    file.corrected = True

    match emittance_scan.scan_parameters.axis:
        case Axis.AcerX | Axis.AcerY:
            ax.set_title(f"AECR scan\n{file.formatted_datetime}")
        case Axis.VenusX | Axis.VenusY:
            ax.set_title(f"VENUS scan\n{file.formatted_datetime}")

    return

