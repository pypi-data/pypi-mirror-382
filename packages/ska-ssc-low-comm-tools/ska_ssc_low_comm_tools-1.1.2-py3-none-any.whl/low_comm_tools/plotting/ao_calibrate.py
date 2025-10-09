"""Code to use AO calibrate"""

# Shamelessly stolen from Flint. Clearly an act of piracy. YARRR!

from __future__ import annotations  # used to keep mypy/pylance happy in AOSolutions

import struct
from argparse import ArgumentParser
from collections.abc import Collection, Iterable
from pathlib import Path
from typing import (
    Any,
    NamedTuple,
)

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from casacore.tables import table
from matplotlib.axes import Axes
from numpy.typing import NDArray

from low_comm_tools.log_config import logger
from low_comm_tools.options import BaseOptions


def divide_bandpass_by_ref_ant_preserve_phase(
    complex_gains: npt.NDArray[np.complexfloating[Any, Any]], ref_ant: int
) -> npt.NDArray[np.complexfloating[Any, Any]]:
    """Divide the bandpass complex gains (solved for initially by something like
    calibrate) by a nominated reference antenna. In the case of ``calibrate``
    there is no implicit reference antenna. This is valid for cases where the
    xy-phase is set to 0 (true via the ASKAP on-dish calibrator).

    This particular function is most appropriate for the `calibrate` style
    solutions, which solve for the Jones in one step. In HMS notation this
    are normally split into two separate 2x2 matrices, one for the gains
    with zero off-diagonal elements and a leakage matrix with ones on
    the diagonal.

    This is the preferred function to use whena attempting to set a
    phase reference antenna to precomputed Jones bandpass solutions.

    The input complex gains should be in the form:
    >> (ant, channel, pol)

    Internally reference phasores are constructed for the G_x and G_y
    terms of the reference antenna. They are then applied:
    >> G_xp = G_x / G_xref
    >> G_xyp = G_xy / G_yref
    >> G_yxp = G_yx / G_xref
    >> G_y = G_y / G_yref

    which is applied to all antennas in ``complex_gains``.

    Args:
        complex_gains (np.ndarray): The complex gains that will be normalised
        ref_ant (int): The desired reference antenna to use

    Returns:
        np.ndarray: The normalised bandpass solutions
    """
    assert len(complex_gains.shape) == 3, (
        f"The shape of the input complex gains should be of rank 3 in form (ant, chan, pol). Received {complex_gains.shape}"
    )

    logger.info(
        f"Dividing bandpass gain solutions using reference antenna={ref_ant}, using correct phasor"
    )

    # Unpack the values for short hand use
    g_x = complex_gains[:, :, 0]
    g_xy = complex_gains[:, :, 1]
    g_yx = complex_gains[:, :, 2]
    g_y = complex_gains[:, :, 3]

    # In the operations below our ship only wants to be touching
    # the phases in a piratey manner. The amplitudes should remina
    # unchanged. Construct phasors of the nominated reference antenna
    ref_g_x = complex_gains[ref_ant, :, 0]
    ref_g_x = ref_g_x / np.abs(ref_g_x)

    ref_g_y = complex_gains[ref_ant, :, 3]
    ref_g_y = ref_g_y / np.abs(ref_g_y)

    # Now here is the math, from one Captain Daniel Mitchell
    # g_x and g_y.d_yx by g_x(ref) and g_y and g_x.d_xy by g_y(ref).
    # i.e. assuming that xy-phase = 0 (due to the ODC) and that the cross terms are leakage.
    # Since calibrate solves for the Jones directly, the off-diagonals are already
    # multiplied through by the appropriate g_y and g_x.
    g_x_prime = g_x / ref_g_x
    g_xy_prime = g_xy / ref_g_y  # Leakage of y into x, so reference the y
    g_yx_prime = g_yx / ref_g_x  # Leakage of x into y, so reference the x
    g_y_prime = g_y / ref_g_y

    # Construct the output array to slice things into
    bp_p = (
        np.zeros_like(complex_gains) * np.nan
        + 1j * np.zeros_like(complex_gains) * np.nan
    )

    # Place things into place
    bp_p[:, :, 0] = g_x_prime
    bp_p[:, :, 1] = g_xy_prime
    bp_p[:, :, 2] = g_yx_prime
    bp_p[:, :, 3] = g_y_prime

    return bp_p


