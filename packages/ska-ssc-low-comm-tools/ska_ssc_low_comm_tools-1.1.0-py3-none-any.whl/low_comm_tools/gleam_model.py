#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
from typing import NamedTuple, cast

import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from astropy.coordinates import FK5, SkyCoord
from astropy.table import Row, Table
from astropy.time import Time
from astroquery.vizier import Vizier
from casacore.tables import table
from matplotlib.figure import Figure
from radio_beam import Beam, Beams
from rm_lite.utils import fitting

from low_comm_tools.beam_model import beam_model_separation
from low_comm_tools.log_config import logger

ZERO_BEAM = Beam(0)


def get_catalogue_values(
    target: SkyCoord,
    radius: u.Quantity,
) -> Table:
    catalogs = {
        "GLEAM-X": "VIII/113/catalog2",
        "GLEAM": "VIII/100/gleamegc",
        "GLEAM-Gal": "VIII/102/gleamgal",
    }
    source_name_columns = {
        "GLEAM-X": "GLEAM-X",
        "GLEAM": "GLEAM",
        "GLEAM-Gal": "GLEAM",
    }

    for catalog_name, catalog in catalogs.items():
        vizier = Vizier(columns=["**"], catalog=catalog)
        vizier.ROW_LIMIT = -1
        result = vizier.query_region(target, radius=radius)
        if len(result) > 0:
            logger.info(f"Using {catalog_name}")
            table = Table(result[0])
            table.rename_column(
                source_name_columns[catalog_name],
                "source_name",
            )
            table.sort("Fintwide", reverse=True)
            return table
        logger.info(f"No matches found in {catalog_name}...")

    msg = "No sources found!"
    raise ValueError(msg)


class GleamRow(NamedTuple):
    row: Row
    separation: u.Quantity
    size_deconv: Beam


def best_match_catalogue(
    target: SkyCoord,
    search_radius: u.Quantity,
    obs_time: Time,
) -> GleamRow:
    catalogue = get_catalogue_values(
        target=target,
        radius=search_radius,
    )
    cat_coords = SkyCoord(
        catalogue["RAJ2000"],
        catalogue["DEJ2000"],
    )
    cat_coords = cat_coords.transform_to(FK5(equinox=obs_time))
    idx, sep, _ = target.match_to_catalog_sky(catalogcoord=cat_coords)
    idx = int(idx)
    row = cast(Row, catalogue[idx])
    psf = Beam(
        major=row["psfawide"] * u.arcsec,
        minor=row["psfbwide"] * u.arcsec,
        pa=row["pawide"] * u.deg,
    )
    size = Beam(
        major=row["awide"] * u.arcsec,
        minor=row["bwide"] * u.arcsec,
        pa=row["psfPAwide"] * u.deg,
    )
    size_deconv = size.deconvolve(psf, failure_returns_pointlike=True)
    return GleamRow(row=row, separation=sep, size_deconv=size_deconv)


def _process_gleam_row(
    gleam_row: GleamRow,
) -> pl.DataFrame:
    frequencies: list[float] = []
    fluxes: list[float] = []
    errors: list[float] = []
    integrated_flux_col = "Fint"

    for col in gleam_row.row.columns:
        if (
            col.startswith(integrated_flux_col)
            and col[len(integrated_flux_col)].isnumeric()
        ):
            frequency = float(col[len(integrated_flux_col) :])
            flux = float(gleam_row.row[col])
            frequencies.append(frequency)
            fluxes.append(flux)
            error_col = f"e_{col}"
            if error_col in gleam_row.row.columns:
                error = float(gleam_row.row[error_col])
                if error < 0:
                    logger.warning(
                        f"Negative error for {error_col}: {error}. Setting to NaN."
                    )
                    error = np.nan
                errors.append(error)
            else:
                logger.warning(f"{error_col} not found in row")
                errors.append(np.nan)

    flux_arr = np.array(fluxes)
    freq_arr = np.array(frequencies)
    error_arr = np.array(errors)

    if gleam_row.separation > 0 * u.deg:
        attenuation = beam_model_separation(
            separation=gleam_row.separation,
            frequency=frequencies * u.MHz,
        )
        flux_arr = flux_arr * attenuation
        # Of course the model is perfect... /s
        error_arr = error_arr * attenuation

    return pl.DataFrame(
        {
            "frequency_mhz": freq_arr,
            "flux_int": flux_arr,
            "e_flux_int": error_arr,
        }
    )


