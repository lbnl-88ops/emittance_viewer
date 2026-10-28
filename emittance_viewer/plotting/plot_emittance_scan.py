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

def calculate_extended_data(file: EmittanceScanFile, offset: bool = True, sigma_clip: bool = True, sigma_alpha: int = 2):
    """Calculate all the extra metadata requested for the SingleScanPane"""
    emittance_scan = file.emittance_scan
    if emittance_scan is None:
        return {}, None

    # Extraction Voltage and Beamline
    extra = emittance_scan.extra_metadata
    assert extra is not None
    ext_v = extra.get("extraction_v", None)
    
    axis = emittance_scan.scan_parameters.axis
    if axis in [Axis.AcerX, Axis.AcerY]:
        beamline = "AECR"
    elif axis in [Axis.VenusX, Axis.VenusY]:
        beamline = "VENUS"
    else:
        beamline = "Unknown"

    # Max current and Utilization (from old FileInfoPane)
    max_current = np.max(emittance_scan.data)
    mult = extra.get("emittance_keithley_multiplier")
    if mult is not None:
        utilization = 100 * (max_current * (10 ** mult)) / 10
    else:
        utilization = 0.0

    try:
        rms = calculate_rms_emittance(emittance_scan, sigma_clip=sigma_clip, sigma_alpha=sigma_alpha, offset=offset)
        
        # Normalized emittance calculation
        m_over_q = extra.get("m_over_q", None)
        if ext_v is not None and m_over_q is not None and ext_v > 0 and m_over_q > 0:
            # Constant: m_u * c^2 / e is approx 931.5 MeV
            beta = np.sqrt(2 * ext_v * 1e3 / (m_over_q * 931.5e6))
            norm_emit = beta * rms.e_rms
        else:
            norm_emit = None

        # Total Current: sum of corrected data * multiplier -> nA
        current_multiplier = 10 ** mult if mult is not None else 1.0
        total_current_nA = np.sum(rms.data) * current_multiplier * 1e9

        data_dict = {
            "beamline": beamline,
            "extraction_v": ext_v,
            "total_current": total_current_nA,
            "rms_emit": rms.e_rms * 1e6, # mm-mrad
            "norm_emit": norm_emit * 1e6 if norm_emit is not None else norm_emit,
            "alpha": rms.alpha,
            "beta": rms.beta, # mm/mrad
            "gamma": rms.gamma, # mrad/mm
            "x_centroid": rms.x_mean * 1e3, # mm
            "xp_centroid": rms.xp_mean * 1e3, # mrad
            "utilization": utilization,
            "calc_offset": np.min(emittance_scan.data)
        }
        return data_dict, rms
    except Exception as e:
        error(f"Error calculating extended data: {e}")
        return {}, None

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


def plot_file(ax, file: EmittanceScanFile, rms_emittance: RMSEmittance | None = None):
    emittance_scan = file.emittance_scan

    if emittance_scan is None:
        info(f"File object: {file.path} has no emittance scan.")
        return None

    try:
        plot_emittance(ax, emittance_scan, rms_emittance=rms_emittance)
    except Exception as e:
        error(f"Error plotting file: {e}")

    match emittance_scan.scan_parameters.axis:
        case Axis.AcerX | Axis.AcerY:
            ax.set_title(f"AECR scan\n{file.formatted_datetime}")
        case Axis.VenusX | Axis.VenusY:
            ax.set_title(f"VENUS scan\n{file.formatted_datetime}")

    return