class MSMetaData(BaseOptions):
    """Structure to hold metadata about a measurement set"""

    stations: list[str]
    """List of stations in the measurement set"""
    frequencies_hz: NDArray[np.floating[Any]]
    """Frequencies in the measurement set in Hz"""


def parse_ms_metadata(ms_path: Path | str) -> MSMetaData:
    """Parse the metadata from a measurement set

    Args:
        ms_path (Path): Path to the measurement set to parse

    Returns:
        MSMetaData: The parsed metadata
    """
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)
    with table(str(ms_path / "ANTENNA"), ack=False) as antenna_table:
        stations = antenna_table.getcol("NAME")
    with table(str(ms_path / "SPECTRAL_WINDOW"), ack=False) as spw_table:
        frequencies_hz = spw_table.getcol("CHAN_FREQ").flatten()

    return MSMetaData(
        stations=stations,
        frequencies_hz=frequencies_hz,
    )


def save_aosolutions_file(aosolutions: AOSolutions, output_path: Path) -> Path:
    """Save a AOSolutions file to the ao-standard binary format.

    Args:
        aosolutions (ApplySolutions): Instance of the solutions to save
        output_path (Path): Output path to write the files to

    Returns:
        Path: Path the file was written to
    """

    header_format = "8s6I2d"
    header_intro = b"MWAOCAL\0"

    output_dir = output_path.parent
    if not output_dir.exists():
        logger.info(f"Creating {output_dir}.")
        output_dir.mkdir(parents=True)

    logger.info(f"Writing aosolutions to {output_path!s}.")
    with output_path.open("wb") as out_file:
        out_file.write(
            struct.pack(
                header_format,
                header_intro,
                0,  # File type, only 0 mode available
                0,  # Structure type, 0 model available only
                aosolutions.nsol,
                aosolutions.nant,
                aosolutions.nchan,
                aosolutions.npol,
                0.0,  # time start, I don't believe these are used in most use cases
                0.0,  # time end, I don't believe these are used in most use cases
            )
        )
        aosolutions.bandpass.tofile(out_file)

    return output_path


def load_aosolutions_file(solutions_path: Path) -> AOSolutions:
    """Load in an AO-style solutions file

    Args:
        solutions_path (Path): The path of the solutions file to load

    Returns:
        AOSolutions: Structure container the deserialized solutions file
    """

    if not solutions_path.exists() and not solutions_path.is_file():
        msg = f"{solutions_path!s} either does not exist or is not a file. "
        raise FileNotFoundError(msg)
    logger.info(f"Loading {solutions_path}")

    with solutions_path.open("rb") as in_file:
        _junk = np.fromfile(in_file, dtype="<i4", count=2)

        header = np.fromfile(in_file, dtype="<i4", count=10)
        logger.info(f"Header extracted: {header=}")
        file_type = header[0]
        assert file_type == 0, f"Expected file_type of 0, found {file_type}"

        structure_type = header[1]
        assert file_type == 0, f"Expected structure_type of 0, found {structure_type}"

        nsol, nant, nchan, npol = header[2:6]
        sol_shape = (nsol, nant, nchan, npol)

        bandpass = np.fromfile(in_file, dtype="<c16", count=np.prod(sol_shape)).reshape(
            sol_shape
        )
        logger.info(f"Loaded solutions of shape {bandpass.shape}")

        return AOSolutions(
            path=solutions_path,
            nsol=nsol,
            nant=nant,
            nchan=nchan,
            npol=npol,
            bandpass=bandpass,
        )