class FluxDF(NamedTuple):
    source_name: str
    row_df: pl.DataFrame
    gleam_row: GleamRow


def make_flux_df(
    target: SkyCoord,
    radius: u.Quantity,
    obs_time: Time,
) -> FluxDF:
    gleam_row = best_match_catalogue(
        target,
        search_radius=radius,
        obs_time=obs_time,
    )

    row_df = _process_gleam_row(gleam_row=gleam_row)

    return FluxDF(
        source_name=str(gleam_row.row["source_name"]),
        row_df=row_df,
        gleam_row=gleam_row,
    )


class SkyModelDicts(NamedTuple):
    row_df_dict: dict[str, pl.DataFrame]
    coord_dict: dict[str, SkyCoord]
    size_dict: dict[str, Beam]


def make_sky_model_dicts(
    target: SkyCoord,
    radius: u.Quantity,
) -> SkyModelDicts:
    gleam_cat = get_catalogue_values(target=target, radius=radius)
    cat_coords = SkyCoord(
        gleam_cat["RAJ2000"],
        gleam_cat["DEJ2000"],
    )
    separations = cat_coords.separation(target)
    psfs = Beams(
        major=gleam_cat["psfawide"].to(u.arcsec),
        minor=gleam_cat["psfbwide"].to(u.arcsec),
        pa=gleam_cat["pawide"].to(u.deg),
    )
    sizes = Beams(
        major=gleam_cat["awide"].to(u.arcsec),
        minor=gleam_cat["bwide"].to(u.arcsec),
        pa=gleam_cat["psfPAwide"].to(u.deg),
    )

    coord_dict: dict[str, SkyCoord] = {}
    row_df_dict: dict[str, pl.DataFrame] = {}
    size_dict: dict[str, Beam] = {}
    for coord, separation, row, psf, size in zip(
        cat_coords,
        separations,
        gleam_cat,
        psfs,
        sizes,
        strict=True,
    ):
        size_deconv = size.deconvolve(psf, failure_returns_pointlike=True)
        gleam_row = GleamRow(
            row=row,
            separation=separation,
            size_deconv=size_deconv,
        )
        row_df = _process_gleam_row(gleam_row=gleam_row)
        source_name = row["source_name"]
        row_df_dict[source_name] = row_df
        coord_dict[source_name] = coord
        size_dict[source_name] = size_deconv

    return SkyModelDicts(
        row_df_dict=row_df_dict,
        coord_dict=coord_dict,
        size_dict=size_dict,
    )


def plot_fitted_sed(
    flux_df: pl.DataFrame,
    ref_freq_hz: float,
    fit_result: fitting.FitResult,
) -> Figure:
    freq_arr_hz = flux_df["frequency_mhz"].to_numpy() * 1e6
    fig, ax = plt.subplots()
    ax.errorbar(
        freq_arr_hz / 1e6,
        flux_df["flux_int"].to_numpy(),
        yerr=flux_df["e_flux_int"].to_numpy(),
        fmt="o",
    )
    ax.plot(
        freq_arr_hz / 1e6,
        fit_result.stokes_i_model_func(freq_arr_hz / ref_freq_hz, *fit_result.popt),
    )
    ax.set(
        xlabel="Frequency  / MHz ",
        ylabel="Integrated flux Density / Jy",
        title="Fitted SED",
    )
    return fig


class FittedSED(NamedTuple):
    fit_result: fitting.FitResult
    ref_freq_hz: float
    plot: Figure | None


class FittingError(Exception): ...


def fit_power_law(
    flux_df: pl.DataFrame, make_plot: bool = False, ref_freq_hz: float | None = None
) -> FittedSED | None:
    """ """
    freq_arr_hz = flux_df["frequency_mhz"].to_numpy() * 1e6
    if ref_freq_hz is None:
        ref_freq_hz = float(np.round(np.mean(freq_arr_hz), decimals=2))
    try:
        fit_result = fitting.dynamic_fit(
            freq_arr_hz=freq_arr_hz,
            ref_freq_hz=ref_freq_hz,
            stokes_i_arr=flux_df["flux_int"].to_numpy(),
            stokes_i_error_arr=flux_df["e_flux_int"].to_numpy(),
            fit_order=3,
            fit_type="log",
        )
    except Exception:
        mean_flux_mjy = flux_df["flux_int"].mean() * 1e3  # type: ignore[operator]
        msg = f"Failed to fit SED. Mean apparent flux is {mean_flux_mjy:0.2f}mJy. Consider reducing radius..."
        logger.error(msg)
        return None

    fig: Figure | None = None
    if make_plot:
        fig = plot_fitted_sed(
            flux_df=flux_df,
            ref_freq_hz=ref_freq_hz,
            fit_result=fit_result,
        )
    return FittedSED(
        fit_result=fit_result,
        ref_freq_hz=ref_freq_hz,
        plot=fig,
    )


