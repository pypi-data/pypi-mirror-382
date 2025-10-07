#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from shutil import copytree

from casacore.tables import table, taql

from low_comm_tools.log_config import logger


def _copy_subtable(
    ms_path: Path,
    subtable_path: Path,
    dry_run: bool = False,
) -> Path:
    subtable_dest_path = ms_path / subtable_path.name
    if subtable_dest_path.exists():
        logger.info(f"Subtable {subtable_dest_path} already exists, skipping copy.")
        return subtable_dest_path

    verb = "Would copy" if dry_run else "Copying"
    logger.info(f"{verb} {subtable_path} into {subtable_dest_path}")
    if dry_run:
        return subtable_dest_path

    copytree(subtable_path, subtable_dest_path)
    return subtable_dest_path


def _update_ms(
    ms_path: Path,
    subtable_path: Path,
    telescope_name: str | None = None,
    dry_run: bool = False,
) -> Path:
    if dry_run:
        logger.info(f"Would make {subtable_path.name} a subtable of {ms_path}")
        if telescope_name is not None:
            logger.info(
                f"Would set TELESCOPE_NAME={telescope_name} in {ms_path}::OBSERVATION"
            )
        return ms_path

    with table(str(ms_path), readonly=False, ack=False) as tab:
        with table(str(subtable_path), ack=False) as sub_tab:
            tab.putkeyword(subtable_path.name, sub_tab, makesubrecord=True)
        if telescope_name is not None:
            taql(f"UPDATE $tab::OBSERVATION SET TELESCOPE_NAME='{telescope_name}'")

    return ms_path


def addsubtable(
    msfile: str | Path,
    subtablefile: str | Path,
    telescope_name: str | None = None,
    dry_run: bool = False,
) -> Path:
    """Adds an existing table as a subtable to another table
    The subtable is copied into the MS if it is not a subdirectory already"""

    ms_path = Path(msfile)
    subtable_path = Path(subtablefile)

    subtable_path_in_ms = _copy_subtable(ms_path, subtable_path, dry_run=dry_run)
    updated_ms_path = _update_ms(
        ms_path, subtable_path_in_ms, telescope_name=telescope_name, dry_run=dry_run
    )

    logger.info("Done!")
    return updated_ms_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Copy an existing table (e.g. PHASED_ARRAY) to another table as a subtable"
    )
    parser.add_argument("ms", help="Path to target MeasurementSet", type=Path)
    parser.add_argument("subtable", help="Path to subtable to add", type=Path)
    parser.add_argument("-d", "--dry-run", help="Dry run", action="store_true")
    parser.add_argument(
        "-n", "--name", help="Set telescope name", type=str, default=None
    )

    args = parser.parse_args()

    _ = addsubtable(
        msfile=args.ms,
        subtablefile=args.subtable,
        dry_run=args.dry_run,
        telescope_name=args.name,
    )


if __name__ == "__main__":
    main()
