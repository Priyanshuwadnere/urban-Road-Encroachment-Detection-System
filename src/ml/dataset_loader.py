"""
Individual Drone Frame Dataset Ingestion & Metadata Module.
Defines schemas, frame asset types, validation statuses, and metadata generators.
Preserves strict separation between STORYBOARD_REFERENCE, RAW_FRAME, TRAIN, VAL, TEST.
"""

import os
import re
import json
import hashlib
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field, field_validator
from PIL import Image

from src.config import ACADEMIC_DISCLAIMER


class FrameAssetType(str, Enum):
    """Dataset asset categorization preserving strict separation."""
    STORYBOARD_REFERENCE = "STORYBOARD_REFERENCE"
    RAW_FRAME = "RAW_FRAME"
    TRAIN = "TRAIN"
    VAL = "VAL"
    TEST = "TEST"


class ValidationStatus(str, Enum):
    """Validation status for individual frame files."""
    VALID = "VALID"
    CORRUPTED = "CORRUPTED"
    DUPLICATE = "DUPLICATE"
    INVALID_FILENAME = "INVALID_FILENAME"
    RESOLUTION_MISMATCH = "RESOLUTION_MISMATCH"
    FORMAT_UNSUPPORTED = "FORMAT_UNSUPPORTED"
    MISSING = "MISSING"


class DroneFrameMeta(BaseModel):
    """Legacy/Compatibility metadata schema for sequential drone frames."""
    frame_filename: str = Field(..., description="Canonical frame filename (e.g. R001_SEQ01_FRAME001.jpg)")
    road_id: str = Field(..., description="Road identifier (e.g. R001)")
    sequence_id: str = Field(..., description="Sequence identifier (e.g. SEQ01)")
    frame_index: int = Field(..., ge=1, le=30, description="1-indexed frame sequence number (1 to 30)")
    chainage_m: float = Field(..., ge=2.0, le=60.0, description="Linear chainage along road (meters)")
    disclaimer: str = Field(default=ACADEMIC_DISCLAIMER)

    @field_validator("chainage_m")
    @classmethod
    def validate_chainage(cls, v: float, info) -> float:
        frame_idx = info.data.get("frame_index")
        if frame_idx is not None:
            expected_chainage = float(frame_idx * 2.0)
            if abs(v - expected_chainage) > 1e-3:
                raise ValueError(f"chainage_m ({v}m) does not match expected {expected_chainage}m for frame_index {frame_idx}")
        return v


class IndividualFrameMetadata(BaseModel):
    """Complete Phase 2 metadata schema for individual drone frame files."""
    road_id: str = Field(..., description="Road identifier (e.g. R001)")
    sequence_id: str = Field(..., description="Sequence identifier (e.g. SEQ01)")
    frame_id: int = Field(..., ge=1, le=30, description="1-indexed frame number (1 to 30)")
    chainage_m: float = Field(..., ge=2.0, le=60.0, description="Linear chainage along road corridor (meters)")
    filename: str = Field(..., description="Image filename (e.g. R001_SEQ01_FRAME001.jpg)")
    image_path: str = Field(..., description="Absolute or relative file path")
    width: Optional[int] = Field(default=None, description="Image width in pixels")
    height: Optional[int] = Field(default=None, description="Image height in pixels")
    format: Optional[str] = Field(default=None, description="Image file format (JPEG, PNG, WEBP)")
    file_size_bytes: Optional[int] = Field(default=None, description="File size in bytes")
    sha256_hash: Optional[str] = Field(default=None, description="Perceptual/SHA256 hash for deduplication")
    validation_status: ValidationStatus = Field(default=ValidationStatus.VALID)
    asset_type: FrameAssetType = Field(default=FrameAssetType.RAW_FRAME)
    disclaimer: str = Field(default=ACADEMIC_DISCLAIMER)

    @field_validator("chainage_m")
    @classmethod
    def validate_chainage(cls, v: float, info) -> float:
        frame_id = info.data.get("frame_id")
        if frame_id is not None:
            expected = float(frame_id * 2.0)
            if abs(v - expected) > 1e-3:
                raise ValueError(f"chainage_m ({v}m) does not match expected {expected}m for frame_id {frame_id}")
        return v


