"""
Individual Drone Frame Validation & Ingestion Engine.
Validates individual frame files, detects corruption, duplicates, missing frames,
and invalid filenames. Computes sequence-level dataset splits preventing temporal leakage.
"""

import os
import re
import json
from typing import List, Dict, Any, Optional, Set, Tuple
from PIL import Image

from src.config import ACADEMIC_DISCLAIMER
from src.ml.dataset_loader import (
    FrameAssetType,
    ValidationStatus,
    IndividualFrameMetadata,
    SequenceValidationSummary,
    SequenceSplitInfo,
    DatasetManifest,
    compute_file_sha256,
)

FILENAME_PATTERN = re.compile(
    r"^R(?P<road>\d+)_SEQ(?P<seq>\d+)_FRAME(?P<frame>\d+)\.(?i:jpg|jpeg|png|webp)$"
)
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class IndividualFrameValidator:
    """Validator for single drone frame files."""

    @staticmethod
    def validate_frame_file(
        file_path: str, asset_type: FrameAssetType = FrameAssetType.RAW_FRAME
    ) -> IndividualFrameMetadata:
        """
        Validate single frame file format, filename pattern, image integrity, and dimensions.
        """
        filename = os.path.basename(file_path)
        match = FILENAME_PATTERN.match(filename)

        if not match:
            return IndividualFrameMetadata(
                road_id="R000",
                sequence_id="SEQ00",
                frame_id=1,
                chainage_m=2.0,
                filename=filename,
                image_path=file_path,
                validation_status=ValidationStatus.INVALID_FILENAME,
                asset_type=asset_type,
            )

        road_num = int(match.group("road"))
        seq_num = int(match.group("seq"))
        frame_num = int(match.group("frame"))

        road_id = f"R{road_num:03d}"
        seq_id = f"SEQ{seq_num:02d}"

        # Frame ID must be between 1 and 30
        if frame_num < 1 or frame_num > 30:
            return IndividualFrameMetadata(
                road_id=road_id,
                sequence_id=seq_id,
                frame_id=min(max(frame_num, 1), 30),
                chainage_m=float(min(max(frame_num, 1), 30) * 2.0),
                filename=filename,
                image_path=file_path,
                validation_status=ValidationStatus.INVALID_FILENAME,
                asset_type=asset_type,
            )

        chainage_m = float(frame_num * 2.0)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        if not os.path.exists(file_path) or file_size == 0:
            return IndividualFrameMetadata(
                road_id=road_id,
                sequence_id=seq_id,
                frame_id=frame_num,
                chainage_m=chainage_m,
                filename=filename,
                image_path=file_path,
                validation_status=ValidationStatus.CORRUPTED,
                asset_type=asset_type,
            )

        # Image integrity check with Pillow
        try:
            with Image.open(file_path) as img:
                img_format = img.format
                width, height = img.size
                img.verify()  # Check for header/file corruption

            # Re-open after verify() to ensure pixel payload loadable
            with Image.open(file_path) as img:
                img.load()

            if img_format not in ALLOWED_FORMATS:
                return IndividualFrameMetadata(
                    road_id=road_id,
                    sequence_id=seq_id,
                    frame_id=frame_num,
                    chainage_m=chainage_m,
                    filename=filename,
                    image_path=file_path,
                    width=width,
                    height=height,
                    format=img_format,
                    file_size_bytes=file_size,
                    validation_status=ValidationStatus.FORMAT_UNSUPPORTED,
                    asset_type=asset_type,
                )

            sha256_hash = compute_file_sha256(file_path)

            return IndividualFrameMetadata(
                road_id=road_id,
                sequence_id=seq_id,
                frame_id=frame_num,
                chainage_m=chainage_m,
                filename=filename,
                image_path=file_path,
                width=width,
                height=height,
                format=img_format,
                file_size_bytes=file_size,
                sha256_hash=sha256_hash,
                validation_status=ValidationStatus.VALID,
                asset_type=asset_type,
            )

        except Exception:
            return IndividualFrameMetadata(
                road_id=road_id,
                sequence_id=seq_id,
                frame_id=frame_num,
                chainage_m=chainage_m,
                filename=filename,
                image_path=file_path,
                file_size_bytes=file_size,
                validation_status=ValidationStatus.CORRUPTED,
                asset_type=asset_type,
            )