# TODO: Rename the bandpass attribute?
class AOSolutions(NamedTuple):
    """Structure to load an AO-style solutions file"""

    path: Path
    """Path of the solutions file loaded"""
    nsol: int
    """Number of time solutions"""
    nant: int
    """Number of antenna in the solution file"""
    nchan: int
    """Number of channels in the solution file"""
    npol: int
    """Number of polarisations in the file"""
    bandpass: npt.NDArray[np.complexfloating[Any, Any]]
    """Complex data representing the antenna Jones. Shape is (nsol, nant, nchan, npol)"""

    # TODO: Need tocorporate the start and end times into this header

    @classmethod
    def load(cls, path: Path) -> AOSolutions:
        """Load in an AO-stule solution file. See `load_solutions_file`, which is
        internally used.
        """
        return load_aosolutions_file(solutions_path=path)

    def save(self, output_path: Path) -> Path:
        """Save the instance of AOSolution to a standard aosolution binary file

        Args:
            output_path (Path): Location to write the file to

        Returns:
            Path: Location the file was written to
        """
        return save_aosolutions_file(aosolutions=self, output_path=output_path)

    def plot_solutions(self, ref_ant: int | None = 0) -> Iterable[Path]:
        """Plot the solutions of all antenna for the first time-interval
        in the aosolutions file. The XX and the YY will be plotted.

        Args:
            ref_ant (Optional[int], optional): Reference antenna to use. If None is specified there is no division by a reference antenna.  Defaults to 0.

        Returns:
            Iterable[Path]: Path to the phase and amplited plots created.
        """
        # TODO: Change call signature to pass straight through
        return plot_solutions(solutions=self, ref_ant=ref_ant)


def fill_between_flags(
    ax: Axes,
    flags: npt.NDArray[np.bool_],
    values: npt.NDArray[np.complexfloating[Any, Any]]
    | npt.NDArray[np.floating[Any]]
    | None = None,
    direction: str = "x",
) -> None:
    """Plot vertical or horizontal lines where data are flagged.

    NOTE: This is pretty inefficient and not intended for regular use.

    Args:
        ax (plt.Axes): Axes object to plot lines on
        flags (np.ndarray): Flags to consider. If `True`, plot.
        values (Optional[np.ndarray], optional): The values to plot at. Useful if the position does not map to location. Defaults to None.
        direction (str, optional): If `x` use axvline, if `y` use axhline. Defaults to "x".
    """
    if values is None:
        values = np.arange(len(flags)).astype(float)

    mask = np.argwhere(flags)
    plot_vals = values[mask]
    func = ax.axvline if direction == "x" else ax.axhline

    for v in plot_vals:
        func(v, color="black", alpha=0.3)


