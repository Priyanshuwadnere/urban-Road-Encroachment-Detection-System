"""
YOLO Instance Segmentation Annotation Quality Control & Validator.
Performs comprehensive checks on label files:
  - Class ID validation (0 to 7 ONLY)
  - Normalized coordinate bounds [0.0, 1.0]
  - Minimum polygon vertex count (>= 3 points)
  - Degenerate / zero-area polygon detection
  - Duplicate polygon detection
  - Missing label & orphan label detection
"""

import os
import sys
from typing import List, Dict, Any, Tuple, Optional
from shapely.geometry import Polygon

sys.path.insert(0, os.path.abspath("."))
from src.config import PHYSICAL_CLASSES, ACADEMIC_DISCLAIMER


class AnnotationValidator:
    """Validator for YOLO Segmentation label files (.txt)."""

    @staticmethod
    def validate_label_file(
        label_path: str, image_path: Optional[str] = None
    ) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
        """
        Validate single YOLO segmentation label file.
        Format per line: <class_id> <x1> <y1> <x2> <y2> ... <xn> <yn>
        Returns: (is_valid, error_list, parsed_polygons)
        """
        errors = []
        parsed_polygons = []

        if not os.path.exists(label_path):
            errors.append(f"Label file not found: {label_path}")
            return False, errors, parsed_polygons

        # Empty label file (valid for images with no physical target objects)
        if os.path.getsize(label_path) == 0:
            return True, [], parsed_polygons

        seen_polygon_hashes = set()

        with open(label_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            parts = line_str.split()
            if len(parts) < 7:  # class_id + 3 coordinate pairs (x1, y1, x2, y2, x3, y3)
                errors.append(
                    f"Line {line_num}: Insufficient values ({len(parts)}). Minimum 7 expected (class_id + 3 (x,y) pairs)."
                )
                continue

            # 1. Class ID validation
            try:
                class_id = int(parts[0])
            except ValueError:
                errors.append(f"Line {line_num}: Non-integer class_id '{parts[0]}'.")
                continue

            if class_id not in PHYSICAL_CLASSES:
                errors.append(
                    f"Line {line_num}: Invalid class_id {class_id}. Allowed classes are 0 to 7 ONLY (NO encroachment class)."
                )
                continue

            # 2. Coordinate pair count validation
            coords_raw = parts[1:]
            if len(coords_raw) % 2 != 0:
                errors.append(
                    f"Line {line_num}: Odd number of coordinate values ({len(coords_raw)}). Must be paired (x, y)."
                )
                continue

            # 3. Coordinate bounds validation [0.0, 1.0]
            try:
                coords = [float(v) for v in coords_raw]
            except ValueError:
                errors.append(f"Line {line_num}: Non-float coordinate detected.")
                continue

            out_of_bounds = [v for v in coords if v < 0.0 or v > 1.0]
            if out_of_bounds:
                errors.append(
                    f"Line {line_num}: Coordinates out of normalized bounds [0.0, 1.0]: {out_of_bounds[:3]}"
                )
                continue

            # 4. Construct point pairs [(x1,y1), ...]
            pts = [(coords[i], coords[i + 1]) for i in range(0, len(coords), 2)]

            if len(pts) < 3:
                errors.append(f"Line {line_num}: Polygon has fewer than 3 unique vertices.")
                continue

            # 5. Duplicate polygon check
            poly_hash = tuple(round(c, 5) for c in coords)
            if poly_hash in seen_polygon_hashes:
                errors.append(f"Line {line_num}: Duplicate polygon detected in same label file.")
                continue
            seen_polygon_hashes.add(poly_hash)

            # 6. Polygon geometry validation with Shapely
            try:
                poly = Polygon(pts)
                if poly.is_empty or poly.area < 1e-7:
                    errors.append(f"Line {line_num}: Degenerate zero-area polygon.")
                    continue
            except Exception as e:
                errors.append(f"Line {line_num}: Invalid polygon geometry: {str(e)}")
                continue

            parsed_polygons.append(
                {
                    "class_id": class_id,
                    "class_name": PHYSICAL_CLASSES[class_id],
                    "vertices": pts,
                    "area_norm": poly.area,
                }
            )

        is_valid = len(errors) == 0
        return is_valid, errors, parsed_polygons

    @classmethod
    def validate_dataset_structure(
        cls, dataset_root: str = "dataset"
    ) -> Dict[str, Any]:
        """
        Validate complete YOLO dataset structure across train, val, and test splits.
        Checks missing label files, orphan label files, and content validity.
        """
        splits = ["train", "val", "test"]
        summary = {
            "total_images": 0,
            "total_labels": 0,
            "missing_label_files": [],
            "orphan_label_files": [],
            "corrupted_label_files": [],
            "total_annotated_polygons": 0,
            "class_distribution": {cid: 0 for cid in PHYSICAL_CLASSES.keys()},
            "disclaimer": ACADEMIC_DISCLAIMER,
        }

        for split in splits:
            img_dir = os.path.join(dataset_root, "images", split)
            lbl_dir = os.path.join(dataset_root, "labels", split)

            img_files = (
                {
                    os.path.splitext(f)[0]: os.path.join(img_dir, f)
                    for f in os.listdir(img_dir)
                    if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
                }
                if os.path.exists(img_dir)
                else {}
            )

            lbl_files = (
                {
                    os.path.splitext(f)[0]: os.path.join(lbl_dir, f)
                    for f in os.listdir(lbl_dir)
                    if f.lower().endswith(".txt")
                }
                if os.path.exists(lbl_dir)
                else {}
            )

            summary["total_images"] += len(img_files)
            summary["total_labels"] += len(lbl_files)

            # Check missing label files
            for base_name, img_path in img_files.items():
                if base_name not in lbl_files:
                    summary["missing_label_files"].append(img_path)
                else:
                    lbl_path = lbl_files[base_name]
                    is_valid, errors, polys = cls.validate_label_file(lbl_path, img_path)
                    if not is_valid:
                        summary["corrupted_label_files"].append({"file": lbl_path, "errors": errors})
                    else:
                        summary["total_annotated_polygons"] += len(polys)
                        for p in polys:
                            cid = p["class_id"]
                            summary["class_distribution"][cid] += 1

            # Check orphan label files
            for base_name, lbl_path in lbl_files.items():
                if base_name not in img_files:
                    summary["orphan_label_files"].append(lbl_path)

        return summary
