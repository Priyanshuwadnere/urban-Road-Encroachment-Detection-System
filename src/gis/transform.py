"""
Coordinate Transformation Engine.
Maps 2D pixel coordinates (u, v) from drone image space to metric map space (X, Y)
using an Affine transformation or 3x3 Homography Matrix.
"""

import json
from typing import List, Tuple, Union, Optional
import numpy as np
from src.core.exceptions import TransformError


class CoordinateTransformer:
    """
    Handles forward (Pixel -> Map) and inverse (Map -> Pixel) coordinate transformations.
    Supports 2D Affine (scale, rotate, translate) and 3x3 Homography matrices.
    """

    def __init__(
        self,
        matrix: Optional[Union[List[List[float]], np.ndarray]] = None,
        pixels_per_meter: float = 20.0,
        origin_x: float = 0.0,
        origin_y: float = 0.0,
    ):
        """
        Initialize transformer with a 3x3 matrix or scale/offset defaults.
        """
        if matrix is not None:
            self.matrix = np.array(matrix, dtype=np.float64)
            if self.matrix.shape != (3, 3):
                raise TransformError(f"Transformation matrix must be shape (3, 3), got {self.matrix.shape}")
        else:
            # Default simple scaling & translation matrix:
            # X = origin_x + u / scale
            # Y = origin_y + v / scale
            scale = 1.0 / pixels_per_meter
            self.matrix = np.array(
                [
                    [scale, 0.0, origin_x],
                    [0.0, scale, origin_y],
                    [0.0, 0.0, 1.0],
                ],
                dtype=np.float64,
            )

        try:
            self.inv_matrix = np.linalg.inv(self.matrix)
        except np.linalg.LinAlgError as e:
            raise TransformError(f"Transformation matrix is singular and non-invertible: {e}")

    def pixel_to_map(self, pixel_coords: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Convert a list of pixel coordinates [(u, v), ...] to map metric coordinates [(X, Y), ...].
        """
        if not pixel_coords:
            return []

        pts = np.array(pixel_coords, dtype=np.float64)
        if pts.ndim != 2 or pts.shape[1] != 2:
            raise TransformError("pixel_coords must be a list of (u, v) tuples.")

        # Homogeneous coordinates [u, v, 1]^T
        ones = np.ones((pts.shape[0], 1), dtype=np.float64)
        pts_h = np.hstack([pts, ones])  # (N, 3)

        # Transform: (3, 3) @ (3, N) -> (3, N) -> transpose to (N, 3)
        transformed_h = (self.matrix @ pts_h.T).T

        # Normalize by scale factor w (third element)
        w = transformed_h[:, 2:3]
        if np.any(np.abs(w) < 1e-9):
            raise TransformError("Transformation resulted in division by zero (w near 0).")

        map_pts = transformed_h[:, :2] / w
        return [(float(x), float(y)) for x, y in map_pts]

    def map_to_pixel(self, map_coords: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Convert a list of map metric coordinates [(X, Y), ...] to pixel coordinates [(u, v), ...].
        """
        if not map_coords:
            return []

        pts = np.array(map_coords, dtype=np.float64)
        if pts.ndim != 2 or pts.shape[1] != 2:
            raise TransformError("map_coords must be a list of (X, Y) tuples.")

        ones = np.ones((pts.shape[0], 1), dtype=np.float64)
        pts_h = np.hstack([pts, ones])

        transformed_h = (self.inv_matrix @ pts_h.T).T
        w = transformed_h[:, 2:3]
        if np.any(np.abs(w) < 1e-9):
            raise TransformError("Inverse transformation resulted in division by zero.")

        pixel_pts = transformed_h[:, :2] / w
        return [(float(u), float(v)) for u, v in pixel_pts]

    def save_to_json(self, file_path: str) -> None:
        """Export matrix parameters to JSON file."""
        data = {"matrix": self.matrix.tolist()}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_json(cls, file_path: str) -> "CoordinateTransformer":
        """Import matrix parameters from JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "matrix" not in data:
            raise TransformError("Invalid JSON: 'matrix' key missing.")
        return cls(matrix=data["matrix"])

    @classmethod
    def create_uav_calibrated_transformer(
        cls,
        image_width: float = 1024.0,
        image_height: float = 723.0,
        gsd_m_per_px: float = 0.054545,
        road_centerline_px: float = 475.0,
        metric_centerline_x: float = 24.5,
        metric_datum_y: float = 40.0,
    ) -> "CoordinateTransformer":
        """
        Create a calibrated CoordinateTransformer mapping from image space (u, v)
        to metric map space (X, Y), preserving physical dimensions, orientation, and reversibility.
        """
        sx = gsd_m_per_px
        sy = gsd_m_per_px
        tx = metric_centerline_x - road_centerline_px * sx
        ty = metric_datum_y
        matrix = [
            [sx, 0.0, tx],
            [0.0, -sy, ty],
            [0.0, 0.0, 1.0],
        ]
        return cls(matrix=matrix)
