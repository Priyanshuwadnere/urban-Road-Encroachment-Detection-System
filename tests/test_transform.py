"""Unit tests for Coordinate Transformer matrix module."""

import pytest
import numpy as np
from src.gis.transform import CoordinateTransformer
from src.core.exceptions import TransformError


def test_default_affine_transform():
    # pixels_per_meter = 20.0 => scale = 0.05
    transformer = CoordinateTransformer(pixels_per_meter=20.0, origin_x=0.0, origin_y=0.0)

    pixels = [(400.0, 1000.0), (0.0, 0.0)]
    map_coords = transformer.pixel_to_map(pixels)

    assert map_coords[0] == pytest.approx((20.0, 50.0))
    assert map_coords[1] == pytest.approx((0.0, 0.0))


def test_inverse_transform_reversibility():
    matrix = [
        [0.05, 0.0, 10.0],
        [0.0, 0.05, 5.0],
        [0.0, 0.0, 1.0],
    ]
    transformer = CoordinateTransformer(matrix=matrix)

    original_pixels = [(100.0, 200.0), (50.0, 80.0), (0.0, 0.0)]
    map_coords = transformer.pixel_to_map(original_pixels)
    recovered_pixels = transformer.map_to_pixel(map_coords)

    for orig, rec in zip(original_pixels, recovered_pixels):
        assert rec[0] == pytest.approx(orig[0], abs=1e-5)
        assert rec[1] == pytest.approx(orig[1], abs=1e-5)


def test_singular_matrix_raises_error():
    singular_matrix = [
        [1.0, 2.0, 3.0],
        [2.0, 4.0, 6.0],  # Linear dependent row
        [0.0, 0.0, 1.0],
    ]
    with pytest.raises(TransformError, match="singular"):
        CoordinateTransformer(matrix=singular_matrix)


def test_json_serialization(tmp_path):
    json_file = str(tmp_path / "matrix.json")
    matrix = [
        [0.1, 0.0, 5.0],
        [0.0, 0.1, 10.0],
        [0.0, 0.0, 1.0],
    ]
    t1 = CoordinateTransformer(matrix=matrix)
    t1.save_to_json(json_file)

    t2 = CoordinateTransformer.load_from_json(json_file)
    assert np.allclose(t1.matrix, t2.matrix)