def _aocal_model_csv(
    coord: SkyCoord,
    sed: list[float],
    ref_freq_hz: float,
    size: Beam,
    source_name: str = "s0",
    include_header: bool = True,
) -> list[str]:
    # Example format
    # Format = Name, Type, Ra, Dec, I, SpectralIndex, LogarithmicSI, ReferenceFrequency='888500000.0', MajorAxis, MinorAxis, Orientation
    # s0,POINT,19:39:25.0261,-63.42.45.625,14.23058308,[0.42280414,-1.74293221,0.605334],true,888500000.0,,,

    # Common Supported Column Names
    # Name — Source/component name
    # Type — Component type (e.g., POINT, GAUSSIAN)
    # Ra — Right Ascension (sexagesimal or decimal)
    # Dec — Declination (sexagesimal or decimal)
    # I — Stokes I flux (Jy)
    # SpectralIndex — List of spectral index or polynomial coefficients (e.g., [0.7, -0.1])
    # LogarithmicSI — true for power law, false for polynomial
    # ReferenceFrequency — Reference frequency (Hz)
    # MajorAxis — Major axis (arcsec, for Gaussian)
    # MinorAxis — Minor axis (arcsec, for Gaussian)
    # Orientation — Orientation angle (degrees)
    # Patch — Patch name (optional, for grouping)
    # (sometimes) Q, U, V — Stokes Q/U/V fluxes (if supported by your version)

    if size == ZERO_BEAM:
        src_type = "POINT"
        major = ""
        minor = ""
        pa = ""
    else:
        src_type = "GAUSSIAN"
        major = f"{size.major.to(u.arcsec).value}"
        minor = f"{size.minor.to(u.arcsec).value}"
        pa = f"{size.pa.to(u.deg).value}"

    ra_str = coord.ra.to_string(unit=u.hour, sep=":", pad=True)
    dec_str = coord.dec.to_string(unit=u.deg, sep=".", alwayssign=True, pad=True)
    ref_flux = sed[0]
    spectral_terms = f"[{', '.join(map(str, sed[1:]))}]"

    header = f"format = Name, Type, Ra, Dec, I, SpectralIndex, LogarithmicSI, ReferenceFrequency='{ref_freq_hz}', MajorAxis, MinorAxis, Orientation"
    # TODO: Support extended sources, polynomials etc.
    src_line = f"{source_name},{src_type},{ra_str},{dec_str},{ref_flux},{spectral_terms},true,{ref_freq_hz},{major},{minor},{pa}"

    if not include_header:
        return [src_line]
    return [header, src_line]


def _aocal_model_skymodel(
    coord: SkyCoord,
    sed: list[float],
    ref_freq_hz: float,
    size: Beam,
    source_name: str = "s0",
    include_header: bool = True,
) -> list[str]:
    ## Example format
    # skymodel fileformat 1.1
    # source {
    # name "J122906+020251"
    # component {
    #     type point
    #     position 12:29:06.69982572 +02.03.08.59762998
    #     sed {
    #     frequency 152.35 MHz
    #     fluxdensity Jy 88.64482341801 0 0 0
    #     spectral-index { -0.6519563419265709 0.44503898644144735 1.34890623346774 }
    #     }
    #   }
    # }
    ## From Hyperdrive documentation:
    # source {
    #   name "J002549-260211"
    #   component {
    #     type point
    #     position 0h25m49.2s -26d02m13s
    #     measurement {
    #       frequency 80 MHz
    #       fluxdensity Jy 15.83 0 0 0
    #     }
    #     measurement {
    #       frequency 100 MHz
    #       fluxdensity Jy 16.77 0 0 0
    #     }
    #   }
    # }
    # source {
    #   name "COM000338-1517"
    #   component {
    #     type gaussian
    #     position 0h03m38.7844s -15d17m09.7338s
    #     shape 89.05978540785397 61.79359416237104 89.07023307815388
    #     sed {
    #       frequency 160 MHz
    #       fluxdensity Jy 0.3276758375536325 0 0 0
    #       spectral-index { -0.9578697792073567 0.00 }
    #     }
    #   }
    # }

    if size == ZERO_BEAM:
        src_type = "point"
        shape_str = ""
    else:
        src_type = "gaussian"
        major = size.major.to(u.arcsec).value
        minor = size.minor.to(u.arcsec).value
        pa = size.pa.to(u.deg).value
        shape_str = f"shape {major} {minor} {pa}"

    ra_str = coord.ra.to_string(unit=u.hour, sep=":", pad=True)
    dec_str = coord.dec.to_string(unit=u.deg, sep=".", alwayssign=True, pad=True)
    ref_flux = sed[0]
    spectral_terms = f"{{{', '.join(map(str, sed[1:]))}}}"

    header = "skymodel fileformat 1.1"
    src_lines = f"""source {{
    name "{source_name}"
    component {{
        type {src_type}
        position {ra_str} {dec_str}
        {shape_str}
        sed {{
            frequency {ref_freq_hz / 1e6} MHz
            fluxdensity Jy {ref_flux} 0 0 0
            spectral-index {spectral_terms}
        }}
    }}
}}
""".split()

    if not include_header:
        return src_lines

    return [header, *src_lines]


