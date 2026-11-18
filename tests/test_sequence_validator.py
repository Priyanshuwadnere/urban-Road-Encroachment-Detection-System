"""
Unit tests for Individual Drone Frame Ingestion & Validation Pipeline (Phase 2).
"""

import os
import pytest
from PIL import Image
from src.ml.dataset_loader import (
    FrameAssetType,
    ValidationStatus,
    IndividualFrameMetadata,
    load_storyboard_registry,
)
from src.ml.sequence_validator import IndividualFrameValidator, DatasetSequenceIngestor


@pytest.fixture
def sample_jpeg(tmp_path):
    """Generate a clean 100x100 RGB JPEG image."""
    img_path = str(tmp_path / "R001_SEQ01_FRAME001.jpg")
    img = Image.new("RGB", (100, 100), color=(200, 100, 50))
    img.save(img_path, format="JPEG")
    return img_path


@pytest.fixture
def corrupted_file(tmp_path):
    """Generate a 0-byte corrupted image file."""
    file_path = str(tmp_path / "R001_SEQ01_FRAME002.jpg")
    with open(file_path, "wb") as f:
        f.write(b"NOT_AN_IMAGE_FILE_DATA")
    return file_path


def test_valid_frame_validation(sample_jpeg):
    meta = IndividualFrameValidator.validate_frame_file(sample_jpeg)
    assert meta.validation_status == ValidationStatus.VALID
    assert meta.road_id == "R001"
    assert meta.sequence_id == "SEQ01"
    assert meta.frame_id == 1
    assert meta.chainage_m == 2.0
    assert meta.width == 100
    assert meta.height == 100
    assert meta.format == "JPEG"
    assert meta.sha256_hash is not None
    assert meta.asset_type == FrameAssetType.RAW_FRAME


def test_corrupted_frame_detection(corrupted_file):
    meta = IndividualFrameValidator.validate_frame_file(corrupted_file)
    assert meta.validation_status == ValidationStatus.CORRUPTED


def test_invalid_filename_detection(tmp_path):
    bad_name = str(tmp_path / "drone_photo_bad_name.jpg")
    with open(bad_name, "w") as f:
        f.write("dummy")

    meta = IndividualFrameValidator.validate_frame_file(bad_name)
    assert meta.validation_status == ValidationStatus.INVALID_FILENAME


def test_duplicate_frame_detection(tmp_path):
    seq_dir = tmp_path / "R001_SEQ01"
    seq_dir.mkdir()

    # Create two identical image files (same content -> same SHA256)
    img = Image.new("RGB", (64, 64), color=(10, 20, 30))
    f1 = str(seq_dir / "R001_SEQ01_FRAME001.jpg")
    f2 = str(seq_dir / "R001_SEQ01_FRAME002.jpg")
    img.save(f1, format="JPEG")
    img.save(f2, format="JPEG")

    ingestor = DatasetSequenceIngestor(raw_sequences_root=str(tmp_path))
    summary, frames = ingestor.scan_sequence_directory("R001", "SEQ01", expected_frames=2)

    assert summary.valid_frames_count == 1
    assert summary.duplicate_frame_ids == [2]


def test_missing_frame_detection(tmp_path):
    seq_dir = tmp_path / "R001_SEQ01"
    seq_dir.mkdir()

    # Create Frame 1 and Frame 3 (Frame 2 missing)
    img = Image.new("RGB", (64, 64), color=(50, 50, 50))
    img.save(str(seq_dir / "R001_SEQ01_FRAME001.jpg"), format="JPEG")
    # Change color slightly so hash differs
    img2 = Image.new("RGB", (64, 64), color=(60, 60, 60))
    img2.save(str(seq_dir / "R001_SEQ01_FRAME003.jpg"), format="JPEG")

    ingestor = DatasetSequenceIngestor(raw_sequences_root=str(tmp_path))
    summary, frames = ingestor.scan_sequence_directory("R001", "SEQ01", expected_frames=3)

    assert summary.valid_frames_count == 2
    assert summary.missing_frame_ids == [2]


def test_sequence_level_splits(tmp_path):
    ingestor = DatasetSequenceIngestor(raw_sequences_root=str(tmp_path))
    manifest = ingestor.build_dataset_manifest(
        expected_sequences=[("R001", "SEQ01"), ("R001", "SEQ02"), ("R001", "SEQ03")],
        manifest_output_path=str(tmp_path / "manifest.json"),
    )

    splits = {s.sequence_id: s.assigned_split for s in manifest.sequence_splits}
    assert splits["SEQ01"] == FrameAssetType.TRAIN
    assert splits["SEQ02"] == FrameAssetType.VAL
    assert splits["SEQ03"] == FrameAssetType.TEST


def test_strict_storyboard_separation():
    registry = load_storyboard_registry()
    assert registry["asset_type"] == "STORYBOARD_REFERENCE"
    assert registry["usage_rules"]["is_ml_input"] is False
    assert registry["usage_rules"]["is_training_data"] is False
