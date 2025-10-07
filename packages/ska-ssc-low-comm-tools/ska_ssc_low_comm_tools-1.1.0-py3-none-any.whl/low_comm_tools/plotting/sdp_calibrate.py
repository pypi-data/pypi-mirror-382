from __future__ import annotations

from typing import NamedTuple

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import xarray as xr
from matplotlib.figure import Figure
from ska_sdp_datamodels.calibration.calibration_model import GainTable
from ska_sdp_datamodels.visibility import Visibility

from low_comm_tools.sdp.utils import MetaData, phase


def plot_gains(
    vis: Visibility,
    gaintable: GainTable,
    metadata: MetaData,
) -> Figure:
    # ============================================================================ #
    # gain plots

    x = vis.frequency.data / 1e6

    fig, axs = plt.subplots(
        2, metadata.nstation, figsize=(14, 6), sharex=True, sharey=False
    )
    fig.suptitle("gains (EveryBeam-based model)")
    for k in range(metadata.nstation):
        ax = axs[0, k]
        ax.plot(x, np.abs(gaintable.gain.data[0, k, :, 0, 0]), "b", label="J00")
        ax.plot(x, np.abs(gaintable.gain.data[0, k, :, 0, 1]), "c", label="J01")
        ax.plot(x, np.abs(gaintable.gain.data[0, k, :, 1, 0]), "m", label="J10")
        ax.plot(x, np.abs(gaintable.gain.data[0, k, :, 1, 1]), "r", label="J11")
        ax.grid()
        ax.set_title(f"|{metadata.stations[k]}|")

        ax = axs[1, k]
        ax.plot(x, phase(gaintable.gain.data[0, k, :, 0, 0]), "b")
        ax.plot(x, phase(gaintable.gain.data[0, k, :, 0, 1]), "c")
        ax.plot(x, phase(gaintable.gain.data[0, k, :, 1, 0]), "m")
        ax.plot(x, phase(gaintable.gain.data[0, k, :, 1, 1]), "r")
        ax.grid()
        ax.set_title(f"{metadata.stations[k]} phase")
        ax.set_xlabel("frequency (MHz)")

        if k == 0:
            fig.legend()
    return fig


class VisibilityPlots(NamedTuple):
    raw_fig: Figure
    model_fig: Figure
    cal_fig: Figure


