"""
Pydantic schemas and domain data models for Phase 5 GIS Analysis.
Extends core system schemas with property master, road master, chainage fields,
and data provenance tracking (YOLO Prediction vs. Synthetic Reference Benchmark).
"""

from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.config import ACADEMIC_DISCLAIMER
from src.core.schemas import EncroachmentMetrics


class PropertyMasterRecord(BaseModel):
    """Legal cadastral property parcel record in GIS database."""
    parcel_id: str = Field(..., description="Cadastral survey parcel ID (e.g. P-01 to P-10)")
    owner_name_synthetic: str = Field(..., description="Synthetic owner name")
    address_synthetic: str = Field(..., description="Synthetic parcel address")
    area_sqm: float = Field(..., gt=0.0, description="Legal parcel area in square meters")
    geometry_geojson: Dict[str, Any] = Field(..., description="GeoJSON polygon boundary geometry")
    disclaimer: str = Field(default=ACADEMIC_DISCLAIMER)


class RoadMasterRecord(BaseModel):
    """Government Road Right-of-Way (ROW) corridor master record."""
    row_id: str = Field(..., description="Road ROW corridor ID")
    road_name: str = Field(..., description="Official road name (e.g. Road R-001)")
    legal_width_m: float = Field(..., gt=0.0, description="Prescribed legal ROW corridor width in meters")
    geometry_geojson: Dict[str, Any] = Field(..., description="GeoJSON polygon geometry of legal ROW corridor")
    centerline_geojson: Optional[Dict[str, Any]] = Field(default=None, description="GeoJSON LineString of road centerline")
    carriageway_geojson: Optional[Dict[str, Any]] = Field(default=None, description="GeoJSON polygon of paved carriageway")
    disclaimer: str = Field(default=ACADEMIC_DISCLAIMER)


class DetectedObjectGISRecord(BaseModel):
    """Physical object detection georeferenced in GIS map space."""
    detection_id: str = Field(..., description="Unique detection identifier")
    frame_id: Optional[str] = Field(default=None, description="Source video frame filename")
    sequence_id: Optional[str] = Field(default=None, description="Source video sequence ID")
    class_id: int = Field(default=-1, description="Physical object class ID (0-7 for YOLO, -1 for synthetic benchmark)")
    class_name: str = Field(..., description="Physical structure class name or reference structure concept")
    structure_concept: Optional[str] = Field(default=None, description="Original structure concept (e.g. staircase/shop-side extension)")
    data_provenance: str = Field(default="YOLO_MODEL_PREDICTION", description="Source provenance (YOLO_MODEL_PREDICTION or SYNTHETIC_GIS_REFERENCE_BENCHMARK)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection or synthetic benchmark confidence score")
    pixel_polygon: List[Tuple[float, float]] = Field(..., min_length=3, description="Image pixel coordinates [(u, v), ...]")
    map_polygon: List[Tuple[float, float]] = Field(..., min_length=3, description="Georeferenced map coordinates [(X, Y), ...]")


class Phase5EncroachmentResult(BaseModel):
    """Complete Phase 5 Encroachment Analysis Result."""
    case_id: str = Field(..., description="Unique encroachment case reference ID")
    detection_id: str = Field(..., description="Source physical object detection ID")
    frame_id: Optional[str] = Field(default=None, description="Source frame ID")
    sequence_id: Optional[str] = Field(default=None, description="Source sequence ID")
    class_id: int = Field(default=-1, description="Physical object class ID (-1 for reference cases)")
    class_name: str = Field(...)
    structure_concept: Optional[str] = Field(default=None, description="Original reference structure concept")
    data_provenance: str = Field(default="YOLO_MODEL_PREDICTION", description="Data provenance classification")
    parcel_id: Optional[str] = Field(default=None, description="Associated legal parcel ID (e.g. P-07)")
    row_id: Optional[str] = Field(default=None, description="Associated road ROW corridor ID")
    status: str = Field(..., description="GIS Decision Status string")
    action_required: str = Field(..., description="Recommended action flag")
    severity: str = Field(default="NONE", description="Engineering severity category (CRITICAL, HIGH, MODERATE, MINOR, NONE, UNKNOWN)")
    confidence: float = Field(...)
    chainage_m: Optional[float] = Field(default=None, description="Perpendicular chainage distance along centerline (m)")
    chainage_str: Optional[str] = Field(default=None, description="Formatted chainage string (e.g. 0+011.0)")
    metrics: Optional[EncroachmentMetrics] = Field(default=None)
    encroachment_zone: Optional[str] = Field(
        default=None,
        description="Corridor zone: 'FOOTPATH', 'PAVED_ROAD', or 'BETWEEN_PAVED_ROAD_AND_FOOTPATH'"
    )
    encroachment_polygon_geojson: Optional[Dict[str, Any]] = Field(default=None, description="GeoJSON polygon of encroaching portion")
    disclaimer: str = Field(default=ACADEMIC_DISCLAIMER)
