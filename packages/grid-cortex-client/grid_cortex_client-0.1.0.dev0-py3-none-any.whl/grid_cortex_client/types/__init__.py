"""Shared domain types.

This sub-package defines basic type aliases for common input types.
"""

from PIL import Image

# ---------------------------------------------------------------------------
# Basic primitive aliases
# ---------------------------------------------------------------------------

ImageRGB = Image.Image  # A three-channel RGB image loaded via Pillow.
