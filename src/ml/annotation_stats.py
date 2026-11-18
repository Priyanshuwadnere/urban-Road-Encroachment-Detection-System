"""
YOLO Annotation Statistics Utility.
Calculates dataset annotation metrics, class distribution, split breakdown,
and verifies zero fabrication (ANNOTATED OBJECTS = 0 when unannotated).
"""

import os
import sys
from typing import Dict, Any

sys.path.insert(0, os.path.abspath("."))
from src.config import PHYSICAL_CLASSES, ACADEMIC_DISCLAIMER
from src.ml.annotation_validator import AnnotationValidator


def compute_dataset_annotation_statistics(dataset_root: str = "dataset") -> Dict[str, Any]:
    """
    Compute dataset annotation metrics across train, val, and test splits.
    Returns dictionary with class counts, split breakdown, and total objects.
    """
    summary = AnnotationValidator.validate_dataset_structure(dataset_root)

    total_annotated = summary["total_annotated_polygons"]
    class_dist = summary["class_distribution"]

    split_counts = {"train": 0, "val": 0, "test": 0}
    for split in ["train", "val", "test"]:
        img_dir = os.path.join(dataset_root, "images", split)
        if os.path.exists(img_dir):
            split_counts[split] = len([f for f in os.listdir(img_dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))])

    stats = {
        "total_images": summary["total_images"],
        "total_labels": summary["total_labels"],
        "total_annotated_objects": total_annotated,
        "split_image_counts": split_counts,
        "class_distribution": {
            PHYSICAL_CLASSES[cid]: class_dist[cid] for cid in sorted(class_dist.keys())
        },
        "missing_label_files_count": len(summary["missing_label_files"]),
        "orphan_label_files_count": len(summary["orphan_label_files"]),
        "corrupted_label_files_count": len(summary["corrupted_label_files"]),
        "disclaimer": ACADEMIC_DISCLAIMER,
    }

    return stats


def print_annotation_statistics_report(dataset_root: str = "dataset") -> None:
    """Print human-readable annotation statistics report."""
    stats = compute_dataset_annotation_statistics(dataset_root)

    print("=" * 80)
    print("PHASE 3A — YOLO ANNOTATION DATASET STATISTICS REPORT")
    print("=" * 80)
    print(f"Total Images Ingested: {stats['total_images']} (Train: {stats['split_image_counts']['train']}, Val: {stats['split_image_counts']['val']}, Test: {stats['split_image_counts']['test']})")
    print(f"Total Label Files: {stats['total_labels']}")
    print(f"TOTAL ANNOTATED OBJECTS: {stats['total_annotated_objects']}")
    print("-" * 80)
    print("Class Distribution (Physical Classes 0 to 7):")
    for class_name, count in stats["class_distribution"].items():
        print(f"  - {class_name}: {count} polygons")
    print("-" * 80)
    print(f"Missing Label Files: {stats['missing_label_files_count']}")
    print(f"Orphan Label Files: {stats['orphan_label_files_count']}")
    print(f"Corrupted Label Files: {stats['corrupted_label_files_count']}")
    print(f"Disclaimer: {stats['disclaimer']}")
    print("=" * 80)


if __name__ == "__main__":
    print_annotation_statistics_report()
