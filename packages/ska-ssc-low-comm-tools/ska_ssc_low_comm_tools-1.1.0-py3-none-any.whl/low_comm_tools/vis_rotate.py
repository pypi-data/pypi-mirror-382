#!/usr/bin/env python
from __future__ import annotations

import argparse
import functools
from pathlib import Path
from typing import Any, Literal, NamedTuple

import astropy.units as u
import numpy as np
import numpy.typing as npt
from astropy.coordinates import AltAz, Angle, EarthLocation, SkyCoord
from astropy.time import Time
from casacore.tables import table
from ska_low_mccs_calibration import eep
from tqdm import tqdm

from low_comm_tools.exceptions import VisError
from low_comm_tools.ms_utils import (
    get_antenna_names_from_ms,
    get_columns_from_ms,
    get_coord_from_ms,
    get_freq_from_ms,
    get_time_from_table,
)
from low_comm_tools.stations import SKA_LOW_LOCATION, load_rotation

EAST = Angle((np.pi / 2) * u.rad)
RotModeType = Literal["ground", "analytic", "oskardipole", "eep"]


class RotationJones(NamedTuple):
    jones: npt.NDArray[np.complexfloating[Any, Any]]
    """Rotation Jones matrix"""
    jones_h: npt.NDArray[np.complexfloating[Any, Any]]
    """Hermetian conjugate of `matrix`"""


def hermite_transpose(
    jones: npt.NDArray[np.complexfloating[Any, Any]],
) -> npt.NDArray[np.complexfloating[Any, Any]]:
    """Perform a Hermetian transpose of a Jones matrix.

    Can be shape [..., 2, 2]
    Transpose will be performed over the last two axes.

    Args:
        array (npt.NDArray[np.complexfloating[Any, Any]]): The Jones matrix

    Returns:
        npt.NDArray[np.complexfloating[Any, Any]]: Hermetian transposed Jones
    """
    return jones.swapaxes(-2, -1).conj()


# This is the rotation function used if mode = 'ground'
def rot_mat(angle_rad: float, do_inv: bool) -> RotationJones:
    """Simple rotation matrix

    Args:
        angle(float): Angle of rotation
        do_inv (bool): Invert matrices?

    Returns:
        RotationJones: matrix, matrix_h
    """
    mat = np.array(
        [
            [np.cos(-angle_rad), -np.sin(-angle_rad)],
            [np.sin(-angle_rad), np.cos(-angle_rad)],
        ],
        dtype=complex,
    )
    if do_inv:
        return RotationJones(np.linalg.inv(mat), np.linalg.inv(mat.conj().T))  # pyright: ignore[reportArgumentType]
    return RotationJones(mat, mat.conj().T)


# Rotation function used if mode = 'analytic'
def rot_analytic(
    times: Time,
    loc: EarthLocation,
    radec: SkyCoord,
    ang_rad: float,
    do_inv: bool,
) -> RotationJones:
    """Create a rotation Jones from an analytic basis.

    Args:
        time (Time): Times of observation
        loc (EarthLocation): Station location
        radec (SkyCoord): Beam centre location
        ang (float): Station rotation
        do_inv (bool): Invert matrices?

    Returns:
        RotationJones: matrix, matrix_h
    """

    # Based on Randall's getJonesAnalyticSimple
    # Updated 21 Feb 2025 with extra cos(theta) factor
    # Updated 16 May 2025 to vectorise in time
    # Updated 27 May 2025 to fix rotation angle, change inverse behaviour

    n_times = len(times)
    ang = ang_rad * u.rad

    altaz = radec.transform_to(AltAz(obstime=times, location=loc))
    zenith_angle = Angle(altaz.zen)
    azimuth = Angle(altaz.az)
    az_from_east = EAST - azimuth  # was previously called `pr` - don't know why

    cos_zenith = np.cos(zenith_angle)
    # Jones terms
    jones_pp = -np.sin(az_from_east + ang) * cos_zenith
    jones_pt = np.cos(az_from_east + ang) * cos_zenith * cos_zenith
    jones_qp = np.cos(az_from_east + ang) * cos_zenith
    jones_qt = np.sin(az_from_east + ang) * cos_zenith * cos_zenith
    # include 0.5 factor to match scaling of EEPs approximately
    # Question: Where is this included? Not clear currently...

    jones = np.zeros((n_times, 2, 2), dtype=complex)
    jones_H = np.zeros((n_times, 2, 2), dtype=complex)

    jones[:, 0, 0] = jones_pp
    jones[:, 0, 1] = jones_pt

    # Question - why are these negated?
    jones[:, 1, 0] = -jones_qp
    jones[:, 1, 1] = -jones_qt

    jones = jones.conj()  # Why conjugating here?
    jones_H = hermite_transpose(jones=jones)

    # Seems weird to return here on inverse - logic seemed flipped
    # TODO: Check this
    if do_inv:
        return RotationJones(jones, jones_H)

    return RotationJones(np.linalg.inv(jones), np.linalg.inv(jones_H))  # pyright: ignore[reportArgumentType]


