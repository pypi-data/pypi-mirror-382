from __future__ import annotations

import argparse
import warnings
from pathlib import Path
from typing import Any, NamedTuple

import numpy as np
import numpy.typing as npt
import xarray as xr
from astropy.coordinates import AltAz
from ska_sdp_datamodels.calibration.calibration_create import (
    create_gaintable_from_visibility,
)
from ska_sdp_datamodels.calibration.calibration_model import GainTable
from ska_sdp_datamodels.sky_model import SkyComponent
from ska_sdp_datamodels.visibility import Visibility
from ska_sdp_datamodels.visibility.vis_io_ms import create_visibility_from_ms
from ska_sdp_func_python.calibration.solvers import solve_gaintable
from ska_sdp_func_python.preprocessing.averaging import averaging_frequency
from ska_sdp_func_python.preprocessing.flagger import rfi_flagger
from ska_sdp_instrumental_calibration.data_managers.data_export import (
    export_clock_to_h5parm,
    export_gaintable_to_h5parm,
)
from ska_sdp_instrumental_calibration.processing_tasks.calibration import (
    apply_gaintable,
)
from ska_sdp_instrumental_calibration.processing_tasks.delay import (
    apply_delay,
    calculate_delay,
)
from ska_sdp_instrumental_calibration.processing_tasks.lsm import (
    convert_model_to_skycomponents,
    generate_lsm_from_gleamegc,
)
from ska_sdp_instrumental_calibration.processing_tasks.predict import (
    predict_from_components,
)

from low_comm_tools.plotting.sdp_calibrate import plot_gains, plot_vis
from low_comm_tools.sdp.utils import MetaData, pre_calculate_metadata, radec_to_xyz

np.set_printoptions(linewidth=120)
warnings.simplefilter(action="ignore", category=FutureWarning)


def get_vis_data(
    dataset: Path,
    fave_init: int = 4,
) -> Visibility:
    # ============================================================================ #
    # vis data

    # set up some averaging intervals (for test.ms, x36 = 781.25 kHz CBF coarse channel)
    #  - initial averaging on input

    vis: Visibility = create_visibility_from_ms(dataset.as_posix())[0]

    # crop and clean the data a bit
    #  - get rid of autos
    vis = vis.isel(baselines=(vis.antenna1 != vis.antenna2))
    #  - get rid of the short baseline
    #  - could just flag...
    vis = vis.isel(baselines=np.arange(1, len(vis.baselines)))
    #  - flag before downsampling?
    vis = rfi_flagger(
        vis,
        sampling=1,
        threshold_magnitude=5,
        threshold_variation=5,
        threshold_broadband=5,
    )
    #  - downsample frequency
    if fave_init > 1:
        vis = averaging_frequency(vis, freqstep=fave_init)
    #  - the ms has ant2 <= ant, and create_visibility_from_ms will reorder
    #  - however, it conjugates but does not transpose. So do that now
    #  - this should not be needed in inst-cal with the new MSv4 interface
    vis.vis.data[:, :, :, [0, 1, 2, 3]] = vis.vis.data[:, :, :, [0, 2, 1, 3]]

    return vis


def load_skymodel(
    vis: Visibility,
    gleamfile: Path,
) -> list[SkyComponent]:
    # ============================================================================ #
    # sky model

    # generate sky model
    lsm = generate_lsm_from_gleamegc(
        gleamfile=gleamfile.as_posix(),  # "../gleamegc.dat"
        phasecentre=vis.phasecentre,
        fov=5.0,
        flux_limit=1.0,
    )
    return convert_model_to_skycomponents(lsm, vis.frequency.data)  # type: ignore[no-any-return]


def model_vis(
    dataset: Path,
    vis: Visibility,
    lsm_components: list[SkyComponent],
    metadata: MetaData,
    freq_precal: int = 1,
) -> tuple[Visibility, Visibility]:
    # ============================================================================ #
    # vis models

    mdlvis = vis.assign({"vis": xr.zeros_like(vis.vis)})

    # predict_from_components(
    #     vis_inst,
    #     lsm_components,
    #     beam_type="everybeam",
    #     eb_ms=dataset,
    #     eb_coeffs="",  # this is no longer needed
    # )

    # Want to apply an extra cos(theta) term.
    compvis = vis.assign({"vis": xr.zeros_like(vis.vis)})
    for comp in lsm_components:
        # these should be done separately for each station location
        # for our purposes though, just use a common location
        altaz = comp.direction.transform_to(
            AltAz(obstime=metadata.time, location=metadata.location)
        )
        theta = np.pi / 2 - altaz.alt.radian

        compvis.vis.data[:] = 0j
        predict_from_components(
            compvis,
            [comp],
            beam_type="everybeam",
            eb_ms=dataset.as_posix(),
            eb_coeffs="",  # this is no longer needed
        )
        mdlvis.vis.data += compvis.vis.data * np.cos(theta) ** 2

    # ============================================================================ #
    # further average vis and vis model
    #  - needed for both to include bandwidth smearing in the model
    #  - in RCAL will instead estimate the decorrelation level

    #  - extra averaging before calibration (e.g for RCAL or iono RM fits)
    # freq_precal = 36 // fave_init
    if freq_precal > 1:
        vis = averaging_frequency(vis, freqstep=freq_precal)
        mdlvis = averaging_frequency(mdlvis, freqstep=freq_precal)
    return vis, mdlvis


