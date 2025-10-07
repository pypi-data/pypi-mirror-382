from __future__ import annotations

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path

from low_comm_tools.ms_utils import get_field_name_from_ms


def get_parser(
    add_help: bool = True,
) -> ArgumentParser:
    parser = ArgumentParser(
        description="Get field name from a Measurement Set (MS).",
        formatter_class=ArgumentDefaultsHelpFormatter,
        add_help=add_help,
    )
    parser.add_argument(
        "ms_path",
        type=Path,
        help="Path to the Measurement Set (MS) directory.",
    )
    parser.add_argument(
        "--field-index",
        type=int,
        default=0,
        help="Index of the field to retrieve the name for.",
    )
    return parser


def main() -> None:
    args = get_parser().parse_args()

    field_name = get_field_name_from_ms(args.ms_path, field_index=args.field_index)
    print(field_name)  # noqa: T201


if __name__ == "__main__":
    main()