# Two helper functions for rot_oskar
def oskar_e_theta(kl: float, theta: float, phi: float) -> float:
    """Evaluate E_theta for dipole to match current OSKAR function.

    This is also in ska-sdp-func (and therefore also used by EveryBeam?).
    The dipole is oriented with its axis along the x-axis, where phi = 0.

    A hack was added in order to help identify where phi = 0.

    TODO: Add descriptions for arguments. These appear to be angles in radians.

    Args:
        kl (float): TODO: Add description
        theta (float): TODO: Add description
        phi (float): TODO: Add description

    Returns:
        float: E_theta term
    """
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    cos_p = np.cos(phi)
    denom = 1 + cos_p**2 * (cos_t**2 - 1)
    return float(-cos_p * cos_t * (np.cos(kl * cos_p * sin_t) - np.cos(kl)) / denom)


def oskar_e_phi(kl: float, theta: float, phi: float) -> float:
    """Evaluate E_phi for dipole to match current OSKAR function.

    This is also in ska-sdp-func (and therefore also used by EveryBeam?).
    The dipole is oriented with its axis along the x-axis, where phi = 0.

    A hack was added in order to help identify where phi = 0.

    TODO: Add descriptions for arguments. These appear to be angles in radians.

    Args:
        kl (float): TODO: Add description
        theta (float): TODO: Add description
        phi (float): TODO: Add description


    Returns:
        float: E_phi term
    """
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    cos_p = np.cos(phi)
    sin_p = np.sin(phi)
    denom = 1 + cos_p**2 * (cos_t**2 - 1)
    return float(sin_p * (np.cos(kl * cos_p * sin_t) - np.cos(kl)) / denom)