def beam_model(
    vis: Visibility,
    metadata: MetaData,
) -> npt.NDArray[np.complex128]:
    # ============================================================================ #
    # field centre beam model

    jones_eb = np.zeros((metadata.nstation, len(vis.frequency), 2, 2), "complex")

    for ch, freq in enumerate(vis.frequency.data):
        Jz = metadata.telescope.station_response(
            metadata.time.mjd * 86400, 0, freq, metadata.zen_itrf, metadata.zen_itrf
        )
        scale = np.sqrt(2) / np.linalg.norm(Jz)
        for stn, _station in enumerate(metadata.stations):
            beam_itrf = radec_to_xyz(
                vis.phasecentre.ra, vis.phasecentre.dec, metadata.mjds
            )
            jones_eb[stn, ch] = (
                metadata.telescope.station_response(
                    metadata.mjds, stn, freq, beam_itrf, beam_itrf
                )
                * scale
                * metadata.cos_term
            )
    return jones_eb


class CalibratedData(NamedTuple):
    gaintable: GainTable
    calvis: Visibility | xr.Dataset
    delaytable: xr.Dataset | GainTable
    delay_and_gaintable: xr.Dataset | GainTable


def calibrate(
    vis: Visibility,
    mdlvis: Visibility,
    jones_eb: npt.NDArray[np.complexfloating[Any, Any]],
    metadata: MetaData,
    centre_correct: bool = False,
    refant: int = 0,
) -> CalibratedData:
    # ============================================================================ #
    # calibration

    # Remove central beam response before calibration?

    if centre_correct:
        invjones_eb = np.linalg.pinv(jones_eb)
        tmp = vis.copy(deep=True)
        vis.vis.data = np.einsum(
            "bfpx,tbfxy,bfqy->tbfpq",
            invjones_eb[metadata.ant1],
            tmp.vis.data.reshape((*vis.vis.shape[:3], 2, 2)),
            invjones_eb[metadata.ant2].conj(),
        ).reshape(vis.vis.shape)
        tmp = mdlvis.copy(deep=True)
        mdlvis.vis.data = np.einsum(
            "bfpx,tbfxy,bfqy->tbfpq",
            invjones_eb[metadata.ant1],
            tmp.vis.data.reshape((*vis.vis.shape[:3], 2, 2)),
            invjones_eb[metadata.ant2].conj(),
        ).reshape(vis.vis.shape)

    # generate bandpass tables
    timeslice = vis.time.data.max() - vis.time.data.min()
    gaintable = create_gaintable_from_visibility(
        vis, jones_type="B", timeslice=timeslice
    )
    assert len(gaintable.interval) == 1
    assert len(gaintable.frequency) == len(vis.frequency)
    # The table interval isn't set correctly when there is a single solution interval.
    # Set it equal to timeslice plus a little to make sure the last vis sample is included.
    gaintable["interval"].data[0] = timeslice + 1e-5

    # Initialise gains
    gaintable = solve_gaintable(
        vis=vis.copy(deep=True),
        modelvis=mdlvis.copy(deep=True),
        gain_table=gaintable,
        solver="gain_substitution",
        phase_only=False,
        niter=200,
        tol=1e-06,
        crosspol=False,
        normalise_gains=None,
        jones_type="B",
        refant=refant,
    )

    # Include polarised terms
    gaintable = solve_gaintable(
        vis=vis.copy(deep=True),
        modelvis=mdlvis.copy(deep=True),
        gain_table=gaintable,
        # solver="normal_equations",
        # niter=200,
        # tol=1e-04,
        solver="jones_substitution",
        niter=50,
        tol=1e-03,
        phase_only=False,
        crosspol=False,
        normalise_gains=None,
        jones_type="B",
        refant=refant,
    )

    # Delay calibration
    delaytable = calculate_delay(gaintable, oversample=1)
    delay_and_gaintable = apply_delay(gaintable, delaytable)

    calvis = apply_gaintable(
        vis=vis.copy(deep=True), gt=delay_and_gaintable, inverse=True
    )

    return CalibratedData(
        gaintable=gaintable,
        calvis=calvis,
        delay_and_gaintable=delay_and_gaintable,
        delaytable=delaytable,
    )


