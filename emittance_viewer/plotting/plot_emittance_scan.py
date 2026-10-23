import numpy as np

from logging import info, error
import matplotlib.pyplot as plt
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
    return

    rms: RMSEmittance = calculate_rms_emittance(emittance_scan)
    if slit_offset is None:
        slit_offset = VENUS_OFFSET
    south_slit, north_slit = None, None
    if plot_slits:
        try:
            south_slit = (emittance_scan.extra_metadata["slit_south"])
            north_slit = -(24 - emittance_scan.extra_metadata["slit_north"])
        except KeyError:
            error("No slit information found")

    position = rms.x
    divergence = rms.xp

    I_plot = rms.data * 1e9  # unit nA
    total_I = np.sum(I_plot * 1e-3)
    theta = np.linspace(0, 2 * np.pi, 100)
    E_rms = rms.e_rms * 1e6  # convert to mm mrad
    A = rms.alpha
    B = rms.beta
    x_e = np.sqrt(E_rms * B) * np.cos(theta) + rms.x_mean * 1e3
    x_prime_e = (
        -np.sqrt(E_rms / B) * (A * np.cos(theta) + np.sin(theta)) + rms.xp_mean * 1e3
    )
    m, n = I_plot.shape
    binlength_position = (max(position) - min(position)) / n
    binlength_divergence = (max(divergence) - min(divergence)) / m
    xx, xxp = np.meshgrid(position, divergence)
    cm = ax.pcolormesh(
        xx,
        xxp,
        I_plot.T,
        cmap="inferno",
    )
    ax.plot(
        x_e,
        x_prime_e,
        "r--",
        label=r"$\epsilon_{rms}$ = " + f"{round(E_rms, 4)} [mm mrad]",
    )
    if plot_slits and south_slit is not None and north_slit is not None:
        for slit in [south_slit, north_slit]:
            ax.axvline(slit - slit_offset, ls='--', c='r')
    from emittance_viewer.gui.style.constants import COLOR_BG

    props = dict(boxstyle="round", facecolor=COLOR_BG, alpha=1.0)
    ax.text(
        0.025,
        0.025,
        "\n".join(
            [
                r"$I_{\text{total}}$ = " + f"{round(total_I, 4)}" + r" [$\mu A$]",
                r"$\epsilon_{rms}$ = " + f"{round(E_rms, 4)} [mm mrad]",
            ]
        ),
        fontsize=10,
        transform=ax.transAxes,
        bbox=props,
    )
    ax.plot(rms.x_mean * 1e3, rms.xp_mean * 1e3, "wx")
    ax.set_box_aspect(1)
    plt.colorbar(cm, ax=ax, label="Current (nA)")
    ax.set_xlim(rms.x[0], rms.x[-1])
    ax.set_ylim(rms.xp[0], rms.xp[-1])
    ax.set_title(file.formatted_datetime)
    # ax.legend()

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