# Rotation function for mode = 'oskardipole'
def rot_oskar(
    times: Time,
    loc: EarthLocation,
    radec: SkyCoord,
    ang_rad: float,
    do_inv: bool,
) -> RotationJones:
    """Create a rotation Jones from OSKAR

    This should be the same as OSKAR uses for its analytic model,
    except that here we have added an extra factor of cos(zenithangle)

    Args:
        time (Time): Times of observation
        loc (EarthLocation): Station location
        radec (SkyCoord): Beam centre location
        ang (float): Station rotation
        do_inv (bool): Invert matrices?

    Returns:
        RotationJones: _description_
    """
    altaz = radec.transform_to(AltAz(obstime=times, location=loc))
    zenith_angle = Angle(altaz.zen)
    azimuth = Angle(altaz.az)
    az_from_east = EAST - azimuth  # was previously called `pr` - don't know why

    ang = ang_rad * u.rad  # Assuming radians are provided

    ### From here the statements are copied from OSKAR
    # Define some common dipole parameters.
    freq_hz = 100e6
    dipole_length_m = 1.5  # 1.5 metres is half a wavelength at 100 MHz.
    kl = dipole_length_m * (np.pi * freq_hz / 299792458.0)
    orientation_x = ang + EAST  # "Azimuth" of X dipole axis.
    orientation_y = ang  # "Azimuth" of Y dipole axis.
    delta_phi_x = EAST - orientation_x
    delta_phi_y = EAST - orientation_y
    phi_x = az_from_east + delta_phi_x  # Phi angles relative to X dipole axis.
    phi_y = az_from_east + delta_phi_y  # Phi angles relative to Y dipole axis.
    oskar_e_theta_x = oskar_e_theta(kl=kl, theta=zenith_angle.rad, phi=phi_x.rad)  # pyright: ignore[reportArgumentType]
    oskar_e_theta_y = oskar_e_theta(kl=kl, theta=zenith_angle.rad, phi=phi_y.rad)  # pyright: ignore[reportArgumentType]

    oskar_e_phi_x = oskar_e_phi(kl=kl, theta=zenith_angle.rad, phi=phi_x.rad)  # pyright: ignore[reportArgumentType]

    oskar_e_phi_y = oskar_e_phi(kl=kl, theta=zenith_angle.rad, phi=phi_y.rad)  # pyright: ignore[reportArgumentType]
    ### end part copied from OSKAR. Now compose this the way we need it here.

    # AT - Added back this term. Calling this function previously would have errored.
    # Have not verified if this is mathematically correct
    # TODO: Check this!
    cos_zenith = np.cos(zenith_angle)
    jones = np.zeros((len(times), 2, 2), dtype=complex)
    jones_H = np.zeros((len(times), 2, 2), dtype=complex)
    jones[:, 0, 0] = oskar_e_phi_x * cos_zenith
    jones[:, 0, 1] = oskar_e_theta_x * cos_zenith
    jones[:, 1, 0] = oskar_e_phi_y * cos_zenith
    jones[:, 1, 1] = oskar_e_theta_y * cos_zenith

    jones = jones.conj()
    jones_H = hermite_transpose(jones)

    if do_inv:
        return RotationJones(jones, jones_H)

    jones_inv = np.linalg.inv(jones)
    jones_H_inv = np.linalg.inv(jones_H)
    return RotationJones(jones_inv, jones_H_inv)  # pyright: ignore[reportArgumentType]


# Rotation function used if mode = 'eep'
def rot_eep(  # type: ignore[no-untyped-def]
    times: Time,
    loc: EarthLocation,
    radec: SkyCoord,
    ang_rad: float,
    do_inv: bool,
    **eep_kwargs,
) -> RotationJones:
    # We will get a Jones matrix for each time step
    eep_jones = eep.station_beam_matrix(
        eep_rotation_deg=np.rad2deg(ang_rad),  # -ve seems necessary from testing
        location=loc,
        time=times,  # pyright: ignore[reportArgumentType]
        right_ascension_deg=radec.ra.deg,  # pyright: ignore[reportOptionalMemberAccess,reportArgumentType]
        declination_deg=radec.dec.deg,  # pyright: ignore[reportOptionalMemberAccess,reportArgumentType]
        **eep_kwargs,  # e.g. eeps, pa_correction
    )
    # Jones is shape:
    # (time, 2, 2)
    # Swap sign of X-axis (test)
    # AT - Change from an off diagonal swap to a columnar swap
    eep_jones[:, 0, :] *= -1
    # Noting that the other column seems equivalent i.e.
    # eep_jones[:, 1, :] *= -1

    # Prepare the arrays to return using vectorized operations
    # np.linalg.inv automatically broadcasts over the first dimension (time axis)
    if do_inv:  # inv is the other way around for this Jones matrix...
        jones = eep_jones.copy().astype(complex)
        jones_H = hermite_transpose(eep_jones).astype(complex)
    else:
        jones = np.linalg.inv(eep_jones).astype(complex)
        jones_H = np.linalg.inv(hermite_transpose(eep_jones)).astype(complex)

    return RotationJones(jones, jones_H)


