"""
Unit tests for Phase 3C Annotation Audit & Visual Verification Engine.
"""

import os
import pytest
from src.config import PHYSICAL_CLASSES
from src.ml.annotation_auditor import AnnotationAuditor


def test_audit_dataset_execution():
    results = AnnotationAuditor.audit_dataset()

    assert results["total_images_audited"] == 90
    assert results["total_annotations_audited"] == 551

    status = results["status_counts"]
    assert status["VERIFIED"] + status["QUESTIONABLE"] + status["REQUIRES MANUAL REVIEW"] == 551

    assert results["class_confusion_cases"] == 0
    assert results["geometry_issues"] == 0
    assert results["missing_object_cases"] == 0
    assert results["false_object_cases"] == 0
    assert results["critical_issues"] == 0


def test_per_class_audit_breakdown():
    results = AnnotationAuditor.audit_dataset()
    per_class = results["per_class_audit"]

    assert len(per_class) == 8
    for cid in range(8):
        assert cid in per_class
        assert per_class[cid]["class_name"] == PHYSICAL_CLASSES[cid]
        assert per_class[cid]["total_count"] > 0

    assert 8 not in per_class


def test_honest_provenance_statement():
    results = AnnotationAuditor.audit_dataset()
    statement = results.get("honest_provenance_statement", "")
    assert "HONEST AUDIT STATEMENT" in statement
    assert "170x153" in statement or "resolution" in statement.lower()
    assert "manual review" in statement.lower()


def test_audit_previews_exist():
    audit_dir = "dataset/audit"
    assert os.path.exists(audit_dir)

    for split in ["train", "val", "test"]:
        split_dir = os.path.join(audit_dir, split)
        assert os.path.exists(split_dir)
        files = [f for f in os.listdir(split_dir) if f.endswith("_audit.jpg")]
        assert len(files) == 30
