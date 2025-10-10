"""Preprocessing helpers.

Utility functions to load images from various sources and encode them as
base-64 strings suitable for JSON transport.
"""

import base64
import io
import logging
import os
from typing import Union, Any
import requests  # Add requests import

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_FORMATS = (".png", ".jpg", ".jpeg", ".bmp", ".tiff")


def load_image(image_input: Union[str, Image.Image, np.ndarray]) -> Image.Image:
    """Return a Pillow RGB image from multiple input types.

    Args:
        image_input: File path, URL, ``PIL.Image`` or NumPy array.

    Returns:
        Pillow image in RGB mode.
    """
    if isinstance(image_input, str):
        # Check if it's a URL
        if image_input.startswith(("http://", "https://")):
            try:
                logger.debug(f"Fetching image from URL: {image_input}")
                response = requests.get(image_input, timeout=10)
                response.raise_for_status()  # Raise an exception for bad status codes
                img_bytes = io.BytesIO(response.content)
                return Image.open(img_bytes).convert("RGB")
            except requests.exceptions.RequestException as e:
                raise IOError(
                    f"Failed to fetch image from URL {image_input}: {e}"
                ) from e
            except Exception as e:
                raise IOError(
                    f"Failed to load image from URL {image_input} after fetching: {e}"
                ) from e
        # Otherwise, assume it's a local file path
        elif not os.path.exists(image_input):
            raise FileNotFoundError(f"Image path does not exist: {image_input}")
        if not image_input.lower().endswith(SUPPORTED_IMAGE_FORMATS):
            raise ValueError(
                f"Unsupported image format: {image_input}. Supported: {SUPPORTED_IMAGE_FORMATS}"
            )
        try:
            return Image.open(image_input).convert("RGB")
        except Exception as e:
            raise IOError(f"Failed to load image from path {image_input}: {e}") from e
    elif isinstance(image_input, Image.Image):
        return image_input.convert("RGB")
    elif isinstance(image_input, np.ndarray):
        try:
            return Image.fromarray(image_input).convert("RGB")
        except Exception as e:
            raise ValueError(f"Failed to convert numpy array to PIL Image: {e}") from e
    raise TypeError(
        f"Unsupported image input type: {type(image_input)}. Supported: str, PIL.Image, np.ndarray."
    )


def encode_image_to_base64(image: Image.Image, encoding_format: str = "JPEG") -> str:
    """Encode *image* as base-64 text suitable for JSON payloads.

    Args:
        image: Pillow image to encode.
        encoding_format: Image format passed to :py:meth:`PIL.Image.Image.save`.

    Returns:
        Base-64 encoded string (UTF-8).
    """
    if not isinstance(image, Image.Image):
        raise TypeError("Input must be a PIL Image object.")

    buffered = io.BytesIO()
    image.save(buffered, format=encoding_format)
    encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

    logger.debug(f"Encoded image to base64 with format {encoding_format}")
    return encoded_image


# ---------------------------------------------------------------------------
# Array helpers
# ---------------------------------------------------------------------------


def encode_array_to_base64(array: np.ndarray) -> str:
    """Encode a NumPy array as a base-64 string.

    The array is serialized with :pyfunc:`numpy.save` (``.npy`` format) and then
    base-64 encoded so that it can be safely transported inside a JSON payload.

    Parameters
    ----------
    array:
        N-dimensional NumPy array.

    Returns
    -------
    str
        UTF-8 base-64 text representing the ``.npy`` bytes.
    """

    from io import BytesIO
    import base64 as _b64

    if not isinstance(array, np.ndarray):
        raise TypeError("array must be a NumPy ndarray")

    buf = BytesIO()
    np.save(buf, array, allow_pickle=False)
    return _b64.b64encode(buf.getvalue()).decode("utf-8")


# ---------------------------------------------------------------------------
# Recursive encoding helper
# ---------------------------------------------------------------------------


def _encode_nested(element: Any) -> Any:  # noqa: D401 internal helper
    """Recursively encode NumPy arrays inside *element* to base-64.

    Supports nested dictionaries and lists/tuples.  Other types are returned
    unchanged.
    """

    if isinstance(element, np.ndarray):
        return encode_array_to_base64(element)
    elif isinstance(element, dict):
        return {k: _encode_nested(v) for k, v in element.items()}
    elif isinstance(element, (list, tuple)):
        return [_encode_nested(v) for v in element]
    else:
        return element


def encode_nested(data: Any) -> Any:  # noqa: D401 public helper
    """Encode arrays inside *data*.

    Simply calls :pyfunc:`_encode_nested` – exposed for reuse by wrappers.
    """

    return _encode_nested(data)