# Makes loading EEPs hashable for caching
def _hashable_freqs(
    chan_freq_int_round_mhz: npt.NDArray[np.integer[Any]],
) -> tuple[int, ...]:
    # Convert ndarray to a hashable tuple of floats
    return tuple(np.asarray(chan_freq_int_round_mhz, dtype=int).ravel())


@functools.cache
def _load_eeps(
    chan_freqs: tuple[int, ...],
    eepdir: Path,
    eepbase: str,
    eepsuff: str,
) -> dict[int, npt.NDArray[np.complexfloating[Any, Any]]]:
    chan_freq_to_get = list(set(chan_freqs))
    freq_eep_map: dict[int, npt.NDArray[np.complexfloating[Any, Any]]] = {}
    for fmhz in tqdm(chan_freq_to_get, desc="Loading EEPs"):
        freq_eep_map[fmhz] = eep.load_eeps(  # pyright: ignore[reportArgumentType]
            fmhz, eepdir.as_posix(), filebase=eepbase, suffix=eepsuff
        )
    return freq_eep_map


def _load_eeps_cached(
    chan_freq_int_round_mhz: npt.NDArray[np.integer[Any]],
    eepdir: Path,
    eepbase: str,
    eepsuff: str,
) -> dict[int, npt.NDArray[np.complexfloating[Any, Any]]]:
    return _load_eeps(
        _hashable_freqs(chan_freq_int_round_mhz), eepdir, eepbase, eepsuff
    )


