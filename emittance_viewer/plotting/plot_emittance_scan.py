from enum import Enum, auto

import numpy as np

from logging import info
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.artist import Artist
from emittance_viewer.files import EmittanceScanFile
from emittance_viewer.status_bar import update_status_bar

from ops.ecris.analysis.emittance_scan.rms_emittance import (
    RMSEmittance,
    calculate_rms_emittance,
)


class Rescale(Enum):
    NONE = auto()
    LINEAR = auto()
    POLYNOMIAL = auto()


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
        ax.grid(alpha=0.5, ls="--")
        font_size = 10
        ax.tick_params(labelsize=font_size)
        ax.set_xlabel(f"Position [mm]")
        ax.set_ylabel(f"Divergence [mrad]")
        # ax.colorbar(label="Current [nA]")
        ax.set_facecolor("white")
    return fig, axs


def plot_file(ax, file: EmittanceScanFile):
    emittance_scan = file.emittance_scan

    if emittance_scan is None:
        info(f"File object: {file.path} has no emittance scan.")
        return None

    rms: RMSEmittance = calculate_rms_emittance(emittance_scan)

    position = rms.x
    divergence = rms.xp

    I_plot = rms.data * 1e9  # unit nA
    theta = np.linspace(0, 2 * np.pi, 100)
    E_rms = rms.e_rms * 1e6  # convert to mm mrad
    A = rms.alpha
    B = rms.beta
    x_e = np.sqrt(4 * E_rms * B) * np.cos(theta) + rms.x_mean * 1e3
    x_prime_e = (
        -np.sqrt(4 * E_rms / B) * (A * np.cos(theta) + np.sin(theta))
        + rms.xp_mean * 1e3
    )
    m, n = I_plot.shape
    binlength_position = (max(position) - min(position)) / n
    binlength_divergence = (max(divergence) - min(divergence)) / m
    xx, xxp = np.meshgrid(position, divergence)
    ax.pcolormesh(xx, xxp, I_plot.T, cmap="inferno")
    ax.plot(
        x_e,
        x_prime_e,
        "r--",
        label=r"$\epsilon_{rms}$ = " + f"{round(E_rms, 4)} [mm mrad]",
    )
    ax.plot(rms.x_mean * 1e3, rms.xp_mean * 1e3, "wx")
    ax.set_xlim(rms.x[0], rms.x[-1])
    ax.set_ylim(rms.xp[0], rms.xp[-1])
    ax.set_title(file.formatted_datetime)
    ax.legend()

    return

    # match rescale_method:
    #     case Rescale.POLYNOMIAL:
    #         csd.m_over_q, sol = polynomial_fit_mq(
    #             csd,
    #             [Element("O", "Oxygen", 15.9949, 8)],
    #             polynomial_order=4,
    #             always_optimize=True,
    #             nonlinear_bounds=(-1e-2, 1e-2),
    #         )
    #         info("Polynomial fit complete:")
    #         info(sol)
    #         if sol.success:
    #             update_status_bar("Polynomial fit succeeded.")
    #         else:
    #             update_status_bar(f"Polynomial fit failed: {sol.message}.")
    #         label = file.formatted_datetime
    #     case Rescale.LINEAR:
    #         scale_with_oxygen(csd)
    #         label = file.formatted_datetime + " (linear scaling)"
    #     case Rescale.NONE:
    #         info("Skipping rescale")
    #         csd.m_over_q = estimate_m_over_q(csd)
    #         label = file.formatted_datetime + " (not rescaled)"
    #
    # (ln,) = ax.plot(csd.m_over_q, csd.beam_current, label=label, animated=True)
    # current_xtick_max = ax.get_xticks()[-1]
    # x_tick_max = int(np.max(csd.m_over_q)) + 2
    # if x_tick_max > current_xtick_max:
    #     ax.set_xticks(range(0, x_tick_max))
    # return ln
