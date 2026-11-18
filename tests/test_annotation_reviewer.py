"""
Unit tests for Phase 3D Human Annotation Review Engine & Review Queue.
"""

import os
import json
import pytest
from src.config import PHYSICAL_CLASSES
from src.ml.annotation_reviewer import HumanReviewEngine, PriorityReviewQueue, ReviewStatus


def test_priority_queue_ordering():
    engine = HumanReviewEngine()
    queue = engine.build_review_queue()

    assert len(queue) == 551

    # Verify priority ranks: staircase (1) < shop_extension (2) < veranda (3) < awning (4) < compound_wall (5)
    first_item = queue[0]
    assert first_item.class_name == "staircase" or first_item.class_id in [1, 2, 3, 6, 7]

    ranks = [PriorityReviewQueue.get_priority_rank(r.class_id) for r in queue]
    assert ranks == sorted(ranks)  # Ensure strictly sorted by priority rank


def test_human_review_simulation_results():
    engine = HumanReviewEngine()
    report = engine.process_human_review_simulation()

    assert report["total_annotations_reviewed"] == 551
    assert report["approved_without_changes"] == 420
    assert report["corrected"] == 60
    assert report["rejected"] == 27
    assert report["uncertain"] == 44
    assert report["remaining_pending"] == 0

    assert os.path.exists("dataset/review_audit.json")


def test_low_resolution_suitability_assessment():
    engine = HumanReviewEngine()
    engine.build_review_queue()

    # Small structure records must be flagged resolution_suitable=False
    small_records = [r for r in engine.records if r.class_id in [1, 2, 3, 6]]
    assert len(small_records) == 44
    for r in small_records:
        assert r.resolution_suitable is False

    # Main building records must be flagged resolution_suitable=True
    bldg_records = [r for r in engine.records if r.class_id == 0]
    for r in bldg_records:
        assert r.resolution_suitable is True


def test_provenance_statement_presence():
    engine = HumanReviewEngine()
    report = engine.process_human_review_simulation()

    prov = report.get("provenance_statement", "")
    assert "SYNTHETIC / ACADEMIC PROTOTYPE" in prov
    assert "storyboard montages" in prov
