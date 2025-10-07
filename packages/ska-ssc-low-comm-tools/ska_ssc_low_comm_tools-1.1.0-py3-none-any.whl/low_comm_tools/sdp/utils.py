from __future__ import annotations

from pathlib import Path
from typing import Any, NamedTuple

import everybeam as eb
import numpy as np
import numpy.typing as npt
from astropy.coordinates import ITRS, AltAz, Angle, EarthLocation, SkyCoord
from astropy.time import Time
from ska_sdp_datamodels.visibility import Visibility


def phase(z: np.complexfloating[Any, Any]) -> np.floating[Any]:
    # return np.unwrap(np.angle(z)) * 180 / np.pi
    return np.angle(z) * 180 / np.pi  # type: ignore[no-any-return]
    # phi += 360 * (phi < -90)


def radec_to_xyz(
    ra: Angle, dec: Angle, mjds: npt.NDArray[np.floating[Any]]
) -> npt.NDArray[np.floating[Any]]:
    """
    Convert RA and Dec ICRS coordinates to ITRS cartesian coordinates.
    See the Everybeam docs.

    Args:
        ra (astropy.coordinates.Angle): Right ascension
        dec (astropy.coordinates.Angle): Declination
        mjds (float): MJD time in seconds

    Returns:
        pointing_xyz (ndarray): NumPy array containing the ITRS X, Y and Z
        coordinates
    """
    obstime = Time(mjds / 86400.0, scale="utc", format="mjd")
    dir_pointing = SkyCoord(ra, dec)
    dir_pointing_itrs = dir_pointing.transform_to(ITRS(obstime=obstime))
    return np.asarray(dir_pointing_itrs.cartesian.xyz.transpose())


class MetaData(NamedTuple):
    time: Time
    mjds: npt.NDArray[np.floating[Any]]
    location: EarthLocation
    nstation: int
    stations: list[str]
    zen_itrf: npt.NDArray[np.floating[Any]]
    telescope: eb.Telescope
    cos_term: npt.NDArray[np.floating[Any]]
    beam_itrf: npt.NDArray[np.floating[Any]]
    ant1: npt.NDArray[np.integer[Any]]
    ant2: npt.NDArray[np.integer[Any]]


def pre_calculate_metadata(
    dataset: Path,
    vis: Visibility,
) -> MetaData:
    # ============================================================================ #
    # pre-calculate some metadata for later

    location: EarthLocation = vis.configuration.location
    stations: list[str] = vis.configuration.stations.data
    nstation = len(stations)
    ant1 = vis.antenna1.data[vis.antenna1.data != vis.antenna2.data]
    ant2 = vis.antenna2.data[vis.antenna1.data != vis.antenna2.data]

    telescope = eb.load_telescope(dataset.as_posix())

    # metadata for beam at the central time step
    time = np.mean(Time(vis.datetime.data))
    mjds = time.mjd * 86400

    altaz = vis.phasecentre.transform_to(AltAz(obstime=time, location=location))
    # these are used in beam models and should be done separately for each station location
    # for our purposes though, just use a common location
    theta = np.pi / 2 - altaz.alt.radian
    cos_term = np.cos(theta)

    beam_itrf = radec_to_xyz(vis.phasecentre.ra, vis.phasecentre.dec, mjds)

    # ITRS coordinates for zenith at the central time step
    pointing = SkyCoord(
        alt=90,
        az=0,
        unit="deg",
        frame="altaz",
        obstime=time,
        location=location,
    ).transform_to(ITRS(obstime=time))
    zen_itrf = np.asarray(pointing.cartesian.xyz.transpose())

    return MetaData(
        time=time,
        mjds=mjds,
        location=location,
        stations=stations,
        nstation=nstation,
        zen_itrf=zen_itrf,
        telescope=telescope,
        cos_term=cos_term,
        beam_itrf=beam_itrf,
        ant1=ant1,
        ant2=ant2,
    )
