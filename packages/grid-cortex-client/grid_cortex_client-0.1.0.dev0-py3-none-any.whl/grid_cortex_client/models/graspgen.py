# grid_cortex_client/src/grid_cortex_client/models/graspgen.py
"""GraspGen wrapper.

Grasp generation from depth + segmentation + camera intrinsics.

Takes depth image, segmentation mask, camera intrinsics, and auxiliary
arguments to generate grasp poses and confidence scores.
"""

from __future__ import annotations

from typing import Any, Dict, Union

import numpy as np
from PIL import Image

from ..preprocessing import load_image, encode_array_to_base64
from ..types import ImageRGB  # type: ignore
from .base_model import BaseModel


class GraspGen(BaseModel):
    """Grasp generation from depth + segmentation (GraspGen).

    Preferred usage
    ---------------
    ```pycon
    >>> grasps, conf = CortexClient().run(
    ...     "graspgen",
    ...     depth_image=depth, seg_image=seg,
    ...     camera_intrinsics=K, aux_args=aux
    ... )
    ```
    """

    name: str = "graspgen"
    model_id: str = "graspgen"

    # ------------------------------------------------------------------
    # BaseModel implementation
    # ------------------------------------------------------------------

    def preprocess(
        self,
        *,
        depth_image: Union[str, ImageRGB, np.ndarray],
        seg_image: Union[str, ImageRGB, np.ndarray],
        camera_intrinsics: Union[str, np.ndarray],
        aux_args: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare JSON payload for GraspGen.

        Args:
            depth_image: Depth image (path/URL/PIL/ndarray).
            seg_image: Segmentation mask (path/URL/PIL/ndarray).
            camera_intrinsics: 3x3 camera intrinsics matrix.
            aux_args: Dict with "num_grasps", "gripper_config", "camera_extrinsics".
        """
        # Load and encode images
        if isinstance(depth_image, (str, Image.Image)):
            depth_pil = load_image(depth_image)
            depth_array = np.array(depth_pil)
        else:
            depth_array = np.asarray(depth_image)

        if isinstance(seg_image, (str, Image.Image)):
            seg_pil = load_image(seg_image)
            seg_array = np.array(seg_pil)
        else:
            seg_array = np.asarray(seg_image)

        # Load intrinsics
        if isinstance(camera_intrinsics, str):
            intrinsics = np.load(camera_intrinsics)
        else:
            intrinsics = np.asarray(camera_intrinsics)

        # Encode arrays
        depth_b64 = encode_array_to_base64(depth_array)
        seg_b64 = encode_array_to_base64(seg_array)
        intrinsics_b64 = encode_array_to_base64(intrinsics)

        # Encode aux_args as base64-encoded npz (matching server implementation)
        import base64
        import io

        # Convert aux_args to numpy arrays (server expects dict of arrays)
        aux_arrays = {}
        for key, value in aux_args.items():
            if isinstance(value, str):
                # Convert string to numpy array (server will call .item() on it)
                aux_arrays[key] = np.array(value)
            elif isinstance(value, (int, float)):
                # Convert scalar to numpy array
                aux_arrays[key] = np.array(value)
            elif isinstance(value, np.ndarray):
                # Keep as is
                aux_arrays[key] = value
            else:
                # Convert other types to numpy array
                aux_arrays[key] = np.array(value)

        # Save as npz with allow_pickle=True to handle mixed types
        aux_buf = io.BytesIO()
        np.savez(aux_buf, **aux_arrays)
        aux_b64 = base64.b64encode(aux_buf.getvalue()).decode("utf-8")

        return {
            "depth_image": depth_b64,
            "seg_image": seg_b64,
            "camera_intrinsics": intrinsics_b64,
            "aux_args": aux_b64,
        }

    def postprocess(
        self, response_data: Dict[str, Any], **_: Any
    ) -> tuple[np.ndarray, np.ndarray]:  # noqa: D401
        """Decode grasps and confidence from response."""
        grasps = np.array(response_data["output"])
        conf = np.array(response_data["confidence"])
        return grasps, conf

    def run(
        self,
        depth_image: Union[str, ImageRGB, np.ndarray],
        seg_image: Union[str, ImageRGB, np.ndarray],
        camera_intrinsics: Union[str, np.ndarray],
        aux_args: Dict[str, Any],
        timeout: float | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Generate grasps from depth + segmentation using GraspGen.

        Args:
            depth_image (Union[str, ImageRGB, np.ndarray]): Depth image.
            seg_image (Union[str, ImageRGB, np.ndarray]): Segmentation mask.
            camera_intrinsics (Union[str, np.ndarray]): 3x3 camera intrinsics matrix.
            aux_args (Dict[str, Any]): Auxiliary parameters:
                - "num_grasps": Number of grasps to generate
                - "gripper_config": Gripper configuration string
                - "camera_extrinsics": 4x4 camera extrinsics matrix
            timeout (float | None): Optional HTTP timeout.

        Returns:
            tuple[np.ndarray, np.ndarray]: Tuple of (grasps, confidence):
                - grasps: Array of 4x4 grasp poses (N, 4, 4)
                - confidence: Array of confidence scores (N,)

        Raises:
            ValueError: If images cannot be loaded or parameters are invalid.
            RuntimeError: If no HTTP transport is configured.
            Exception: If the HTTP request fails.

        Examples:
            >>> from grid_cortex_client import CortexClient, ModelType
            >>> import numpy as np
            >>> from PIL import Image
            >>> client = CortexClient()
            >>> K = np.eye(3)
            >>> aux = {"num_grasps": 128, "gripper_config": "single_suction_cup_30mm", "camera_extrinsics": np.eye(4)}
            >>> depth_image = np.load("depth.npy")
            >>> seg_image = np.array(Image.open("seg.png"))
            >>> grasps, conf = client.run(ModelType.GRASPGEN, depth_image=depth_image, seg_image=seg_image, camera_intrinsics=K, aux_args=aux)
            >>> print(f"Generated {len(grasps)} grasps")
        """
        return super().run(
            depth_image=depth_image,
            seg_image=seg_image,
            camera_intrinsics=camera_intrinsics,
            aux_args=aux_args,
            timeout=timeout,
        )
