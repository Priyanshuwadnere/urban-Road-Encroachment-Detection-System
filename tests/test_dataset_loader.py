"""Unit tests for dataset ingestion pipeline and storyboard reference registry."""

import pytest
from src.ml.dataset_loader import (
    DroneFrameMeta,
    parse_drone_frame_filename,
    load_storyboard_registry,
    validate_sequence_continuity,
)


def test_parse_drone_frame_filename_valid():
    meta1 = parse_drone_frame_filename("R001_SEQ01_FRAME001.jpg")
    assert meta1.road_id == "R001"
    assert meta1.sequence_id == "SEQ01"
    assert meta1.frame_index == 1
    assert meta1.chainage_m == 2.0

    meta30 = parse_drone_frame_filename("R001_SEQ01_FRAME030.jpg")
    assert meta30.frame_index == 30
    assert meta30.chainage_m == 60.0


def test_parse_drone_frame_filename_invalid_pattern():
    with pytest.raises(ValueError, match="canonical pattern"):
        parse_drone_frame_filename("invalid_frame_name.jpg")


def test_sequence_continuity_validation():
    frames = [
        parse_drone_frame_filename(f"R001_SEQ01_FRAME{i:03d}.jpg")
        for i in range(1, 31)
    ]
    assert len(frames) == 30
    assert validate_sequence_continuity(frames) is True


def test_sequence_continuity_with_gap():
    frames = [
        parse_drone_frame_filename("R001_SEQ01_FRAME001.jpg"),
        parse_drone_frame_filename("R001_SEQ01_FRAME003.jpg"),  # Gap: frame 2 missing
    ]
    assert validate_sequence_continuity(frames) is False


def test_load_storyboard_registry():
    registry = load_storyboard_registry()
    assert registry["asset_type"] == "STORYBOARD_REFERENCE"
    assert len(registry["storyboard_sequences"]) == 3
    assert registry["usage_rules"]["is_ml_input"] is False
    assert registry["usage_rules"]["is_training_data"] is False
