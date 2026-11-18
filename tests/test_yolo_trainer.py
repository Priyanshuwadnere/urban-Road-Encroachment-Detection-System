"""
Unit tests for Phase 4 YOLO Instance Segmentation Training & Evaluation Engine.
"""

import os
import yaml
import pytest
from src.ml.yolo_trainer import YoloSegmentationTrainer, YoloTrainingConfig
from src.ml.yolo_evaluator import YoloSegmentationEvaluator


def test_baseline_dataset_yaml_configuration():
    yaml_path = "dataset/baseline_dataset.yaml"
    assert os.path.exists(yaml_path)

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["train"] == "images/train"
    assert data["val"] == "images/val"
    assert data["test"] == "images/test"

    names = data["names"]
    assert 0 in names and names[0] == "building"
    assert 5 in names and names[5] == "ramp"
    assert 7 in names and names[7] == "compound_wall"

    # Must NOT contain 'encroachment' class or class 8
    assert 8 not in names
    assert "encroachment" not in names.values()


def test_experiment_b_sufficiency_assessment():
    trainer = YoloSegmentationTrainer()
    assessment = trainer.evaluate_8class_sufficiency()

    assert assessment["experiment"] == "EXPERIMENT B — 8-CLASS MODEL"
    assert assessment["is_sufficient"] is False
    assert "staircase" in assessment["zero_instance_classes"]
    assert "shop_extension" in assessment["zero_instance_classes"]
    assert "veranda" in assessment["zero_instance_classes"]
    assert "shed" in assessment["zero_instance_classes"]
    assert "awning" in assessment["zero_instance_classes"]


def test_reproducible_seed_setting():
    config = YoloTrainingConfig(seed=42)
    trainer = YoloSegmentationTrainer(config)
    trainer.set_reproducible_seed()
    assert config.seed == 42


def test_evaluator_test_sequence():
    evaluator = YoloSegmentationEvaluator(runs_root="runs/segmentation")
    report = evaluator.evaluate_test_sequence(
        weights_path="runs/segmentation/baseline/weights/best.pt",
        test_dataset_yaml="dataset/baseline_dataset.yaml",
        img_dir="dataset/images/test",
    )

    assert report["test_sequence_id"] == "R001_SEQ03"
    assert report["test_images_count"] == 30

    metrics = report["final_test_metrics"]
    assert metrics["precision"] > 0.0
    assert metrics["recall"] > 0.0
    assert metrics["f1_score"] > 0.0
    assert metrics["mAP_50"] > 0.0

    assert os.path.exists("runs/segmentation/predictions")
    assert report["prediction_renders_count"] > 0


def test_provenance_and_limitations():
    evaluator = YoloSegmentationEvaluator(runs_root="runs/segmentation")
    report = evaluator.evaluate_test_sequence(
        weights_path="runs/segmentation/baseline/weights/best.pt",
        test_dataset_yaml="dataset/baseline_dataset.yaml",
        img_dir="dataset/images/test",
    )

    assert "SYNTHETIC / ACADEMIC PROTOTYPE" in report["provenance_statement"]
    assert "170x153" in report["limitations"]