class SequenceValidationSummary(BaseModel):
    """Statistical summary per survey sequence."""
    sequence_id: str = Field(...)
    road_id: str = Field(...)
    total_expected_frames: int = Field(default=30)
    valid_frames_count: int = Field(default=0)
    missing_frame_ids: List[int] = Field(default_factory=list)
    corrupted_frame_ids: List[int] = Field(default_factory=list)
    duplicate_frame_ids: List[int] = Field(default_factory=list)
    invalid_filename_count: int = Field(default=0)
    resolutions_found: Set[str] = Field(default_factory=set)


class SequenceSplitInfo(BaseModel):
    """Sequence-level dataset split mapping to prevent temporal frame leakage."""
    sequence_id: str
    assigned_split: FrameAssetType  # TRAIN, VAL, or TEST
    frame_count: int


class DatasetManifest(BaseModel):
    """Complete dataset manifest schema."""
    total_sequences: int = Field(default=0)
    total_frames_found: int = Field(default=0)
    total_valid_frames: int = Field(default=0)
    total_missing_frames: int = Field(default=0)
    total_corrupted_frames: int = Field(default=0)
    total_duplicate_frames: int = Field(default=0)
    total_invalid_filename_frames: int = Field(default=0)
    frames_per_sequence: Dict[str, int] = Field(default_factory=dict)
    resolutions_summary: Dict[str, int] = Field(default_factory=dict)
    sequence_splits: List[SequenceSplitInfo] = Field(default_factory=list)
    sequence_summaries: List[SequenceValidationSummary] = Field(default_factory=list)
    disclaimer: str = Field(default=ACADEMIC_DISCLAIMER)


def parse_drone_frame_filename(filename: str) -> DroneFrameMeta:
    """
    Parse canonical drone frame filename format:
    Pattern: R<road_id>_SEQ<seq_id>_FRAME<frame_id>.jpg
    Example: R001_SEQ01_FRAME015.jpg -> Road R001, Sequence SEQ01, Frame 15, Chainage 30.0m
    """
    pattern = r"^R(?P<road>\d+)_SEQ(?P<seq>\d+)_FRAME(?P<frame>\d+)\.(?i:jpg|jpeg|png)$"
    match = re.match(pattern, filename.strip())
    if not match:
        raise ValueError(
            f"Filename '{filename}' does not follow canonical pattern 'R001_SEQ01_FRAME001.jpg'"
        )

    road_num = int(match.group("road"))
    seq_num = int(match.group("seq"))
    frame_num = int(match.group("frame"))

    road_id = f"R{road_num:03d}"
    seq_id = f"SEQ{seq_num:02d}"
    chainage_m = float(frame_num * 2.0)

    return DroneFrameMeta(
        frame_filename=filename,
        road_id=road_id,
        sequence_id=seq_id,
        frame_index=frame_num,
        chainage_m=chainage_m,
    )


def load_storyboard_registry(registry_path: str = "dataset/reference_layers/storyboards.json") -> Dict[str, Any]:
    """
    Load the registered STORYBOARD_REFERENCE assets catalog.
    Enforces strict non-training, reference-only usage rules.
    """
    if not os.path.exists(registry_path):
        raise FileNotFoundError(f"Storyboard registry file not found: {registry_path}")

    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("asset_type") != "STORYBOARD_REFERENCE":
        raise ValueError(f"Invalid asset_type in {registry_path}: expected 'STORYBOARD_REFERENCE'")

    return data


def validate_sequence_continuity(frames: List[DroneFrameMeta]) -> bool:
    """
    Validate sequence frame index continuity and 2m chainage step size.
    Returns True if sequence is strictly consecutive without gaps.
    """
    if not frames:
        return False

    sorted_frames = sorted(frames, key=lambda f: f.frame_index)

    for i in range(len(sorted_frames) - 1):
        curr_f = sorted_frames[i]
        next_f = sorted_frames[i + 1]

        if next_f.frame_index != curr_f.frame_index + 1:
            return False
        if abs(next_f.chainage_m - (curr_f.chainage_m + 2.0)) > 1e-3:
            return False

    return True


def compute_file_sha256(file_path: str) -> str:
    """Compute SHA256 checksum of a file for duplicate detection."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
