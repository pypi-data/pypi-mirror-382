from __future__ import annotations

import logging

# Create logger
logging.captureWarnings(True)
logger = logging.getLogger("low_comm_tools")
logger.setLevel(logging.INFO)

# Create console handler and set level to debug
format_str = "%(levelname)s %(module)s - %(funcName)s: %(message)s"
formatter = logging.Formatter(format_str)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
