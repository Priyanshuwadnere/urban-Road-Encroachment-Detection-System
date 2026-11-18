"""
Storyboard Frame Extraction Engine.
Extracts the 30 individual drone frame tiles from each of the 3 storyboard reference montages
and saves them as canonical raw sequence files under dataset/raw_sequences/R001_SEQ01/,
R001_SEQ02/, and R001_SEQ03/.
"""

import os
import sys
import json
from typing import List, Dict, Any, Tuple
from PIL import Image

sys.path.insert(0, os.path.abspath("."))

from src.config import ACADEMIC_DISCLAIMER
from src.ml.dataset_loader import load_storyboard_registry


def extract_frames_from_storyboard(
    storyboard_path: str,
    output_dir: str,
    road_id: str,
    sequence_id: str,
    rows: int = 5,
    cols: int = 6,
    expected_frames: int = 30,
) -> List[str]:
    """
    Extract individual 5x6 grid frame tiles from a storyboard montage image.
    Saves canonical frame files: R001_SEQ01_FRAME001.jpg to R001_SEQ01_FRAME030.jpg.
    """
    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(storyboard_path):
        raise FileNotFoundError(f"Storyboard image not found: {storyboard_path}")

    img = Image.open(storyboard_path)
    img_w, img_h = img.size

    tile_w = img_w / cols
    tile_h = img_h / rows

    saved_filepaths: List[str] = []
    frame_idx = 1

    for r in range(rows):
        for c in range(cols):
            if frame_idx > expected_frames:
                break

            # Calculate crop bounding box
            left = int(c * tile_w)
            top = int(r * tile_h)
            right = int((c + 1) * tile_w) if c < cols - 1 else img_w
            bottom = int((r + 1) * tile_h) if r < rows - 1 else img_h

            crop_tile = img.crop((left, top, right, bottom))

            # Canonical filename: e.g. R001_SEQ01_FRAME001.jpg
            filename = f"{road_id}_{sequence_id}_FRAME{frame_idx:03d}.jpg"
            file_path = os.path.join(output_dir, filename)

            # Convert RGBA or Palette to RGB before JPEG save if needed
            if crop_tile.mode != "RGB":
                crop_tile = crop_tile.convert("RGB")

            crop_tile.save(file_path, format="JPEG", quality=95)
            saved_filepaths.append(file_path)

            frame_idx += 1

    return saved_filepaths


def populate_raw_sequences_from_storyboards(
    registry_path: str = "dataset/reference_layers/storyboards.json",
    raw_sequences_root: str = "dataset/raw_sequences",
) -> Dict[str, int]:
    """
    Extract all 3 storyboard sequences into dataset/raw_sequences/ directory structure.
    Returns dictionary mapping sequence_id to extracted frame count.
    """
    registry = load_storyboard_registry(registry_path)
    results = {}

    for seq in registry.get("storyboard_sequences", []):
        seq_id = seq["sequence_id"].replace("-", "")  # e.g. "SEQ01"
        road_id = seq["road_id"]                       # e.g. "R001"
        storyboard_path = seq["file_path"]

        out_dir = os.path.join(raw_sequences_root, f"{road_id}_{seq_id}")
        extracted_files = extract_frames_from_storyboard(
            storyboard_path=storyboard_path,
            output_dir=out_dir,
            road_id=road_id,
            sequence_id=seq_id,
            rows=5,
            cols=6,
            expected_frames=30,
        )
        results[seq_id] = len(extracted_files)

    return results


if __name__ == "__main__":
    res = populate_raw_sequences_from_storyboards()
    print("Storyboard extraction completed:", res)
