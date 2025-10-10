__version__ = "1.0.0"
__release__ = "dev" # "dev" or "stable"

import re

ORIGINAL_PIXEL_SIZE = 0.325
ORIGINAL_UNIT = "µm"
TIFF_REGEX = re.compile(r"(.+)\.tiff?", re.IGNORECASE)