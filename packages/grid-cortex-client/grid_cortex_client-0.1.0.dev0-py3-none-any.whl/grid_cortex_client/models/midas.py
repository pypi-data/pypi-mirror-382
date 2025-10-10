# grid_cortex_client/src/grid_cortex_client/models/midas.py
"""MiDaS wrapper.

Monocular depth estimation powered by MiDaS.

This closely mirrors :pyclass:`ZoeDepth` but calls the ``/midas/run`` endpoint.
"""

from __future__ import annotations

from typing import Any, Dict, Union

import numpy as np
from PIL import Image

from ..preprocessing import load_image, encode_image_to_base64
from ..postprocessing import postprocess_depth_response
from ..types import ImageRGB  # type: ignore  # forward-declared in parent package
from .base_model import BaseModel


class Midas(BaseModel):
    """Monocular depth estimation (MiDaS).

    Preferred usage (through :class:`~grid_cortex_client.CortexClient`)
    ----------------------------------------------------------------
    ```pycon
    >>> depth = CortexClient().run("midas", image_input=img)
    >>> depth.shape
    (480, 640)
    ```

    Direct wrapper usage
    --------------------
    ```pycon
    >>> from grid_cortex_client.models.midas import Midas
    >>> wrapper = Midas(transport=client.http_client)
    >>> depth = wrapper.run(image_input=img)
    ```

    The API is identical to :pyclass:`ZoeDepth`.
    """

    name: str = "midas"
    model_id: str = "midas"

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    def __init__(self, *, transport=None):
        super().__init__(transport=transport)

    # ------------------------------------------------------------------
    # BaseModel implementation
    # ------------------------------------------------------------------

    def preprocess(
        self,
        *,
        image_input: Union[str, ImageRGB, np.ndarray],
    ) -> Dict[str, Any]:
        """Encode *image_input* into base-64 PNG suitable for MiDaS."""

        pil_img: Image.Image = load_image(image_input)
        encoded = encode_image_to_base64(pil_img, encoding_format="PNG")
        return {"image_input": encoded}

    def postprocess(self, response_data: Dict[str, Any], **_: Any) -> np.ndarray:  # noqa: D401
        """Decode base-64 ``.npy`` depth to ``np.ndarray``."""

        return postprocess_depth_response(response_data).astype(np.float32)

    def run(
        self,
        image_input: Union[str, ImageRGB, np.ndarray],
        timeout: float | None = None,
    ) -> np.ndarray:
        """Estimate depth from single RGB image.

        Args:
            image_input (Union[str, ImageRGB, np.ndarray]): RGB image as file path, URL, PIL Image, or numpy array.
            timeout (float | None): Optional timeout in seconds for the HTTP request.

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
            >>> depth = client.run(ModelType.MIDAS, image_input=image)
            >>> print(depth.shape)  # (480, 640)
        """

        return super().run(image_input=image_input, timeout=timeout)
