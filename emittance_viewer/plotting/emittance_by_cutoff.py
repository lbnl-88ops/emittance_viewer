import numpy as np
from ops.ecris.analysis.emittance_scan.rms_emittance import calculate_rms_emittance
from ops.ecris.analysis.model.emittance_scan import EmittanceScan
from ops.ecris.analysis.plot.emittance_scan import RMSEmittance
from emittance_viewer.files.emittance_file import EmittanceScanFile


def plot_emittance_by_cutoff(
        ax, 
        file: EmittanceScanFile, 
        sigma_clipped_rms: RMSEmittance,
        sigma_clip_setting: int):
    emittances = []
    offset = np.min(file.emittance_scan.data)
    cutoffs = np.linspace(0, np.max(file.emittance_scan.data)) 
    for cutoff in cutoffs:
        em = file.emittance_scan
        new_scan = EmittanceScan(em.timestamp, np.where(em.data - offset < cutoff, 0, em.data), em.scan_parameters, em.extra_metadata)

        rms = calculate_rms_emittance(new_scan,
                                      sigma_clip=False,
                                      offset=-offset)
        emittances.append(rms.e_rms * 1e6)
    median = np.median(file.emittance_scan.data)
    std = np.std(file.emittance_scan.data)
    cut = np.greater(sigma_clipped_rms.data, 0)
    min = np.min(sigma_clipped_rms.data[cut])*1e6
    # ax.axvline((median + sigma_clip_setting * std)*1e6, ls='--')
    if min:
        ax.axvline(min, ls='--', c='r')
    ax.plot(cutoffs * 1e6, emittances)
    ax.set_xlabel(r"Cutoff")
    ax.set_ylabel(r"$\varepsilon$")