def plot_solutions(
    solutions: Path | AOSolutions, ref_ant: int | None = 0, ms_path: Path | None = None
) -> Collection[Path]:
    """Plot solutions for AO-style solutions

    Args:
        solutions (Path): Path to the solutions file
        ref_ant (Optional[int], optional): Reference antenna to use. If None is specified there is no division by a reference antenna.  Defaults to 0.

    Return:
        Collection[Path] -- The paths of the two plots createda
    """
    ao_sols = (
        AOSolutions.load(path=solutions) if isinstance(solutions, Path) else solutions
    )
    solutions_path = ao_sols.path
    logger.info(f"Plotting {solutions_path}")

    if ao_sols.nsol > 1:
        logger.warning(f"Found {ao_sols.nsol} intervals, plotting the first. ")
    plot_sol = 0  # The first time interval

    data = ao_sols.bandpass[plot_sol]
    if ref_ant is not None and ref_ant < 0:
        ref_ant = select_refant(bandpass=ao_sols.bandpass)
        logger.info(f"Overwriting reference antenna selection, using {ref_ant=}")

    if ref_ant is not None:
        data = divide_bandpass_by_ref_ant_preserve_phase(
            complex_gains=ao_sols.bandpass[plot_sol], ref_ant=ref_ant
        )

    amplitudes = np.abs(data)
    phases = np.angle(data, deg=True)
    channels = np.arange(ao_sols.nchan)

    ant_names = np.arange(ao_sols.nant)
    x_axis_array = channels
    x_label = "Channel"

    if ms_path is not None:
        ms_metadata = parse_ms_metadata(ms_path)
        assert ms_metadata.frequencies_hz.shape[0] == ao_sols.nchan, (
            f"Expected {ao_sols.nchan} channels, found {ms_metadata.frequencies_hz.shape[0]} in {ms_path!s}"
        )
        assert len(ms_metadata.stations) == ao_sols.nant, (
            f"Expected {ao_sols.nant} antennas, found {len(ms_metadata.stations)} in {ms_path!s}"
        )
        frequencies_mhz = ms_metadata.frequencies_hz / 1e6

        x_axis_array = frequencies_mhz  # type: ignore[assignment]
        x_label = "Frequency / MHz"
        ant_names = ms_metadata.stations  # type: ignore[assignment]

    ncolumns = 2
    nrows = ao_sols.nant // ncolumns
    if ncolumns * nrows < ao_sols.nant:
        nrows += 1
    logger.debug(f"Plotting {plot_sol=} with {ncolumns=} {nrows=}")

    fig_amp, axes_amp = plt.subplots(nrows, ncolumns, figsize=(15, 9))
    fig_ratio, axes_ratio = plt.subplots(nrows, ncolumns, figsize=(15, 9))
    fig_phase, axes_phase = plt.subplots(nrows, ncolumns, figsize=(15, 9))

    for y in range(nrows):
        for x in range(ncolumns):
            ant_idx = y * nrows + x
            ant_name = ant_names[ant_idx]

            amps_xx = amplitudes[ant_idx, :, 0]
            amps_yy = amplitudes[ant_idx, :, 3]
            phase_xx = phases[ant_idx, :, 0]
            phase_yy = phases[ant_idx, :, 3]

            ratio = amps_xx / amps_yy

            if any(np.sum(np.isfinite(amps)) == 0 for amps in (amps_xx, amps_yy)):
                logger.warning(f"No valid data for {ant_idx=}")
                continue

            max_amp_xx = (
                np.nanmax(amps_xx[np.isfinite(amps_xx)])
                if any(np.isfinite(amps_xx))
                else -1
            )
            max_amp_yy = (
                np.nanmax(amps_yy[np.isfinite(amps_yy)])
                if any(np.isfinite(amps_yy))
                else -1
            )
            min_amp_xx = (
                np.nanmin(amps_xx[np.isfinite(amps_xx)])
                if any(np.isfinite(amps_xx))
                else -1
            )
            min_amp_yy = (
                np.nanmin(amps_yy[np.isfinite(amps_yy)])
                if any(np.isfinite(amps_yy))
                else -1
            )
            ax_a, ax_p = axes_amp[y, x], axes_phase[y, x]
            ax_a = axes_amp[y, x]
            ax_r = axes_ratio[y, x]
            ax_a.plot(
                x_axis_array,
                amps_xx,
                marker=None,
                color="tab:blue",
                label="X" if y == 0 and x == 0 else None,
            )
            ax_a.plot(
                x_axis_array,
                amps_yy,
                marker=None,
                color="tab:red",
                label="Y" if y == 0 and x == 0 else None,
            )
            ax_r.plot(
                x_axis_array,
                ratio,
                marker=None,
                color="tab:green",
                label="X/Y" if y == 0 and x == 0 else None,
            )

            ax_a.set(
                ylabel="Amplitude",
                xlabel=x_label,
                ylim=(
                    min(min_amp_xx, min_amp_yy) * 0.9,
                    max(max_amp_xx, max_amp_yy) * 1.1,
                ),
            )
            ax_a.axhline(1, color="black", linestyle="--", linewidth=0.5)
            ax_a.set_title(f"antenna {ant_name}", fontsize=8)
            # fill_between_flags(ax_a, ~np.isfinite(amps_yy) | ~np.isfinite(amps_xx))

            ax_r.set(ylabel="Amplitude Ratio", xlabel=x_label, ylim=(0.8, 1.2))
            ax_r.axhline(1, color="black", linestyle="--", linewidth=0.5)
            ax_r.set_title(f"antenna {ant_name}", fontsize=8)
            # fill_between_flags(ax_r, ~np.isfinite(amps_yy) | ~np.isfinite(amps_xx))

            ax_p.plot(
                x_axis_array,
                phase_xx,
                marker=None,
                color="tab:blue",
                label="X" if y == 0 and x == 0 else None,
            )
            ax_p.plot(
                x_axis_array,
                phase_yy,
                marker=None,
                color="tab:red",
                label="Y" if y == 0 and x == 0 else None,
            )
            ax_p.set(ylabel="Phase / deg", xlabel=x_label, ylim=(-200, 200))
            ax_p.set_title(f"antenna {ant_name}", fontsize=8)
            # fill_between_flags(ax_p, ~np.isfinite(phase_yy) | ~np.isfinite(phase_xx))

    fig_amp.legend()
    fig_phase.legend()
    fig_ratio.legend()

    fig_amp.suptitle(f"{ao_sols.path.name} - Amplitudes")
    fig_phase.suptitle(f"{ao_sols.path.name} - Phases")
    fig_ratio.suptitle(f"{ao_sols.path.name} - Amplitude Ratios")

    fig_amp.tight_layout()
    fig_ratio.tight_layout()
    fig_phase.tight_layout()

    out_amp = f"{solutions_path.with_suffix('.amplitude.png')!s}"
    logger.info(f"Saving {out_amp}.")
    fig_amp.savefig(out_amp)

    out_phase = f"{solutions_path.with_suffix('.phase.png')!s}"
    logger.info(f"Saving {out_phase}.")
    fig_phase.savefig(out_phase)

    out_ratio = f"{solutions_path.with_suffix('.ratio.png')!s}"
    logger.info(f"Saving {out_ratio}.")
    fig_ratio.savefig(out_ratio)

    return [Path(out_amp), Path(out_phase), Path(out_ratio)]