class DatasetSequenceIngestor:
    """Ingestion & validation engine for sequential drone frame datasets."""

    def __init__(self, raw_sequences_root: str = "dataset/raw_sequences"):
        self.raw_sequences_root = raw_sequences_root

    def scan_sequence_directory(
        self,
        road_id: str,
        sequence_id: str,
        expected_frames: int = 30,
        known_hashes: Optional[Dict[str, str]] = None,
    ) -> Tuple[SequenceValidationSummary, List[IndividualFrameMetadata]]:
        """
        Scan a single sequence directory (e.g. dataset/raw_sequences/R001_SEQ01/),
        validate individual frames, detect duplicates, missing frames, and corruption.
        """
        if known_hashes is None:
            known_hashes = {}

        seq_dir_name = f"{road_id}_{sequence_id}"
        seq_dir_path = os.path.join(self.raw_sequences_root, seq_dir_name)

        summary = SequenceValidationSummary(
            sequence_id=sequence_id,
            road_id=road_id,
            total_expected_frames=expected_frames,
        )

        frames_metadata: List[IndividualFrameMetadata] = []
        found_frame_ids: Set[int] = set()

        if not os.path.exists(seq_dir_path) or not os.path.isdir(seq_dir_path):
            # Sequence directory does not exist yet -> all frames missing
            summary.missing_frame_ids = list(range(1, expected_frames + 1))
            return summary, frames_metadata

        files = sorted(os.listdir(seq_dir_path))

        for file_name in files:
            file_path = os.path.join(seq_dir_path, file_name)
            if os.path.isdir(file_path):
                continue

            meta = IndividualFrameValidator.validate_frame_file(file_path)

            if meta.validation_status == ValidationStatus.INVALID_FILENAME:
                summary.invalid_filename_count += 1
                frames_metadata.append(meta)
                continue

            if meta.validation_status in [ValidationStatus.CORRUPTED, ValidationStatus.FORMAT_UNSUPPORTED]:
                summary.corrupted_frame_ids.append(meta.frame_id)
                frames_metadata.append(meta)
                continue

            # Duplicate check using SHA256 hash
            if meta.sha256_hash:
                if meta.sha256_hash in known_hashes:
                    meta.validation_status = ValidationStatus.DUPLICATE
                    summary.duplicate_frame_ids.append(meta.frame_id)
                else:
                    known_hashes[meta.sha256_hash] = meta.filename

            if meta.validation_status == ValidationStatus.VALID:
                summary.valid_frames_count += 1
                found_frame_ids.add(meta.frame_id)
                if meta.width and meta.height:
                    summary.resolutions_found.add(f"{meta.width}x{meta.height}")

            frames_metadata.append(meta)

        # Detect missing frame IDs (from 1 to expected_frames)
        all_expected_ids = set(range(1, expected_frames + 1))
        summary.missing_frame_ids = sorted(list(all_expected_ids - found_frame_ids))

        return summary, frames_metadata

    def build_dataset_manifest(
        self,
        expected_sequences: Optional[List[Tuple[str, str]]] = None,
        manifest_output_path: str = "dataset/dataset_manifest.json",
    ) -> DatasetManifest:
        """
        Scan all expected sequences, compute sequence-level splits (TRAIN, VAL, TEST),
        build comprehensive dataset statistics, and output dataset_manifest.json.
        """
        if expected_sequences is None:
            expected_sequences = [
                ("R001", "SEQ01"),
                ("R001", "SEQ02"),
                ("R001", "SEQ03"),
            ]

        # Sequence-level split allocation to prevent temporal frame leakage
        # SEQ01 -> TRAIN, SEQ02 -> VAL, SEQ03 -> TEST (or fallback to TRAIN if single sequence)
        split_assignments = {}
        split_order = [FrameAssetType.TRAIN, FrameAssetType.VAL, FrameAssetType.TEST]
        for idx, (r_id, s_id) in enumerate(expected_sequences):
            split_type = split_order[idx % len(split_order)]
            split_assignments[s_id] = split_type

        total_frames_found = 0
        total_valid = 0
        total_missing = 0
        total_corrupted = 0
        total_duplicate = 0
        total_invalid_filename = 0

        frames_per_seq: Dict[str, int] = {}
        resolutions_summary: Dict[str, int] = {}
        sequence_splits: List[SequenceSplitInfo] = []
        sequence_summaries: List[SequenceValidationSummary] = []

        known_hashes: Dict[str, str] = {}

        for r_id, s_id in expected_sequences:
            summary, frames_meta = self.scan_sequence_directory(r_id, s_id, known_hashes=known_hashes)

            total_frames_found += len(frames_meta)
            total_valid += summary.valid_frames_count
            total_missing += len(summary.missing_frame_ids)
            total_corrupted += len(summary.corrupted_frame_ids)
            total_duplicate += len(summary.duplicate_frame_ids)
            total_invalid_filename += summary.invalid_filename_count

            frames_per_seq[s_id] = summary.valid_frames_count

            for res in summary.resolutions_found:
                resolutions_summary[res] = resolutions_summary.get(res, 0) + summary.valid_frames_count

            sequence_splits.append(
                SequenceSplitInfo(
                    sequence_id=s_id,
                    assigned_split=split_assignments.get(s_id, FrameAssetType.TRAIN),
                    frame_count=summary.valid_frames_count,
                )
            )
            sequence_summaries.append(summary)

        manifest = DatasetManifest(
            total_sequences=len(expected_sequences),
            total_frames_found=total_frames_found,
            total_valid_frames=total_valid,
            total_missing_frames=total_missing,
            total_corrupted_frames=total_corrupted,
            total_duplicate_frames=total_duplicate,
            total_invalid_filename_frames=total_invalid_filename,
            frames_per_sequence=frames_per_seq,
            resolutions_summary=resolutions_summary,
            sequence_splits=sequence_splits,
            sequence_summaries=sequence_summaries,
            disclaimer=ACADEMIC_DISCLAIMER,
        )

        # Write manifest file
        os.makedirs(os.path.dirname(manifest_output_path), exist_ok=True)
        with open(manifest_output_path, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))

        return manifest
