# grid_cortex_client/src/grid_cortex_client/models/metric3d.py
"""Metric3D wrapper.

Monocular depth estimation powered by Metric3D.

Takes RGB image + encoder type and returns metric depth map.
"""

from __future__ import annotations

from typing import Any, Dict, Union

import numpy as np
from PIL import Image

from ..preprocessing import load_image, encode_image_to_base64
from ..postprocessing import postprocess_depth_response
from ..types import ImageRGB  # type: ignore
from .base_model import BaseModel


class Metric3D(BaseModel):
    """Monocular depth estimation (Metric3D).

    Preferred usage
    ---------------
    ```pycon
    >>> depth = CortexClient().run("metric3d", image_input=img, encoder="vit_large")
    >>> depth.shape
    (480, 640)
    ```
    """

    name: str = "metric3d"
    model_id: str = "metric3d"

    # ------------------------------------------------------------------
    # BaseModel implementation
    # ------------------------------------------------------------------

    def preprocess(
        self,
        *,
        image_input: Union[str, ImageRGB, np.ndarray],
        encoder: str = "vit_large",
    ) -> Dict[str, Any]:
        """Prepare JSON payload for Metric3D.

        Args:
            image_input: Image (path/URL/PIL/ndarray).
            encoder: Encoder type ("vit_large", "vit_base", etc.).
        """
        pil: Image.Image = load_image(image_input)
        encoded = encode_image_to_base64(pil)
        return {
            "image_input": encoded,
            "encoder": encoder,
        }

    def postprocess(self, response_data: Dict[str, Any], **_: Any) -> np.ndarray:  # noqa: D401
        """Decode base-64 .npy depth to np.ndarray."""
        return postprocess_depth_response(response_data).astype(np.float32)

    def run(
        self,
        image_input: Union[str, ImageRGB, np.ndarray],
        encoder: str = "vit_large",
        timeout: float | None = None,
    ) -> np.ndarray:
        """Estimate depth from single RGB image using Metric3D.

        Args:
            image_input (Union[str, ImageRGB, np.ndarray]): RGB image.
            encoder (str): Encoder type ("vit_large", "vit_base", etc.).
            timeout (float | None): Optional HTTP timeout.

        Returns:
            np.ndarray: Depth map as numpy array (H, W) with dtype float32.
            Values represent metric depth in meters.

        Raises:
            ValueError: If image cannot be loaded.
            RuntimeError: If no HTTP transport is configured.
            Exception: If the HTTP request fails.

        Examples:
            >>> from grid_cortex_client import CortexClient, ModelType
            >>> import numpy as np
            >>> from PIL import Image
            >>> client = CortexClient()
            >>> image = np.array(Image.open("cat.jpg"))
            >>> depth = client.run(ModelType.METRIC3D, image_input=image, encoder="vit_large")
            >>> print(depth.shape)  # (480, 640)
        """
        return super().run(
            image_input=image_input,
            encoder=encoder,
            timeout=timeout,
        )
