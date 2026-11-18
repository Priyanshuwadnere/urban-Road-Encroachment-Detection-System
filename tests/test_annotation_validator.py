"""
Unit tests for YOLO Instance Segmentation Annotation Infrastructure & Quality Control (Phase 3B).
"""

import os
import yaml
import pytest
from src.config import PHYSICAL_CLASSES
from src.ml.annotation_validator import AnnotationValidator
from src.ml.annotation_stats import compute_dataset_annotation_statistics


def test_dataset_yaml_configuration():
    yaml_path = "dataset/dataset.yaml"
    assert os.path.exists(yaml_path)

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["train"] == "images/train"
    assert data["val"] == "images/val"
    assert data["test"] == "images/test"

    names = data["names"]
    assert len(names) == 8
    for cid in range(8):
        assert names[cid] == PHYSICAL_CLASSES[cid]

    # CRITICAL: Rejects class 8 or 'encroachment'
    assert 8 not in names
    assert "encroachment" not in names.values()


def test_valid_yolo_label_syntax(tmp_path):
    lbl_file = str(tmp_path / "R001_SEQ01_FRAME001.txt")
    # Valid polygon for class 2: shop_extension
    with open(lbl_file, "w") as f:
        f.write("2 0.1 0.2 0.3 0.2 0.3 0.4 0.1 0.4\n")

    is_valid, errors, polys = AnnotationValidator.validate_label_file(lbl_file)
    assert is_valid is True
    assert len(errors) == 0
    assert len(polys) == 1
    assert polys[0]["class_id"] == 2
    assert polys[0]["class_name"] == "shop_extension"


def test_invalid_class_id_rejection(tmp_path):
    lbl_file = str(tmp_path / "invalid_class.txt")
    # Class 8 is prohibited (no 'encroachment' class allowed)
    with open(lbl_file, "w") as f:
        f.write("8 0.1 0.2 0.3 0.2 0.3 0.4\n")

    is_valid, errors, polys = AnnotationValidator.validate_label_file(lbl_file)
    assert is_valid is False
    assert any("Allowed classes are 0 to 7 ONLY" in err for err in errors)


def test_out_of_bounds_coordinate_rejection(tmp_path):
    lbl_file = str(tmp_path / "out_of_bounds.txt")
    # Coordinate 1.5 is > 1.0 (invalid unnormalized value)
    with open(lbl_file, "w") as f:
        f.write("0 0.1 0.2 1.5 0.2 0.3 0.4\n")

    is_valid, errors, polys = AnnotationValidator.validate_label_file(lbl_file)
    assert is_valid is False
    assert any("normalized bounds" in err for err in errors)


def test_insufficient_vertex_count_rejection(tmp_path):
    lbl_file = str(tmp_path / "insufficient_pts.txt")
    # Only 2 points (4 coordinates) -> invalid polygon
    with open(lbl_file, "w") as f:
        f.write("0 0.1 0.2 0.3 0.4\n")

    is_valid, errors, polys = AnnotationValidator.validate_label_file(lbl_file)
    assert is_valid is False
    assert any("Insufficient values" in err for err in errors)


def test_dataset_annotation_statistics_phase3b():
    stats = compute_dataset_annotation_statistics("dataset")
    assert stats["total_images"] == 90
    assert stats["total_labels"] == 90
    assert stats["total_annotated_objects"] == 551
    assert stats["missing_label_files_count"] == 0
    assert stats["orphan_label_files_count"] == 0
    assert stats["corrupted_label_files_count"] == 0
