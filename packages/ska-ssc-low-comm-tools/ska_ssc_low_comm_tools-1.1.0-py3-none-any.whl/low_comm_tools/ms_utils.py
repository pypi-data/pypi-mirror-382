from __future__ import annotations

from pathlib import Path

import astropy.units as u
import numpy as np
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time
from casacore.tables import table


def get_coord_from_ms(
    ms_path: str | Path,
    field_index: int = 0,
) -> SkyCoord:
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)
    with table(str(ms_path / "FIELD"), ack=False) as tab:
        field_row = tab.getcell("PHASE_DIR", field_index).flatten()
        return SkyCoord(
            ra=field_row[0],
            dec=field_row[1],
            unit=u.rad,
        )


def get_time_from_table(tab: table) -> Time:
    """Get time from OPEN casacore tyable

    Args:
        tab (table): OPEN table

    Returns:
        Time: Times
    """
    times_mjds = np.unique(tab.getcol("TIME_CENTROID")[:].flatten()) * u.s
    return Time(times_mjds, format="mjd", scale="utc")


def get_time_from_ms(
    ms_path: str | Path,
) -> Time:
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)
    with table(str(ms_path), ack=False) as tab:
        return get_time_from_table(tab)


def get_freq_from_ms(
    ms_path: str | Path,
) -> u.Quantity[u.Hz]:
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)
    with table(str(ms_path / "SPECTRAL_WINDOW"), ack=False) as tab:
        return tab.getcol("CHAN_FREQ").flatten() * u.Hz


def get_location_from_ms(
    ms_path: str | Path,
) -> EarthLocation:
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)
    with table(str(ms_path / "ANTENNA"), ack=False) as tab:
        location_array = tab.getcol("POSITION").flatten() * u.m
    return EarthLocation.from_geocentric(
        x=location_array[0],
        y=location_array[1],
        z=location_array[2],
    )


def get_altaz_from_ms(
    ms_path: str | Path,
    field_index: int = 0,
) -> SkyCoord:
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)
    coord = get_coord_from_ms(ms_path, field_index=field_index)
    time = get_time_from_ms(ms_path)
    location = get_location_from_ms(ms_path)
    return coord.transform_to(AltAz(obstime=time, location=location))


def get_field_name_from_ms(
    ms_path: str | Path,
    field_index: int = 0,
) -> str:
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)

    with table(str(ms_path / "FIELD"), ack=False) as tab:
        field_name = str(tab.getcol("NAME")[field_index])

    if field_name.startswith("field_"):
        field_name = field_name.replace("field_", "")

    if field_name.endswith("_0"):
        field_name = field_name.replace("_0", "")

    return field_name


def get_columns_from_ms(
    ms_path: str | Path,
) -> list[str]:
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)
    with table(str(ms_path), ack=False) as tab:
        return list(tab.colnames())


def get_antenna_names_from_ms(
    ms_path: str | Path,
) -> list[str]:
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)
    with table(str(ms_path / "ANTENNA"), ack=False) as tab:
        return list(tab.getcol("NAME"))