def plot_vis(
    vis: Visibility,
    calvis: Visibility | xr.Dataset,
    mdlvis: Visibility,
    metadata: MetaData,
    jones_eb: npt.NDArray[np.complex128],
    centre_correct: bool = False,
) -> VisibilityPlots:
    # ============================================================================ #
    # vis plots

    # If not done earlier, remove central beam response
    if not centre_correct:
        invjones_eb = np.linalg.pinv(jones_eb)
        corvis = vis.copy(deep=True)
        corvis.vis.data = np.einsum(
            "bfpx,tbfxy,bfqy->tbfpq",
            invjones_eb[metadata.ant1],
            calvis.vis.data.reshape((*vis.vis.shape[:3], 2, 2)),
            invjones_eb[metadata.ant2].conj(),
        ).reshape(vis.vis.shape)
    else:
        corvis = calvis

    nbl = len(vis.baselines)
    x = vis.frequency.data / 1e6

    # ylim_abs = (-1, 31)
    # ylim_re = (-31, 31)
    # ylim_im = (-31, 31)

    ylim_abs = np.array([-0.05, 1.05]) * np.max(np.abs(vis.vis.data))

    raw_fig, axs = plt.subplots(2, nbl, figsize=(14, 6), sharex=True, sharey=False)
    raw_fig.suptitle("Raw data")
    for k in range(nbl):
        tag = f"{metadata.stations[metadata.ant1[k]]} x {metadata.stations[metadata.ant2[k]]}"
        ax = axs[0, k]
        ax.plot(x, np.abs(vis.vis.data[0, k, :, 0]), "b", label="XX")
        ax.plot(x, np.abs(vis.vis.data[0, k, :, 1]), "c", label="XY")
        ax.plot(x, np.abs(vis.vis.data[0, k, :, 2]), "m", label="YX")
        ax.plot(x, np.abs(vis.vis.data[0, k, :, 3]), "r", label="YY")
        ax.grid()
        ax.set_ylim(ylim_abs)
        ax.set_title(f"|{tag}|")
        ax = axs[1, k]
        ax.plot(x, phase(vis.vis.data[0, k, :, 0]), "b")
        ax.plot(x, phase(vis.vis.data[0, k, :, 1]), "c")
        ax.plot(x, phase(vis.vis.data[0, k, :, 2]), "m")
        ax.plot(x, phase(vis.vis.data[0, k, :, 3]), "r")
        ax.grid()
        ax.set_title(f"{tag} phase")
        ax.set_xlabel("frequency (MHz)")
        if k == 0:
            raw_fig.legend()

    ylim_abs = np.array([-0.05, 1.05]) * np.max(np.abs(calvis.vis.data))

    model_fig, axs = plt.subplots(2, nbl, figsize=(14, 6), sharex=True, sharey=False)
    model_fig.suptitle("Calibrated vis and EveryBeam-based model")
    for k in range(nbl):
        tag = f"{metadata.stations[metadata.ant1[k]]} x {metadata.stations[metadata.ant2[k]]}"
        ax = axs[0, k]
        ax.plot(
            x,
            np.abs(calvis.vis.data[0, k, :, 0]),
            "b",
            alpha=0.3,
            label="XX calibrated",
        )
        ax.plot(
            x,
            np.abs(calvis.vis.data[0, k, :, 1]),
            "c",
            alpha=0.3,
            label="XY calibrated",
        )
        ax.plot(
            x,
            np.abs(calvis.vis.data[0, k, :, 2]),
            "m",
            alpha=0.3,
            label="YX calibrated",
        )
        ax.plot(
            x,
            np.abs(calvis.vis.data[0, k, :, 3]),
            "r",
            alpha=0.3,
            label="YY calibrated",
        )
        ax.plot(x, np.abs(mdlvis.vis.data[0, k, :, 0]), "b", label="XX model")
        ax.plot(x, np.abs(mdlvis.vis.data[0, k, :, 1]), "c", label="XY model")
        ax.plot(x, np.abs(mdlvis.vis.data[0, k, :, 2]), "m", label="YX model")
        ax.plot(x, np.abs(mdlvis.vis.data[0, k, :, 3]), "r", label="YY model")
        ax.grid()
        ax.set_ylim(ylim_abs)
        ax.set_title(f"|{tag}|")
        ax = axs[1, k]
        ax.plot(x, phase(calvis.vis.data[0, k, :, 0]), "b", alpha=0.3)
        ax.plot(x, phase(calvis.vis.data[0, k, :, 1]), "c", alpha=0.3)
        ax.plot(x, phase(calvis.vis.data[0, k, :, 2]), "m", alpha=0.3)
        ax.plot(x, phase(calvis.vis.data[0, k, :, 3]), "r", alpha=0.3)
        ax.plot(x, phase(mdlvis.vis.data[0, k, :, 0]), "b")
        ax.plot(x, phase(mdlvis.vis.data[0, k, :, 1]), "c")
        ax.plot(x, phase(mdlvis.vis.data[0, k, :, 2]), "m")
        ax.plot(x, phase(mdlvis.vis.data[0, k, :, 3]), "r")
        ax.grid()
        ax.set_title(f"{tag} phase")
        ax.set_xlabel("frequency (MHz)")
        if k == 0:
            model_fig.legend()

    ylim_abs = np.array([-0.05, 1.05]) * np.max(np.abs(corvis.vis.data))

    cal_fig, axs = plt.subplots(2, nbl, figsize=(14, 6), sharex=True, sharey=False)
    cal_fig.suptitle("Beam-corrected, calibratred vis")
    for k in range(nbl):
        tag = f"{metadata.stations[metadata.ant1[k]]} x {metadata.stations[metadata.ant2[k]]}"
        ax = axs[0, k]
        ax.plot(x, np.abs(corvis.vis.data[0, k, :, 0]), "b", label="XX")
        ax.plot(x, np.abs(corvis.vis.data[0, k, :, 1]), "c", label="XY")
        ax.plot(x, np.abs(corvis.vis.data[0, k, :, 2]), "m", label="YX")
        ax.plot(x, np.abs(corvis.vis.data[0, k, :, 3]), "r", label="YY")
        ax.grid()
        ax.set_ylim(ylim_abs)
        ax.set_title(f"|{tag}|")
        ax = axs[1, k]
        ax.plot(x, phase(corvis.vis.data[0, k, :, 0]), "b")
        ax.plot(x, phase(corvis.vis.data[0, k, :, 1]), "c")
        ax.plot(x, phase(corvis.vis.data[0, k, :, 2]), "m")
        ax.plot(x, phase(corvis.vis.data[0, k, :, 3]), "r")
        ax.grid()
        ax.set_title(f"{tag} phase")
        ax.set_xlabel("frequency (MHz)")
        if k == 0:
            cal_fig.legend()

    return VisibilityPlots(
        raw_fig=raw_fig,
        model_fig=model_fig,
        cal_fig=cal_fig,
    )
