"""Post-processing helpers.

Convert raw JSON responses from model endpoints to convenient Python objects.
Only depth-map decoding remains; other model-specific logic now lives in their
respective wrapper files.
"""

from typing import Dict, Any
import numpy as np
import logging
import base64
import io

logger = logging.getLogger(__name__)


def postprocess_depth_response(response: Dict[str, Any]) -> np.ndarray:
    """Decode depth JSON into a NumPy array.

    Args:
        response: JSON dictionary from the `/zoedepth/run` endpoint. Must
            contain an ``"output"`` field that is a base-64 encoded Numpy file
            produced with :pyfunc:`numpy.save`.

    Returns:
        Two-dimensional ``np.ndarray`` with ``float32`` depth values.
    """
    logger.info("Attempting to postprocess depth estimation response into a PIL Image.")
    if not isinstance(response, dict) or "output" not in response:
        logger.error(
            f"Response is not a dict or missing 'output' key. Response: {type(response)}"
        )
        raise ValueError("Response missing 'output' key or is not a dictionary.")

    base64_encoded_numpy = response["output"]
    if not isinstance(base64_encoded_numpy, str):
        logger.error(
            f"'output' key should contain a base64 string, but found {type(base64_encoded_numpy)}."
        )
        raise ValueError(
            f"'output' key should contain a base64 string, but found {type(base64_encoded_numpy)}."
        )

    try:
        decoded_bytes = base64.b64decode(base64_encoded_numpy)
    except base64.binascii.Error as e:
        logger.error(
            f"Base64 decoding failed: {e}. Input (first 100 chars): '{base64_encoded_numpy[:100]}'"
        )
        raise ValueError(f"Base64 decoding failed: {e}") from e

    try:
        bytes_io = io.BytesIO(decoded_bytes)
        # The warning "UserWarning: The given NumPy array is not writeable..." is harmless here.
        # We are only reading from it.
        depth_array = np.load(
            bytes_io, allow_pickle=False
        )  # Added allow_pickle=False for security
    except Exception as e:  # Catching a broader range of np.load errors
        logger.error(
            f"Failed to load NumPy array from decoded_bytes. Error: {e}. Decoded bytes (first 100): {decoded_bytes[:100]}"
        )
        raise ValueError(
            f"Could not load NumPy array from decoded base64 string: {e}"
        ) from e

    if not isinstance(depth_array, np.ndarray):
        logger.error(f"Loaded data is not a NumPy array. Type: {type(depth_array)}")
        raise ValueError(f"Loaded data is not a NumPy array. Type: {type(depth_array)}")

    return depth_array


def postprocess_generic_json_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Return *response* unchanged.

    This helper is retained for backward compatibility.
    """
    logger.info("Postprocessing generic JSON response.")
    return response
