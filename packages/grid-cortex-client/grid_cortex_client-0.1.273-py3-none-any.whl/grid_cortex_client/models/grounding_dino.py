# grid_cortex_client/src/grid_cortex_client/models/grounding_dino.py
"""Grounding DINO wrapper.

Zero-shot phrase-grounding / object detection powered by Grounding DINO.

This mirrors the API of :pyclass:`OWLv2` but calls the ``/grounding-dino/run``
endpoint and supports both *box_threshold* and *text_threshold* parameters.
"""

from __future__ import annotations

from typing import Any, Dict, Union

import base64
import json

import numpy as np

from ..preprocessing import load_image, encode_image_to_base64
from ..types import ImageRGB  # type: ignore
from .base_model import BaseModel


class GroundingDINO(BaseModel):
    """Zero-shot object detection with natural-language prompts (Grounding DINO).

    Preferred usage
    ---------------
    ```pycon
    >>> dets = CortexClient().run("grounding-dino", image_input=img, prompt="person")
    >>> dets["scores"][:3]
    [0.87, 0.79, 0.55]
    ```

    Direct wrapper usage
    --------------------
    ```pycon
    >>> from grid_cortex_client.models.grounding_dino import GroundingDINO
    >>> dets = GroundingDINO(transport=client.http_client).run(image_input=img, prompt="person")
    ```

    Notes
    -----
    The backend returns a JSON payload with a base-64 encoded JSON string under
    key ``"output"``.  Decoding yields a mapping ``{"boxes": [...], "scores": [...],
    "labels": [...]}``.  All numeric values are standard Python *float*/*int*
    types so that the result is trivially convertible to NumPy / PyTorch.
    """

    name: str = "grounding-dino"
    model_id: str = "grounding-dino"

    # ------------------------------------------------------------------
    # BaseModel implementation
    # ------------------------------------------------------------------

    def preprocess(
        self,
        *,
        image_input: Union[str, ImageRGB, np.ndarray],
        prompt: str,
        box_threshold: float | None = None,
        text_threshold: float | None = None,
    ) -> Dict[str, Any]:
        """Return JSON payload for the Grounding DINO endpoint.

        Args:
            image_input: Image to analyse (path / URL / PIL / ndarray).
            prompt: Natural-language phrase whose instances should be detected.
            box_threshold: Filter boxes below this confidence (0-1).
            text_threshold: Filter detections whose text score is below this (0-1).
        """

        pil = load_image(image_input)
        encoded = encode_image_to_base64(pil)
        payload: Dict[str, Any] = {
            "image_input": encoded,
            "prompt": prompt,
        }
        if box_threshold is not None:
            payload["box_threshold"] = box_threshold
        if text_threshold is not None:
            payload["text_threshold"] = text_threshold
        return payload

    def postprocess(self, response_data: Dict[str, Any], **_: Any) -> Dict[str, Any]:  # noqa: D401
        """Decode backend response into plain Python lists.

        The backend returns ``{"output": <b64-json>}``, identical to OWLv2.
        """

        output_b64 = response_data.get("output")
        if not isinstance(output_b64, str):
            raise ValueError("'output' key missing or not str.")
        decoded_json = base64.b64decode(output_b64).decode("utf-8")
        data = json.loads(decoded_json)
        return {
            "boxes": data["boxes"],
            "scores": data["scores"],
            "labels": data.get("labels", []),
        }

    def run(
        self,
        image_input: Union[str, ImageRGB, np.ndarray],
        prompt: str,
        box_threshold: float | None = None,
        text_threshold: float | None = None,
        timeout: float | None = None,
    ) -> Dict[str, Any]:
        """Detect objects in image using text prompt.

        Args:
            image_input (Union[str, ImageRGB, np.ndarray]): RGB image as file path, URL, PIL Image, or numpy array.
            prompt (str): Text describing objects to detect.
            box_threshold (float | None): Optional confidence threshold (0-1).
            text_threshold (float | None): Optional text threshold (0-1).
            timeout (float | None): Optional timeout for the HTTP request.

        Returns:
            Dict[str, Any]: Dictionary with keys:
                - "boxes": List[[x1, y1, x2, y2]] bounding boxes.
                - "scores": List[float] detection confidences.
                - "labels": List[int] class indices (all zeros if class-agnostic).

        Raises:
            ValueError: If image cannot be loaded or prompt is empty.
            RuntimeError: If no HTTP transport is configured.
            Exception: If the HTTP request fails.

        Examples:
            >>> from grid_cortex_client import CortexClient, ModelType
            >>> import numpy as np
            >>> from PIL import Image
            >>> client = CortexClient()
            >>> image = np.array(Image.open("cat.jpg"))
            >>> dets = client.run(ModelType.GROUNDING_DINO, image_input=image, prompt="a person")
            >>> print(len(dets["boxes"]))
        """

        return super().run(
            image_input=image_input,
            prompt=prompt,
            box_threshold=box_threshold,
            text_threshold=text_threshold,
            timeout=timeout,
        )