def create_sky_model_single(
    pointing: SkyCoord,
    radius: u.Quantity,
    obs_time: Time,
    model_type: str = "csv",
    ref_freq_hz: float | None = None,
    precess: bool = False,
) -> list[str]:
    """
    Create a model for the AO calibration.
    """

    source_name, flux_df, gleam_row = make_flux_df(
        target=pointing,
        radius=radius,
        obs_time=obs_time,
    )
    fitted_sed = fit_power_law(flux_df=flux_df, ref_freq_hz=ref_freq_hz)
    if fitted_sed is None:
        msg = "Failed to fit SED"
        raise ValueError(msg)
    if ref_freq_hz is None:
        ref_freq_hz = fitted_sed.ref_freq_hz

    match model_type:
        case "csv":
            model_func = _aocal_model_csv
        case "skymodel":
            model_func = _aocal_model_skymodel
        case _:
            msg = f"Unknown model type: {model_type}"
            raise ValueError(msg)

    if precess:
        apparent_pointing = pointing.transform_to(FK5(equinox=obs_time))
        # Need for de-precessing
        apparent_fake = SkyCoord(ra=apparent_pointing.ra, dec=apparent_pointing.dec)

        pointing = pointing.directional_offset_by(
            position_angle=apparent_fake.position_angle(pointing),
            separation=apparent_fake.separation(pointing),
        )

    return model_func(
        coord=pointing,
        sed=list(fitted_sed.fit_result.popt),
        ref_freq_hz=ref_freq_hz,
        source_name=source_name,
        size=gleam_row.size_deconv,
    )


def create_sky_model_wide(
    pointing: SkyCoord,
    radius: u.Quantity,
    obs_time: Time,
    model_type: str = "csv",
    ref_freq_hz: float | None = None,
    precess: bool = False,
) -> list[str]:
    # TODO: Handle time
    _ = obs_time

    sky_model_dict, coord_dict, size_dict = make_sky_model_dicts(
        target=pointing,
        radius=radius,
    )

    match model_type:
        case "csv":
            model_func = _aocal_model_csv
        case "skymodel":
            model_func = _aocal_model_skymodel
        case _:
            msg = f"Unknown model type: {model_type}"
            raise ValueError(msg)

    model_str_list: list[str] = []
    for i, (source_name, flux_df) in enumerate(sky_model_dict.items()):
        fitted_sed = fit_power_law(flux_df=flux_df, ref_freq_hz=ref_freq_hz)
        if fitted_sed is None:
            continue
        coord = coord_dict[source_name]

        # For the CSV model, the ref_freq must be the same for all sources
        # And also given in the header
        if ref_freq_hz is None and i == 0 and model_type == "csv":
            ref_freq_hz = fitted_sed.ref_freq_hz

        if ref_freq_hz is None:
            msg = "`ref_freq_hz` must be a float (got None)"
            raise ValueError(msg)

        if precess:
            logger.info("Correcting for precession!")
            apparent_coord = coord.transform_to(FK5(equinox=obs_time))
            # Need for de-precessing
            apparent_fake = SkyCoord(ra=apparent_coord.ra, dec=apparent_coord.dec)
            coord = coord.directional_offset_by(
                position_angle=apparent_fake.position_angle(coord),
                separation=apparent_fake.separation(coord),
            )

        model_str_list += model_func(
            coord=coord,
            sed=list(fitted_sed.fit_result.popt),
            ref_freq_hz=ref_freq_hz,
            source_name=source_name,
            include_header=i == 0,
            size=size_dict[source_name],
        )

    return model_str_list