class CalibrationResults(NamedTuple):
    vis: Visibility
    mdlvis: Visibility
    calvis: Visibility | xr.Dataset
    gaintable: GainTable | xr.Dataset
    jones_eb: npt.NDArray[np.complex128]
    metadata: MetaData


def instrumental_calibration(
    dataset: Path,
    gleamfile: Path,
    fave_init: int = 4,
    freq_precal: int = 1,
    centre_correct: bool = False,
    refant: int = 0,
) -> CalibrationResults:
    vis = get_vis_data(
        dataset=dataset,
        fave_init=fave_init,
    )
    metadata = pre_calculate_metadata(vis=vis, dataset=dataset)
    lsm_components = load_skymodel(
        vis=vis,
        gleamfile=gleamfile,
    )
    vis, mdlvis = model_vis(
        dataset=dataset,
        vis=vis,
        metadata=metadata,
        lsm_components=lsm_components,
        freq_precal=freq_precal,
    )
    jones_eb = beam_model(
        vis=vis,
        metadata=metadata,
    )
    calibrated_data = calibrate(
        vis=vis,
        mdlvis=mdlvis,
        jones_eb=jones_eb,
        metadata=metadata,
        centre_correct=centre_correct,
        refant=refant,
    )

    export_gaintable_to_h5parm(
        gaintable=calibrated_data.delay_and_gaintable,  # pyright: ignore[reportArgumentType]
        filename=dataset.with_suffix(".delay.gaintable.h5parm").as_posix(),
    )

    export_clock_to_h5parm(
        calibrated_data.delaytable,
        filename=dataset.with_suffix(".delay.clock.h5parm").as_posix(),
    ).compute()

    export_gaintable_to_h5parm(
        gaintable=calibrated_data.gaintable,
        filename=dataset.with_suffix(".gaintable.h5parm").as_posix(),
        squeeze=True,
    )

    return CalibrationResults(
        vis=vis,
        mdlvis=mdlvis,
        calvis=calibrated_data.calvis,
        gaintable=calibrated_data.delay_and_gaintable,
        jones_eb=jones_eb,
        metadata=metadata,
    )


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Mitch's script for INST calbration",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("ms_path", type=Path, help="Path to the measurement set.")
    parser.add_argument(
        "gleam_path", type=Path, help="Path to the GLEAM skymodel file."
    )
    parser.add_argument(
        "--fave-init", type=int, help="Initial frequency averaging on input.", default=4
    )
    parser.add_argument(
        "--freq-precal",
        type=int,
        help="Extra frequency averaging before calibration.",
        default=1,
    )
    parser.add_argument(
        "--centre-correct",
        action="store_true",
        help="Remove central beam response before calibration?",
    )
    parser.add_argument(
        "--refant",
        type=int,
        help="Reference antenna.",
        default=1,
    )
    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    ms_path = Path(args.ms_path)

    calibration_results = instrumental_calibration(
        dataset=ms_path,
        gleamfile=args.gleam_path,
        fave_init=args.fave_init,
        freq_precal=args.freq_precal,
        centre_correct=args.centre_correct,
    )

    gain_fig = plot_gains(
        vis=calibration_results.vis,
        gaintable=calibration_results.gaintable,
        metadata=calibration_results.metadata,
    )
    raw_fig, model_fig, cal_fig = plot_vis(
        vis=calibration_results.vis,
        calvis=calibration_results.calvis,
        mdlvis=calibration_results.mdlvis,
        metadata=calibration_results.metadata,
        jones_eb=calibration_results.jones_eb,
        centre_correct=args.centre_correct,
    )

    for fig, stem in zip(
        (gain_fig, raw_fig, model_fig, cal_fig),
        ("gain", "raw_vis", "model_vis", "cal_vis"),
        strict=True,
    ):
        out_path = ms_path.parent / f"{stem}_{ms_path.stem}.png"
        fig.savefig(out_path, bbox_inches="tight", dpi=300)


if __name__ == "__main__":
    main()
