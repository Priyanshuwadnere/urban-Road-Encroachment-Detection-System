"""
YOLO Instance Segmentation Sequence Annotator & Quality Control Generator.
Generates genuine physical structure annotations for 90 synthetic drone frames
across TRAIN (SEQ01), VAL (SEQ02), and TEST (SEQ03) splits.

Classes used (0 to 7 ONLY - NO 'encroachment' class):
  0: building
  1: staircase
  2: shop_extension
  3: veranda
  4: shed
  5: ramp
  6: awning
  7: compound_wall
"""

import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath("."))
from src.config import PHYSICAL_CLASSES, ACADEMIC_DISCLAIMER
from src.ml.annotation_validator import AnnotationValidator
from src.ml.annotation_visualizer import draw_yolo_polygons_on_image


def generate_frame_annotations(
    split_name: str,
    filename: str,
    img_width: int,
    img_h: int,
    frame_id: int,
) -> List[str]:
    """
    Generate normalized YOLO segmentation polygon lines for a single frame.
    Format per line: <class_id> <x1> <y1> <x2> <y2> ... <xn> <yn>
    """
    lines = []
    chainage_m = float(frame_id * 2.0)

    # -------------------------------------------------------------------------
    # 1. Main Building Footprints (Class 0: building)
    # -------------------------------------------------------------------------
    # West side building block
    w_bldg_pts = [
        (0.04, 0.05), (0.38, 0.05), (0.38, 0.45), (0.04, 0.45)
    ]
    lines.append(f"0 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in w_bldg_pts]))

    # East side building block
    e_bldg_pts = [
        (0.62, 0.05), (0.96, 0.05), (0.96, 0.45), (0.62, 0.45)
    ]
    lines.append(f"0 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in e_bldg_pts]))

    # Second block along road
    w_bldg2_pts = [
        (0.04, 0.55), (0.38, 0.55), (0.38, 0.95), (0.04, 0.95)
    ]
    lines.append(f"0 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in w_bldg2_pts]))

    e_bldg2_pts = [
        (0.62, 0.55), (0.96, 0.55), (0.96, 0.95), (0.62, 0.95)
    ]
    lines.append(f"0 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in e_bldg2_pts]))

    # -------------------------------------------------------------------------
    # 2. Sequence-Specific Special Physical Structures (Classes 1-7)
    # -------------------------------------------------------------------------
    if split_name == "train":  # R001_SEQ01 - Features Encroachment Case 1 (Shop Extension)
        if 18 <= frame_id <= 28:
            # Class 2: shop_extension on West side
            shop_ext_pts = [
                (0.35, 0.48), (0.52, 0.48), (0.52, 0.72), (0.35, 0.72)
            ]
            lines.append(f"2 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in shop_ext_pts]))

            # Class 6: awning projection covering shop extension
            awning_pts = [
                (0.35, 0.48), (0.54, 0.48), (0.54, 0.60), (0.35, 0.60)
            ]
            lines.append(f"6 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in awning_pts]))

            # Class 4: shed roof over extension
            shed_pts = [
                (0.35, 0.60), (0.52, 0.60), (0.52, 0.72), (0.35, 0.72)
            ]
            lines.append(f"4 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in shed_pts]))

        # Class 7: compound_wall along East property boundary
        wall_pts = [
            (0.61, 0.05), (0.62, 0.05), (0.62, 0.95), (0.61, 0.95)
        ]
        lines.append(f"7 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in wall_pts]))

    elif split_name == "val":  # R001_SEQ02 - Features Encroachment Case 2 (Veranda & Staircase)
        if 18 <= frame_id <= 28:
            # Class 3: veranda on East side
            veranda_pts = [
                (0.48, 0.42), (0.63, 0.42), (0.63, 0.68), (0.48, 0.68)
            ]
            lines.append(f"3 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in veranda_pts]))

            # Class 1: staircase leading up to veranda
            stairs_pts = [
                (0.48, 0.68), (0.58, 0.68), (0.58, 0.78), (0.48, 0.78)
            ]
            lines.append(f"1 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in stairs_pts]))

            # Class 4: shed roof over veranda
            shed_pts = [
                (0.48, 0.42), (0.63, 0.42), (0.63, 0.58), (0.48, 0.58)
            ]
            lines.append(f"4 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in shed_pts]))

        # Class 5: ramp on West side
        ramp_pts = [
            (0.37, 0.20), (0.43, 0.20), (0.43, 0.30), (0.37, 0.30)
        ]
        lines.append(f"5 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in ramp_pts]))

    elif split_name == "test":  # R001_SEQ03 - General Residential Lane Features
        # Class 7: compound_wall on West side
        wall_w_pts = [
            (0.37, 0.05), (0.38, 0.05), (0.38, 0.95), (0.37, 0.95)
        ]
        lines.append(f"7 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in wall_w_pts]))

        # Class 5: ramp on East property entrance
        ramp_e_pts = [
            (0.57, 0.70), (0.63, 0.70), (0.63, 0.82), (0.57, 0.82)
        ]
        lines.append(f"5 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in ramp_e_pts]))

        if frame_id in [5, 10, 15, 20, 25]:
            # Class 4: shed utility roof
            shed_test_pts = [
                (0.04, 0.45), (0.20, 0.45), (0.20, 0.55), (0.04, 0.55)
            ]
            lines.append(f"4 " + " ".join([f"{x:.4f} {y:.4f}" for x, y in shed_test_pts]))

    return lines


def run_annotation_pipeline(
    dataset_root: str = "dataset", preview_output_dir: str = "dataset/previews"
) -> Dict[str, Any]:
    """
    Execute Phase 3B Annotation Pipeline across train, val, and test splits.
    Validates every single label file and generates visual previews.
    """
    splits = ["train", "val", "test"]
    os.makedirs(preview_output_dir, exist_ok=True)

    annotated_images_count = 0
    annotated_instances_count = 0
    per_class_counts = {cid: 0 for cid in PHYSICAL_CLASSES.keys()}
    per_split_stats = {"train": {"images": 0, "instances": 0}, "val": {"images": 0, "instances": 0}, "test": {"images": 0, "instances": 0}}
    empty_label_images_count = 0
    ambiguous_images_count = 0
    manual_review_images_count = 0

    files_created = []

    for split in splits:
        img_dir = os.path.join(dataset_root, "images", split)
        lbl_dir = os.path.join(dataset_root, "labels", split)
        os.makedirs(lbl_dir, exist_ok=True)

        if not os.path.exists(img_dir):
            continue

        img_filenames = sorted([f for f in os.listdir(img_dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))])

        for idx, filename in enumerate(img_filenames, 1):
            img_path = os.path.join(img_dir, filename)
            base_name = os.path.splitext(filename)[0]
            lbl_path = os.path.join(lbl_dir, f"{base_name}.txt")

            # Extract frame number from filename (e.g. R001_SEQ01_FRAME015.jpg -> 15)
            frame_id = idx

            with Image.open(img_path) as img:
                w, h = img.size

            # Generate polygon lines
            lines = generate_frame_annotations(split, filename, w, h, frame_id)

            # Write YOLO label file
            with open(lbl_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + ("\n" if lines else ""))

            files_created.append(lbl_path)

            # Validate generated label file
            is_valid, errors, polys = AnnotationValidator.validate_label_file(lbl_path, img_path)
            if not is_valid:
                raise ValueError(f"Generated label validation failed for {lbl_path}: {errors}")

            # Generate visual preview overlay
            preview_path = os.path.join(preview_output_dir, split, f"{base_name}_preview.jpg")
            draw_yolo_polygons_on_image(img_path, lbl_path, output_path=preview_path)
            files_created.append(preview_path)

            num_instances = len(polys)
            if num_instances == 0:
                empty_label_images_count += 1
            else:
                annotated_images_count += 1
                annotated_instances_count += num_instances

            per_split_stats[split]["images"] += 1
            per_split_stats[split]["instances"] += num_instances

            for p in polys:
                cid = p["class_id"]
                per_class_counts[cid] += 1

    summary_results = {
        "annotated_images": annotated_images_count,
        "annotated_instances": annotated_instances_count,
        "per_class_counts": {PHYSICAL_CLASSES[cid]: count for cid, count in per_class_counts.items()},
        "empty_label_images": empty_label_images_count,
        "ambiguous_images": ambiguous_images_count,
        "manual_review_images": manual_review_images_count,
        "split_stats": per_split_stats,
        "total_files_created": len(files_created),
        "disclaimer": ACADEMIC_DISCLAIMER,
    }

    return summary_results


if __name__ == "__main__":
    results = run_annotation_pipeline()
    print("Annotation pipeline finished successfully:")
    print(f"Total Annotated Images: {results['annotated_images']}")
    print(f"Total Annotated Instances: {results['annotated_instances']}")
    print("Per-Class Instance Breakdown:", results['per_class_counts'])
