# grid_cortex_client/src/grid_cortex_client/models/foundation_stereo.py
"""FoundationStereo wrapper.

Stereo depth estimation powered by FoundationStereo.

Takes left/right stereo pair + camera intrinsics + baseline and returns
metric depth map.
"""

from __future__ import annotations

from typing import Any, Dict, Union

import numpy as np

from ..preprocessing import load_image, encode_image_to_base64, encode_nested
from ..postprocessing import postprocess_depth_response
from ..types import ImageRGB  # type: ignore
from .base_model import BaseModel


class FoundationStereo(BaseModel):
    """Stereo depth estimation (FoundationStereo).

    Preferred usage
    ---------------
    ```pycon
    >>> depth = CortexClient().run(
    ...     "foundationstereo",
    ...     left_image=left_img, right_image=right_img,
    ...     aux_args={"K": K, "baseline": 0.1, "hiera": 0, "valid_iters": 32}
    ... )
    ```
    """

    name: str = "foundationstereo"
    model_id: str = "foundationstereo"

    # ------------------------------------------------------------------
    # BaseModel implementation
    # ------------------------------------------------------------------

    def preprocess(
        self,
        *,
        left_image: Union[str, ImageRGB, np.ndarray],
        right_image: Union[str, ImageRGB, np.ndarray],
        aux_args: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare JSON payload for FoundationStereo.

        Args:
            left_image: Left stereo image.
            right_image: Right stereo image.
            aux_args: Dict with keys "K" (3x3 intrinsics), "baseline" (float),
                "hiera" (int), "valid_iters" (int).
        """
        left_pil = load_image(left_image)
        right_pil = load_image(right_image)

        left_b64 = encode_image_to_base64(left_pil)
        right_b64 = encode_image_to_base64(right_pil)

        # Encode nested arrays in aux_args
        aux_encoded = encode_nested(aux_args)

        return {
            "left_image": left_b64,
            "right_image": right_b64,
            "aux_args": aux_encoded,
        }

    def postprocess(self, response_data: Dict[str, Any], **_: Any) -> np.ndarray:  # noqa: D401
        """Decode base-64 .npy depth to np.ndarray."""
        return postprocess_depth_response(response_data).astype(np.float32)

    def run(
        self,
        left_image: Union[str, ImageRGB, np.ndarray],
        right_image: Union[str, ImageRGB, np.ndarray],
        aux_args: Dict[str, Any],
        timeout: float | None = None,
    ) -> np.ndarray:
        """Estimate depth from stereo pair using FoundationStereo.

        Args:
            left_image (Union[str, ImageRGB, np.ndarray]): Left stereo image.
            right_image (Union[str, ImageRGB, np.ndarray]): Right stereo image.
            aux_args (Dict[str, Any]): Camera parameters:
                - "K": 3x3 camera intrinsics matrix
                - "baseline": Stereo baseline in meters
                - "hiera": Hierarchy level (0-2)
                - "valid_iters": Number of valid iterations
            timeout (float | None): Optional HTTP timeout.

        Returns:
            np.ndarray: Depth map as numpy array (H, W) with dtype float32.
            Values represent metric depth in meters.

        Raises:
            ValueError: If images cannot be loaded or aux_args is invalid.
            RuntimeError: If no HTTP transport is configured.
            Exception: If the HTTP request fails.

        Examples:
            >>> from grid_cortex_client import CortexClient, ModelType
            >>> import numpy as np
            >>> from PIL import Image
            >>> client = CortexClient()
            >>> K = np.array([[525, 0, 320], [0, 525, 240], [0, 0, 1]], dtype=np.float32)
            >>> aux = {"K": K, "baseline": 0.1, "hiera": 0, "valid_iters": 32}
            >>> left_image = np.array(Image.open("left.jpg"))
            >>> right_image = np.array(Image.open("right.jpg"))
            >>> depth = client.run(ModelType.FOUNDATIONSTEREO, left_image=left_image, right_image=right_image, aux_args=aux)
            >>> print(depth.shape)  # (480, 640)
        """
        return super().run(
            left_image=left_image,
            right_image=right_image,
            aux_args=aux_args,
            timeout=timeout,
        )