def get_rot_jones(
    mode: RotModeType,
    station_rot_ant1_rad: float,
    station_rot_ant2_rad: float,
    invert: bool,
    times: Time,
    target: SkyCoord,
    freqs: u.Quantity,
    eepdir: Path,
    eepbase: str,
    eepsuff: str,
    eepcorr: bool,
) -> RotationJones:
    # If we're just rotating the ground coordinates or using
    # the analytic mode, we can already
    # create the rotation matrix for each station
    # Take into account whether we are rotating or unrotating
    match mode:
        case "ground":
            jones_ant_1, _ = rot_mat(
                angle_rad=station_rot_ant1_rad,
                do_inv=invert,
            )
            _, jones_ant_2_H = rot_mat(
                angle_rad=station_rot_ant2_rad,
                do_inv=invert,
            )
            # These are 2x2
            # Expand to (time, freq, 2, 2)
            return RotationJones(
                jones_ant_1[None, None, :, :], jones_ant_2_H[None, None, :, :]
            )

        case "analytic":
            jones_ant_1, _ = rot_analytic(
                times=times,
                loc=SKA_LOW_LOCATION,
                radec=target,
                ang_rad=station_rot_ant1_rad,
                do_inv=invert,
            )
            _, jones_ant_2_H = rot_analytic(
                times=times,
                loc=SKA_LOW_LOCATION,
                radec=target,
                ang_rad=station_rot_ant2_rad,
                do_inv=invert,
            )
            # These are also (time, 2, 2)
            # Expand to (time, freq, 2, 2)
            return RotationJones(
                jones_ant_1[:, None, :, :], jones_ant_2_H[:, None, :, :]
            )

        case "oskardipole":
            jones_ant_1, _ = rot_oskar(
                times=times,
                loc=SKA_LOW_LOCATION,
                radec=target,
                ang_rad=station_rot_ant1_rad,
                do_inv=invert,
            )
            _, jones_ant_2_H = rot_oskar(
                times=times,
                loc=SKA_LOW_LOCATION,
                radec=target,
                ang_rad=station_rot_ant2_rad,
                do_inv=invert,
            )
            # These are also (time, 2, 2)
            # Expand to (time, freq, 2, 2)
            return RotationJones(
                jones_ant_1[:, None, :, :], jones_ant_2_H[:, None, :, :]
            )

        case "eep":
            # Loading in the EEPs is not current done as nice frequency array
            # This forces us to loop over the channel chunks
            chan_freq_int_round_mhz: npt.NDArray[np.integer[Any]] = np.round(
                freqs.to(u.MHz).value
            ).astype(int)
            freq_eep_map = _load_eeps_cached(
                chan_freq_int_round_mhz=chan_freq_int_round_mhz,
                eepdir=eepdir,
                eepbase=eepbase,
                eepsuff=eepsuff,
            )

            jones_ant_1 = np.zeros((len(times), len(freqs), 2, 2), dtype=complex)
            jones_ant_2_H = np.zeros((len(times), len(freqs), 2, 2), dtype=complex)

            # We'll use dicts to store the resulting EEP jones for a given channel
            # A poor-person's cache, if you will
            ant_1_cache: dict[int, npt.NDArray[np.complexfloating[Any, Any]]] = {}
            ant_2_cache: dict[int, npt.NDArray[np.complexfloating[Any, Any]]] = {}

            for channel, freq_mhz_round in enumerate(
                tqdm(chan_freq_int_round_mhz, desc="Computing EEP")
            ):
                if freq_mhz_round in ant_1_cache:
                    _jones_ant_1 = ant_1_cache[freq_mhz_round]
                else:
                    _jones_ant_1, _ = rot_eep(
                        times=times,
                        loc=SKA_LOW_LOCATION,
                        radec=target,
                        ang_rad=station_rot_ant1_rad,
                        eeps=freq_eep_map[freq_mhz_round],
                        do_inv=invert,
                        pa_correction=eepcorr,
                    )
                    ant_1_cache[freq_mhz_round] = _jones_ant_1

                if freq_mhz_round in ant_2_cache:
                    _jones_ant_2_H = ant_2_cache[freq_mhz_round]
                else:
                    _, _jones_ant_2_H = rot_eep(
                        times=times,
                        loc=SKA_LOW_LOCATION,
                        radec=target,
                        ang_rad=station_rot_ant2_rad,
                        eeps=freq_eep_map[freq_mhz_round],
                        do_inv=invert,
                        pa_correction=eepcorr,
                    )
                    ant_2_cache[freq_mhz_round] = _jones_ant_2_H
                jones_ant_1[:, channel, :, :] = _jones_ant_1
                jones_ant_2_H[:, channel, :, :] = _jones_ant_2_H

            return RotationJones(jones_ant_1, jones_ant_2_H)

        case _:
            raise ValueError


