"""
Pydantic schemas and domain data models for Urban Road Encroachment Detection System.
"""

from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from src.config import (
    PHYSICAL_CLASSES,
    ACADEMIC_DISCLAIMER,
    STATUS_REFERENCE_REQUIRED,
    STATUS_PERMISSIBLE,
    STATUS_POTENTIAL_ENCROACHMENT,
)


class PhysicalObjectDetection(BaseModel):
    """
    Physical structure object detected by ML model (Classes 0-7).
    CRITICAL: Does NOT directly assert encroachment.
    """
    detection_id: str = Field(..., description="Unique detection identifier")
    class_id: int = Field(..., ge=0, le=7, description="Physical object class ID (0 to 7)")
    class_name: str = Field(..., description="Physical object class name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="ML detection confidence score")
    pixel_polygon: List[Tuple[float, float]] = Field(
        ..., min_length=3, description="Polygon boundary vertices in image pixel space [(u, v), ...]"
    )
    map_polygon: Optional[List[Tuple[float, float]]] = Field(
        default=None, description="Georeferenced polygon boundary vertices in metric map space [(X, Y), ...]"
    )

    @field_validator("class_name")
    @classmethod
    def validate_class_name(cls, v: str, info) -> str:
        class_id = info.data.get("class_id")
        if class_id is not None and class_id in PHYSICAL_CLASSES:
            expected = PHYSICAL_CLASSES[class_id]
            if v != expected:
                raise ValueError(f"class_name '{v}' does not match expected '{expected}' for class_id {class_id}")
        return v


class CadastralParcel(BaseModel):
    """Legal property boundary dataset record."""
    parcel_id: str = Field(..., description="Cadastral survey / parcel number")
    owner_name_synthetic: str = Field(
        ..., description="Synthetic owner name (SYNTHETIC / ACADEMIC PROTOTYPE)"
    )
    address_synthetic: str = Field(..., description="Synthetic property address")
    geometry_geojson: Dict[str, Any] = Field(..., description="GeoJSON polygon geometry of parcel boundary")
    disclaimer: str = Field(default=ACADEMIC_DISCLAIMER)


class RoadROW(BaseModel):
    """Government Road Right-of-Way (ROW) corridor reference dataset record."""
    row_id: str = Field(..., description="Road ROW corridor identifier")
    road_name: str = Field(..., description="Name of public road")
    legal_width_m: float = Field(..., gt=0.0, description="Prescribed legal ROW width in meters")
    geometry_geojson: Dict[str, Any] = Field(..., description="GeoJSON polygon geometry of road ROW corridor")
    disclaimer: str = Field(default=ACADEMIC_DISCLAIMER)


class EncroachmentMetrics(BaseModel):
    """Spatial metrics for detected encroachment."""
    area_sqm: float = Field(..., ge=0.0, description="Encroachment area in square meters")
    frontage_m: float = Field(..., ge=0.0, description="Encroachment frontage width along road line in meters")
    max_projection_m: float = Field(..., ge=0.0, description="Maximum projection depth into ROW in meters")
    overlap_ratio_pct: float = Field(..., ge=0.0, le=100.0, description="Percentage of detected structure in ROW")


class EncroachmentAnalysisResult(BaseModel):
    """Complete GIS spatial analysis result for a physical structure."""
    case_id: str = Field(..., description="Unique case reference ID")
    detection_id: str = Field(..., description="Source physical detection ID")
    class_id: int = Field(..., ge=0, le=7)
    class_name: str = Field(...)
    parcel_id: Optional[str] = Field(default=None, description="Matched legal property parcel ID")
    row_id: Optional[str] = Field(default=None, description="Matched road ROW corridor ID")
    status: str = Field(..., description="GIS Decision Status string")
    action_required: str = Field(..., description="Recommended action flag")
    severity: str = Field(default="NONE", description="Severity classification (CRITICAL, HIGH, MODERATE, MINOR, NONE, UNKNOWN)")
    confidence: float = Field(...)
    metrics: Optional[EncroachmentMetrics] = Field(default=None)
    encroachment_zone: Optional[str] = Field(
        default=None,
        description="Corridor zone: 'FOOTPATH', 'PAVED_ROAD', or 'BETWEEN_PAVED_ROAD_AND_FOOTPATH'"
    )
    encroachment_polygon_geojson: Optional[Dict[str, Any]] = Field(
        default=None, description="GeoJSON representation of spatial overlap geometry"
    )
    disclaimer: str = Field(default=ACADEMIC_DISCLAIMER)
