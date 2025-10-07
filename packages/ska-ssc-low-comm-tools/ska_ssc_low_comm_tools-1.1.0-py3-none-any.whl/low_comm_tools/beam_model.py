from __future__ import annotations

from functools import cache
from typing import Any

import astropy.units as u
import healpy as hp
import numpy as np
import numpy.typing as npt
import polars as pl
from astropy.constants import c as speed_of_light
from astropy.coordinates import SkyCoord
from numpy.typing import NDArray
from scipy.optimize import curve_fit
from scipy.special import j1


def get_beam_data() -> pl.DataFrame:
    """Get primary beam data

    A bit of a useless function, but could be replaced with proper models.

    Returns:
        pl.DataFrame: Fits to primary beam in a DataFrame
    """
    # Sobey+25 beams
    return pl.DataFrame(
        {
            "freq_mhz": [
                50.00,
                50.78,
                51.5625,
                200,
                200.78125,
                201.5625,
                347.6560,
                348.4375,
                349.21875,
            ],
            "fwhm_g_deg": [
                34.138,
                32.216,
                30.559,
                1.697,
                1.690,
                1.681,
                0.991,
                1.000,
                0.987,
            ],
            "fwhm_a_deg": [
                9.304,
                9.177,
                9.124,
                1.750,
                1.742,
                1.732,
                1.030,
                1.038,
                1.027,
            ],
        }
    )


## Fitting utils
def _one_over(x: float, a: float, c: float) -> float:
    """1/x function for itting

    Args:
        x (float): x-values
        a (float): Amplitude parameter
        c (float): Offset parameter

    Returns:
        float: 1/x value
    """
    return a * (1 / x) + c


@cache
def _fit_beam(
    model_type: str = "airy",
) -> npt.NDArray[np.floating[Any]]:
    match model_type:
        case "gaussian":
            column = "fwhm_g_deg"
        case "airy":
            column = "fwhm_a_deg"
        case _:
            msg = f"Unknown {model_type=}"
            raise NotImplementedError(msg)

    beam_df = get_beam_data()
    popt, _ = curve_fit(_one_over, xdata=beam_df["freq_mhz"], ydata=beam_df[column])  # type: ignore[arg-type]
    return popt


@np.vectorize
def _gaussian_fit_beam(sep_deg: float, freq_mhz: float) -> float:
    """Fit of Gaussian beam to SKA-Low from Sobey+25

    Args:
        sep_deg (float): Separation from beam centre in degrees
        freq_mhz (float): Observing frequency in MHz

    Returns:
        float: Beam response
    """
    # I'm fitting over frequency with 1/x because I don't
    #  have the exact models / data to hand

    popt = _fit_beam("gaussian")
    fwhm_deg = _one_over(freq_mhz, *popt)
    sigma = fwhm_deg / (2 * np.sqrt(2 * np.log(2)))
    mean = 0
    amp = 1
    return float(amp * np.exp(-((sep_deg - mean) ** 2) / (2 * sigma**2)))


@np.vectorize
def jinc(x: float) -> float:
    if x == 0:
        return 0.5
    return float(j1(x) / x)


@np.vectorize
def _airy_fit_beam(sep_deg: float, freq_mhz: float) -> float:
    """Fit of Airy beam to SKA-Low from Sobey+25

    Args:
        sep_deg (float): Separation from beam centre in degrees
        freq_mhz (float): Observing frequency in MHz

    Returns:
        float: Beam response
    """
    # I'm fitting over frequency with 1/x because I don't
    #  have the exact models / data to hand
    wave = speed_of_light / (freq_mhz * u.MHz)
    wave_m = wave.to(u.m).value

    popt = _fit_beam("airy")
    fwhm_deg = _one_over(freq_mhz, *popt)
    fwhm_rad = np.deg2rad(fwhm_deg)

    diameter = 1.029 * wave_m / fwhm_rad

    x = (np.pi * diameter / wave_m) * np.sin(np.deg2rad(sep_deg))
    amp = 1
    return float(amp * (2 * jinc(x)) ** 2)


def beam_model_hpx(
    pointing: SkyCoord,
    frequency: u.Quantity,
    model_type: str = "airy",
    nside: int = 512,
) -> NDArray[np.floating[Any]]:
    """Evaluate the beam model on an all-sky HEALPix grid.

    Args:
        target (SkyCoord): Pointing target
        frequency (u.Quantity): Observing frequency
        model_type (str, optional): Beam model. Can be "gaussian" or "airy". Defaults to "airy".
        nside (int, optional): HEALPix N_side. Defaults to 512.

    Raises:
        NotImplementedError: If `model_type` is not supported

    Returns:
        np.typing.NDArray[np.floating[Any]]: 1D HEALPix array
    """
    # Create HPX grid and evaluate where the target is on the grid
    hpx_grid = np.arange(hp.nside2npix(nside=nside))
    ra_hpx, dec_hpx = hp.pix2ang(nside=nside, ipix=hpx_grid, lonlat=True)
    hpx_coords = SkyCoord(ra=ra_hpx * u.deg, dec=dec_hpx * u.deg, frame="icrs")
    separations = pointing.separation(hpx_coords)
    match model_type:
        case "gaussian":
            model_func = _gaussian_fit_beam
        case "airy":
            model_func = _airy_fit_beam
        case _:
            msg = f"Unknown {model_type=}"
            raise NotImplementedError(msg)

    return model_func(  # type: ignore[no-any-return]
        sep_deg=separations.to(u.deg).value, freq_mhz=frequency.to(u.MHz).value
    )


def beam_model_separation(
    separation: u.Quantity,
    frequency: u.Quantity,
    model_type: str = "airy",
) -> NDArray[np.floating[Any]]:
    match model_type:
        case "gaussian":
            model_func = _gaussian_fit_beam
        case "airy":
            model_func = _airy_fit_beam
        case _:
            msg = f"Unknown {model_type=}"
            raise NotImplementedError(msg)

    return model_func(  # type: ignore[no-any-return]
        sep_deg=separation.to(u.deg).value, freq_mhz=frequency.to(u.MHz).value
    )


def beam_model_target(
    pointing: SkyCoord,
    target: SkyCoord,
    frequency: u.Quantity,
    model_type: str = "airy",
) -> NDArray[np.floating[Any]]:
    separation = pointing.separation(target)
    return beam_model_separation(
        separation=separation, frequency=frequency, model_type=model_type
    )
