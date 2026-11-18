"""
Dataset Split & Directory Manager for Phase 3A Annotation Infrastructure.
Populates dataset/images/ and dataset/labels/ directory structures based on
sequence-level splits:
  SEQ01 -> train/ (30 images)
  SEQ02 -> val/   (30 images)
  SEQ03 -> test/  (30 images)
"""

import os
import shutil
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.abspath("."))
from src.config import ACADEMIC_DISCLAIMER


def setup_yolo_dataset_structure(
    raw_root: str = "dataset/raw_sequences",
    target_dataset_root: str = "dataset",
) -> Dict[str, int]:
    """
    Setup standard YOLO dataset directory hierarchy:
      dataset/images/{train,val,test}
      dataset/labels/{train,val,test}
    Copies/links sequence images to assigned splits while preserving sequence boundary.
    """
    splits_map = {
        "R001_SEQ01": "train",
        "R001_SEQ02": "val",
        "R001_SEQ03": "test",
    }

    counts = {"train": 0, "val": 0, "test": 0}

    for seq_dir_name, split_name in splits_map.items():
        img_target_dir = os.path.join(target_dataset_root, "images", split_name)
        lbl_target_dir = os.path.join(target_dataset_root, "labels", split_name)

        os.makedirs(img_target_dir, exist_ok=True)
        os.makedirs(lbl_target_dir, exist_ok=True)

        seq_src_dir = os.path.join(raw_root, seq_dir_name)
        if not os.path.exists(seq_src_dir):
            continue

        for filename in sorted(os.listdir(seq_src_dir)):
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                src_file = os.path.join(seq_src_dir, filename)
                dst_file = os.path.join(img_target_dir, filename)
                shutil.copy2(src_file, dst_file)
                counts[split_name] += 1

    return counts


if __name__ == "__main__":
    res = setup_yolo_dataset_structure()
    print("YOLO dataset structure initialized:", res)
