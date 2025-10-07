from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import pandas as pd
from casacore.tables import table

from low_comm_tools.log_config import logger
from low_comm_tools.ms_utils import get_antenna_names_from_ms


def convert_caltable(
    cal_table: Path,
    ms_path: Path | None = None,
) -> Path:
    logger.info(f"Converting {cal_table} to text format")
    with table(cal_table.as_posix()) as tab:
        cal_params = np.squeeze(tab.getcol("FPARAM"))
        ant_1 = np.squeeze(tab.getcol("ANTENNA1"))

    delay_df = pd.DataFrame(cal_params, columns=["delay_0", "delay_1"])
    delay_df["antenna_1"] = ant_1

    if ms_path is not None:
        ant_names = get_antenna_names_from_ms(ms_path)
        ant_1_names = [ant_names[i] for i in ant_1]
        delay_df["antenna_1_name"] = ant_1_names

    out_path = cal_table.with_suffix(".csv")
    delay_df.to_csv(out_path, index=False)
    logger.info(f"Wrote {out_path}")
    return out_path


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Convert a CASA caltable to a text file")

    parser.add_argument("caltable", type=Path, help="Path to calibration table(s).")
    parser.add_argument(
        "--ms",
        type=Path,
        help="Path to the MS to get antenna names from.",
        default=None,
    )

    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    _ = convert_caltable(
        cal_table=args.caltable,
        ms_path=args.ms,
    )


if __name__ == "__main__":
    main()
