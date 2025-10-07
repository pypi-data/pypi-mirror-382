from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Literal

import astropy.units as u
import numpy as np
from astropy.coordinates import EarthLocation

from low_comm_tools import data
from low_comm_tools.exceptions import UnitError

AAType = Literal["AA0.5", "AA1", "AA2", "AA*"]

# Set the location of SKA-Low
# This is the location of C1
SKA_LOW_LOCATION = EarthLocation(
    lat=-26.826161995090644 * u.deg,
    lon=116.7656960036497 * u.deg,
    height=347.0376321554915 * u.m,
)


def load_rotation(unit: Literal["deg", "rad"] = "rad") -> dict[str, float]:
    with resources.as_file(resources.files(data)) as data_path:
        angle_data_path = data_path / "ska_low_angles_degrees.json"
    rotation_data: dict[str, float] = json.loads(Path(angle_data_path).read_text())
    match unit:
        case "deg":
            return rotation_data
        case "rad":
            return {k: np.deg2rad(v) for k, v in rotation_data.items()}
        case _:
            msg = f"Unknown unit '{unit}'. Must be 'deg' or 'rad'"  # type: ignore[unreachable]
            raise UnitError(msg)