def rotate_ms(
    msname: Path,
    column: str = "CORRECTED_DATA",
    write_to_column: str | None = None,
    mode: RotModeType = "analytic",
    invert: bool = False,
    dryrun: bool = False,
    eepdir: Path = Path("/shared/eep-data/Perturbed_Vogel_HARP/Average_EEPs/"),
    eepbase: str = "HARP_SKALA41_randvogel_avg_",
    eepsuff: str = ".npz",
    eepcorr: bool = False,
) -> None:
    # Get metadata from MS
    if column not in get_columns_from_ms(msname):
        msg = f"Column '{column}' not in MeasurementSet"
        raise VisError(msg)

    # TODO: Use the global time when iterating over rows
    # times = get_time_from_ms(ms_path=msname)
    target = get_coord_from_ms(ms_path=msname)
    antnames = get_antenna_names_from_ms(ms_path=msname)
    chan_freq = get_freq_from_ms(ms_path=msname).to(u.Hz)

    # Get station rotations
    station_rot_rad = load_rotation(unit="rad")

    # TODO: Iterate over rows instead for speeeeeed
    # Iterate over the unique (cross correlation baselines)
    with table(str(msname), readonly=dryrun) as main_table:
        for sub_table in main_table.iter(("ANTENNA1", "ANTENNA2")):
            # Which baseline are we dealing with?
            ant1 = np.unique(sub_table.getcol("ANTENNA1"))[0]
            ant2 = np.unique(sub_table.getcol("ANTENNA2"))[0]
            if ant1 == ant2:
                continue

            # Get times from subtable since flagging can change the shape!
            # TODO: Can get rid of this by simply iterating over rows
            sub_times = get_time_from_table(sub_table)

            # Get the relevant data from the MS and make an array to store results
            # Data is shape (time, freq, pol)
            # Also want Jones in (time, freq, 2, 2)
            unrot_data = sub_table.getcol(column)
            # rot_data = np.zeros_like(unrot_data)

            unrot_data_mat = unrot_data.reshape(*unrot_data.shape[:-1], 2, 2)

            # Rotate the data for this baseline
            rot_ant_1, rot_ant_2_H = get_rot_jones(
                mode=mode,
                station_rot_ant1_rad=station_rot_rad[antnames[ant1]],
                station_rot_ant2_rad=station_rot_rad[antnames[ant2]],
                invert=invert,
                times=sub_times,
                target=target,
                freqs=chan_freq,
                eepdir=eepdir,
                eepbase=eepbase,
                eepsuff=eepsuff,
                eepcorr=eepcorr,
            )

            rot_data = (rot_ant_1 @ unrot_data_mat @ rot_ant_2_H).reshape(
                unrot_data_mat.shape[0], unrot_data_mat.shape[1], 4
            )

            # Place the rotated data back where it came from, or in DATA,
            # depending on what the user asked for
            if not dryrun:
                sub_table.putcol(
                    write_to_column if write_to_column is not None else column, rot_data
                )


def get_parser(
    add_help: bool = True,
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=add_help,
    )
    parser.add_argument(
        "msname",
        help="Name of MS. This can be a wildcard string. If more than one MS name matches, the process will run for each of them one at a time.",
        nargs="+",
        type=Path,
    )
    parser.add_argument(
        "-c",
        "--column",
        help="MS column name to read. This is also the column that will be written to if not --dryrun, and unless --write_to_column is used.",
        default="CORRECTED_DATA",
    )
    parser.add_argument(
        "-w",
        "--write_to_column",
        help="Write result to another column? (USE WITH CAUTION) [default value of COLUMN argument]",
        default=None,
        type=str,
    )
    parser.add_argument(
        "-m",
        "--mode",
        help='Conversion mode. Choose from "ground" rotation (not recommended), "analytic", "oskardipole", or "eep".',
        default="analytic",
        choices=["ground", "analytic", "oskardipole", "eep"],
        type=str,
    )
    parser.add_argument(
        "-i",
        "--invert",
        help="Invert sense of rotation? Use this option if you are forward modeling (applying to MODEL_DATA) or undoing a previously-applied rotation.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--dryrun",
        help="Only compute the rotations but do not write back into the MS? Useful with -p.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--eepdir",
        help="EEP base directory. Ignored unless MODE is EEP.",
        default=Path("/shared/eep-data/Perturbed_Vogel_HARP/Average_EEPs/"),
        type=Path,
    )
    parser.add_argument(
        "--eepbase",
        help="EEP filename base. Ignored unless MODE is EEP.",
        default="HARP_SKALA41_randvogel_avg_",
        type=str,
    )
    parser.add_argument(
        "--eepsuff",
        help="EEP filename suffix. Ignored unless MODE is EEP.",
        default=".npz",
        type=str,
    )
    parser.add_argument(
        "--eepcorr",
        help="Apply the EEP PA correction? Ignored unless MODE is EEP.",
        default=False,
        action="store_true",
    )
    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    for ms in args.msname:
        rotate_ms(
            msname=ms,
            column=args.column,
            write_to_column=args.write_to_column,
            mode=args.mode,
            invert=args.invert,
            dryrun=args.dryrun,
            eepdir=args.eepdir,
            eepsuff=args.eepsuff,
            eepcorr=args.eepcorr,
        )


if __name__ == "__main__":
    main()
