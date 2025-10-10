# grid_cortex_client/src/grid_cortex_client/models/sam2.py
"""Segment Anything v2 (SAM-2) wrapper.

Interactive/automatic segmentation powered by SAM-2.  The backend supports two
modes:

* ``image`` – automatic mask generation by points / boxes prompts
* ``video`` – (future) video mask propagation

This wrapper exposes the *image* mode documented by the Ray-Serve test script.
"""

from __future__ import annotations

import base64
import json
from typing import Any, Dict, List, Union

import numpy as np
from PIL import Image

from ..preprocessing import load_image, encode_image_to_base64
from ..types import ImageRGB  # type: ignore
from .base_model import BaseModel


class SAM2(BaseModel):
    """Interactive prompt-based segmentation (SAM-2).

    Preferred usage
    ---------------
    ```pycon
    >>> mask = CortexClient().run(
    ...     "sam2", image_input=img,
    ...     prompts=[[320, 240]], labels=[1], multimask_output=False
    ... )
    ```
    """

    name: str = "sam2"
    model_id: str = "sam2"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _encode_prompts(prompts: List[List[int]]) -> str:
        """Encode *prompts* (list of [x, y]) to base-64 JSON string."""
        return base64.b64encode(json.dumps(prompts).encode()).decode()

    # ------------------------------------------------------------------
    # BaseModel implementation
    # ------------------------------------------------------------------

    def preprocess(
        self,
        *,
        image_input: Union[str, ImageRGB, np.ndarray],
        prompts: List[List[int]],
        labels: List[int],
        multimask_output: bool = False,
        mode: str = "image",
    ) -> Dict[str, Any]:
        """Return JSON payload for the SAM-2 endpoint."""
        pil: Image.Image = load_image(image_input)
        encoded_img = encode_image_to_base64(pil)
        return {
            "mode": mode,
            "image_input": encoded_img,
            "prompts": self._encode_prompts(prompts),
            "labels": labels,
            "multimask_output": multimask_output,
        }

    def postprocess(self, response_data: Dict[str, Any], **_: Any) -> Dict[str, Any]:  # noqa: D401
        """Return *response_data* unchanged – backend already returns JSON."""
        return response_data

    def run(
        self,
        image_input: Union[str, ImageRGB, np.ndarray],
        prompts: List[List[int]],
        labels: List[int],
        multimask_output: bool = False,
        mode: str = "image",
        timeout: float | None = None,
    ) -> Dict[str, Any]:
        """Segment image with SAM-2 given point/box prompts.

        Args:
            image_input (Union[str, ImageRGB, np.ndarray]): RGB image.
            prompts (List[List[int]]): List of ``[x, y]`` pixel coordinates.
            labels (List[int]): 1 = foreground, 0 = background per prompt.
            multimask_output (bool): If *True* returns multiple masks.
            mode (str): Endpoint mode; only "image" currently supported.
            timeout (float | None): HTTP timeout.

        Returns:
            Dict[str, Any]: Backend JSON containing encoded masks / scores.

        Examples:
            >>> from grid_cortex_client import CortexClient, ModelType
            >>> import numpy as np
            >>> from PIL import Image
            >>> client = CortexClient()
            >>> image = np.array(Image.open("cat.jpg"))
            >>> mask_json = client.run(
            ...     ModelType.SAM2,
            ...     image_input=image,
            ...     prompts=[[320, 240]],
            ...     labels=[1],
            ... )
        """
        return super().run(
            image_input=image_input,
            prompts=prompts,
            labels=labels,
            multimask_output=multimask_output,
            mode=mode,
            timeout=timeout,
        )