def select_refant(bandpass: npt.NDArray[np.complexfloating[Any, Any]]) -> int:
    """Attempt to select an optimal reference antenna. This works in
    a fairly simple way, and simply selects the antenna which is select
    based purely on the number of valid/unflagged solutions in the
    bandpass aosolutions file.

    Args:
        bandpass (np.ndarray): The aosolutions file that has been
        solved for

    Returns:
        int: The index of the reference antenna that should be used.
    """

    assert len(bandpass.shape) == 4, (
        f"Expected a bandpass of shape (times, ant, channels, pol), received {bandpass.shape=}"
    )

    # create the mask of valid solutions
    mask = np.isfinite(bandpass)
    # Sum_mask will be a shape of length 2 (time, ants)
    sum_mask = np.sum(mask, axis=(2, 3))

    # The refant will be the one with the highest number
    max_ant = np.argmax(sum_mask, keepdims=True)

    return int(max_ant[0][0])


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Run calibrate and apply the solutions given a measurement set and sky-model."
    )

    parser.add_argument(
        "aosolutions", type=Path, help="Path to the solution file to inspect and plot"
    )
    parser.add_argument(
        "--ref-ant",
        type=int,
        default=-1,
        help="The reference antenna to use when plotting the bandpass solutions. If -1, the best one will be selected.",
    )
    parser.add_argument(
        "--ms",
        type=Path,
        default=None,
        help="The measurement set to use when plotting the bandpass solutions.",
    )

    return parser


def main() -> None:
    parser = get_parser()

    args = parser.parse_args()

    _ = plot_solutions(
        solutions=args.aosolutions,
        ref_ant=args.ref_ant,
        ms_path=args.ms,
    )


if __name__ == "__main__":
    main()
