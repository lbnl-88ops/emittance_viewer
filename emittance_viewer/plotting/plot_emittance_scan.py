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

def calculate_extended_data(file: EmittanceScanFile, offset: bool = True, sigma_clip: bool = True, sigma_alpha: float = 3.0, offset_value: float = 0.0):
    """Calculate all the extra metadata requested for the SingleScanPane"""
    emittance_scan = file.emittance_scan
    if emittance_scan is None:
        return {}

    data = emittance_scan.data.copy()
    
    # Apply background offset
    if offset:
        data = data - offset_value
    
    # Apply sigma clipping
    # Stub: This logic should ideally match ops-ecris-analysis
    if sigma_clip:
        # Simple sigma clipping: zero out anything below sigma_alpha * std
        # (Using mean and std of the (potentially offset) data)
        threshold = np.mean(data) + sigma_alpha * np.std(data)
        # However, for emittance scans, we often just want to keep peaks.
        # Let's assume the library will handle the sophisticated version.
        # For now, we'll just zero out values below the threshold.
        data[data < threshold] = 0

    # Extraction Voltage and Beamline
    extra = emittance_scan.extra_metadata
    ext_v = extra.get("extraction_v", 0.0)
    
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
    
    # Total Current calculation (Sum of all data points after corrections)
    if mult is not None:
        # Assuming max_current * 10**mult is in Amps, and total_current is similar.
        # Convert to nA for display consistency.
        total_current_val = np.sum(data) * (10 ** mult) * 1e9
        utilization = 100 * (max_current * (10 ** mult)) / 10
    else:
        total_current_val = np.sum(data)
        utilization = 0.0

    try:
        # Stub: calculate_rms_emittance should eventually take the fitting params
        rms = calculate_rms_emittance(emittance_scan)
        
        # Normalized emittance calculation
        m_over_q = extra.get("m_over_q", 1.0)
        if ext_v > 0 and m_over_q > 0:
            # Constant: m_u * c^2 / e is approx 931.5 MeV
            beta = np.sqrt(2 * ext_v * 1e3 / (m_over_q * 931.5e6))
            norm_emit = beta * rms.e_rms
        else:
            norm_emit = 0.0

        return {
            "beamline": beamline,
            "extraction_v": ext_v,
            "total_current": total_current_val,
            "rms_emit": rms.e_rms,
            "norm_emit": norm_emit,
            "alpha": rms.alpha,
            "beta": rms.beta,
            "gamma": rms.gamma,
            "x_centroid": rms.x_mean,
            "xp_centroid": rms.xp_mean,
            "utilization": utilization,
            "max_current": max_current,
            "gain": 10**(mult if mult is not None else 0)
        }
    except Exception as e:
        error(f"Error calculating extended data: {e}")
        return {}

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


def plot_file(ax, file: EmittanceScanFile, offset: bool = True, sigma_clip: bool = True, sigma_alpha: float = 3.0, offset_value: float = 0.0):
    emittance_scan = file.emittance_scan

    if emittance_scan is None:
        info(f"File object: {file.path} has no emittance scan.")
        return None

    try:
        plot_emittance(ax, emittance_scan, offset=offset, sigma_clip=sigma_clip)
    except RuntimeError:
        plot_emittance(ax, emittance_scan, offset=offset, sigma_clip = False)

    match emittance_scan.scan_parameters.axis:
        case Axis.AcerX | Axis.AcerY:
            ax.set_title(f"AECR scan\n{file.formatted_datetime}")
        case Axis.VenusX | Axis.VenusY:
            ax.set_title(f"VENUS scan\n{file.formatted_datetime}")

    return

