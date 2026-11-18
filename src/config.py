"""
Configuration module for Urban Road Encroachment Detection System.
Defines ML class taxonomies, GIS status constants, default thresholds,
and mandatory academic disclaimers.
"""

from typing import Dict

# Academic disclaimer string required on all system outputs
ACADEMIC_DISCLAIMER: str = (
    "SYNTHETIC / ACADEMIC PROTOTYPE — NOT AN OFFICIAL MUNICIPAL RECORD"
)

# Physical structure classes for YOLO Instance Segmentation (0 to 7)
# CRITICAL RULE: NO 'encroachment' class exists. ML detects physical structures ONLY.
PHYSICAL_CLASSES: Dict[int, str] = {
    0: "building",
    1: "staircase",
    2: "shop_extension",
    3: "veranda",
    4: "shed",
    5: "ramp",
    6: "awning",
    7: "compound_wall",
}

CLASS_NAME_TO_ID: Dict[str, int] = {name: cid for cid, name in PHYSICAL_CLASSES.items()}

# GIS Decision Status Constants
STATUS_POTENTIAL_ENCROACHMENT: str = "POTENTIAL ROAD ROW ENCROACHMENT"
STATUS_PERMISSIBLE: str = "WITHIN PERMISSIBLE BOUNDARY"
STATUS_REFERENCE_REQUIRED: str = "REFERENCE DATA REQUIRED"

ACTION_FIELD_VERIFICATION: str = "FIELD VERIFICATION REQUIRED"
ACTION_NONE: str = "NO ACTION REQUIRED"
ACTION_SUPPLY_REFERENCE: str = "SUPPLY MISSING PARCEL OR ROAD ROW REFERENCE GEOMETRY"

# Spatial Analysis Thresholds
MIN_ENCROACHMENT_AREA_SQM: float = 0.1  # Minimum area (m²) to classify as potential encroachment
DEFAULT_PIXEL_PER_METER: float = 20.0   # Default scaling factor if homography matrix is uncalibrated
