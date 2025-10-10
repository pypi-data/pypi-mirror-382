from __future__ import annotations

import argparse
from pathlib import Path

from low_comm_tools.ms_utils import rename_telescope


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rename TELESCOPE_NAME in MeasurementSet",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("ms_path", help="Path to target MeasurementSet", type=Path)
    parser.add_argument(
        "-n", "--name", help="Set telescope name", type=str, default="SKA-LOW"
    )
    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    _ = rename_telescope(
        ms_path=args.ms_path,
        telescope_name=args.name,
    )


if __name__ == "__main__":
    main()