def get_coord_from_ms(
    ms_path: str | Path,
    field: int = 0,
) -> SkyCoord:
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)
    with table(str(ms_path / "FIELD"), ack=False) as tab:
        field_row = tab.getcell("PHASE_DIR", field).flatten()
        return SkyCoord(
            ra=field_row[0],
            dec=field_row[1],
            unit=u.rad,
        )


def get_time_from_ms(
    ms_path: str | Path,
) -> Time:
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)
    with table(str(ms_path), ack=False) as tab:
        times_mjds = np.unique(tab.getcol("TIME_CENTROID")[:]).flatten() * u.s

    times = Time(times_mjds, format="mjd", scale="utc")

    return Time(times.mean())


def get_freq_from_ms(
    ms_path: str | Path,
) -> u.Quantity:
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)
    with table(str(ms_path / "SPECTRAL_WINDOW"), ack=False) as tab:
        return np.unique(tab.getcol("CHAN_FREQ")[:]).flatten() * u.Hz


def create_ao_cal_model_from_ms(
    ms_path: str | Path,
    output_path: str | Path | None = None,
    model_type: str = "csv",
    sky_type: str = "single",
    ref_freq_hz: float | None = None,
    radius: u.Quantity = 1 * u.deg,
    precess: bool = False,
) -> list[str]:
    """
    Create a model for the AO calibration from a measurement set.
    """
    ms_path = Path(ms_path)
    coord = get_coord_from_ms(ms_path)
    time = get_time_from_ms(ms_path)
    freqs = get_freq_from_ms(ms_path)

    if ref_freq_hz is None:
        ref_freq_hz = freqs.mean().to(u.Hz).value

    match sky_type:
        case "single":
            ao_cal_model_func = create_sky_model_single
        case "wide":
            ao_cal_model_func = create_sky_model_wide
        case _:
            msg = f"Unknown {sky_type}"
            raise ValueError(msg)

    ao_model_str_lines = ao_cal_model_func(
        pointing=coord,
        radius=radius,
        model_type=model_type,
        ref_freq_hz=ref_freq_hz,
        obs_time=time,
        precess=precess,
    )

    if output_path is None:
        output_path = (
            ms_path.parent / f"ao_cal_model_{ms_path.stem}.{sky_type}.{model_type}"
        )
    else:
        output_path = Path(output_path)

    with output_path.open("w") as f:
        f.write("\n".join(ao_model_str_lines) + "\n")
    logger.info(f"AO calibration model written to {output_path}")
    return ao_model_str_lines


def get_parser(
    add_help: bool = True,
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create AO calibration model from MS.",
        add_help=add_help,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("ms_path", type=Path, help="Path to the measurement set.")
    parser.add_argument(
        "-o",
        "--output-path",
        type=str,
        default=None,
        help="Path to save the AO calibration model.",
    )
    parser.add_argument(
        "-m",
        "--model-type",
        type=str,
        choices=["csv", "skymodel"],
        default="csv",
        help="Type of model to create.",
    )
    parser.add_argument(
        "-s",
        "--sky-type",
        type=str,
        choices=["single", "wide"],
        default="single",
        help="Type of sky model to create. 'single' will create a single source mode. Wide will sample many, attenudated by the beam.",
    )
    parser.add_argument(
        "-f", "--reffreq", type=float, default=None, help="Reference frequency in MHz"
    )
    parser.add_argument(
        "-r",
        "--radius",
        type=float,
        default=1,
        help="Search radius for sources in degrees",
    )
    parser.add_argument(
        "-p",
        "--precess",
        action="store_true",
    )
    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    ref_freq = args.reffreq
    if ref_freq is not None:
        ref_freq *= 1e6

    _ = create_ao_cal_model_from_ms(
        ms_path=args.ms_path,
        output_path=args.output_path,
        model_type=args.model_type,
        sky_type=args.sky_type,
        ref_freq_hz=ref_freq,
        radius=args.radius * u.deg,
        precess=args.precess,
    )


if __name__ == "__main__":
    main()
