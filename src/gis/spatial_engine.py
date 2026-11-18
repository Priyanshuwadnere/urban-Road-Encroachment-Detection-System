"""
GIS Spatial Analysis Engine for Urban Road Encroachment Detection.
Executes vector set operations:
  outside_private = detected_structure - legal_property_boundary
  potential_encroachment = outside_private ∩ government_road_ROW

Calculates spatial metrics: area (m²), frontage width (m), max projection depth (m),
and evaluates severity and field verification flags.
"""

import uuid
from typing import Optional, Dict, Any, List, Tuple
from shapely.geometry import shape, mapping, Polygon, MultiPolygon, LineString
from shapely.ops import unary_union

from src.config import (
    MIN_ENCROACHMENT_AREA_SQM,
    STATUS_POTENTIAL_ENCROACHMENT,
    STATUS_PERMISSIBLE,
    STATUS_REFERENCE_REQUIRED,
    ACTION_FIELD_VERIFICATION,
    ACTION_NONE,
    ACTION_SUPPLY_REFERENCE,
    ACADEMIC_DISCLAIMER,
)
from src.core.schemas import (
    PhysicalObjectDetection,
    CadastralParcel,
    RoadROW,
    EncroachmentMetrics,
    EncroachmentAnalysisResult,
)
from src.core.exceptions import InvalidGeometryError
from src.gis.validator import ReferenceDataValidator


class EncroachmentSpatialEngine:
    """Core GIS spatial logic engine performing set algebra and metric estimations."""

    @staticmethod
    def _coords_to_polygon(coords: List[Tuple[float, float]]) -> Polygon:
        """Convert a list of (x, y) tuples into a valid Shapely Polygon."""
        if len(coords) < 3:
            raise InvalidGeometryError(f"Polygon requires at least 3 vertices, got {len(coords)}")
        poly = Polygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)  # Fix minor self-intersections
        if poly.is_empty:
            raise InvalidGeometryError("Resulting polygon is empty.")
        return poly

    @staticmethod
    def _compute_frontage_width(encroachment_geom: Any, row_geom: Any) -> float:
        """
        Estimate frontage width (m) along the road corridor line.
        Calculates shared boundary length or oriented bounding box length along the road.
        """
        if encroachment_geom.is_empty:
            return 0.0

        # Intersection of encroachment boundary with road ROW boundary
        shared_edge = encroachment_geom.boundary.intersection(row_geom.boundary)
        if not shared_edge.is_empty and shared_edge.length > 0.001:
            return float(shared_edge.length)

        # Fallback: Minimum rotated rectangle bounding box length
        try:
            rect = encroachment_geom.minimum_rotated_rectangle
            if isinstance(rect, Polygon) and not rect.is_empty:
                coords = list(rect.exterior.coords)
                side_lens = [
                    ((coords[i][0] - coords[i + 1][0]) ** 2 + (coords[i][1] - coords[i + 1][1]) ** 2) ** 0.5
                    for i in range(len(coords) - 1)
                ]
                return float(max(side_lens))
        except Exception:
            pass

        return float((encroachment_geom.area) ** 0.5)

    @staticmethod
    def _compute_max_projection_depth(encroachment_geom: Any, parcel_geom: Any) -> float:
        """
        Calculate maximum projection depth (m) perpendicular from private boundary into ROW.
        """
        if encroachment_geom.is_empty or parcel_geom is None or parcel_geom.is_empty:
            return 0.0

        parcel_boundary = parcel_geom.boundary
        if isinstance(encroachment_geom, Polygon):
            polys = [encroachment_geom]
        elif isinstance(encroachment_geom, MultiPolygon):
            polys = list(encroachment_geom.geoms)
        else:
            return 0.0

        max_dist = 0.0
        for poly in polys:
            for pt in poly.exterior.coords:
                dist = parcel_boundary.distance(shape({"type": "Point", "coordinates": pt}))
                if dist > max_dist:
                    max_dist = dist

        return float(max_dist)

    @staticmethod
    def _determine_severity(area_sqm: float, max_depth_m: float) -> str:
        """Determine severity category based on area and projection depth."""
        if area_sqm >= 10.0 or max_depth_m >= 2.0:
            return "CRITICAL"
        elif area_sqm >= 5.0 or max_depth_m >= 1.0:
            return "HIGH"
        elif area_sqm >= 2.0 or max_depth_m >= 0.5:
            return "MODERATE"
        elif area_sqm > 0.0:
            return "MINOR"
        return "NONE"

    def analyze(
        self,
        detection: PhysicalObjectDetection,
        parcel: Optional[CadastralParcel] = None,
        row: Optional[RoadROW] = None,
        min_area_threshold: float = MIN_ENCROACHMENT_AREA_SQM,
    ) -> EncroachmentAnalysisResult:
        """
        Execute GIS Encroachment Spatial Analysis.

        Formula:
          outside_private = detected_structure - legal_property_boundary
          potential_encroachment = outside_private ∩ government_road_ROW
        """
        case_id = f"ENC-{uuid.uuid4().hex[:8].upper()}"

        # 1. Validate reference layer availability
        is_valid_ref, status_msg, detail_err = ReferenceDataValidator.validate_layers(parcel, row)
        if not is_valid_ref:
            return EncroachmentAnalysisResult(
                case_id=case_id,
                detection_id=detection.detection_id,
                class_id=detection.class_id,
                class_name=detection.class_name,
                parcel_id=parcel.parcel_id if parcel else None,
                row_id=row.row_id if row else None,
                status=STATUS_REFERENCE_REQUIRED,
                action_required=ACTION_SUPPLY_REFERENCE,
                severity="UNKNOWN",
                confidence=detection.confidence,
                metrics=None,
                encroachment_polygon_geojson=None,
                disclaimer=ACADEMIC_DISCLAIMER,
            )

        # 2. Convert geometries to Shapely objects
        if detection.map_polygon is not None and len(detection.map_polygon) >= 3:
            structure_geom = self._coords_to_polygon(detection.map_polygon)
        else:
            structure_geom = self._coords_to_polygon(detection.pixel_polygon)

        parcel_geom = shape(parcel.geometry_geojson)
        row_geom = shape(row.geometry_geojson)

        # 3. GIS Set Operations
        # outside_private = detected_structure - legal_property_boundary
        outside_private = structure_geom.difference(parcel_geom)

        if outside_private.is_empty:
            # Structure is entirely inside private property
            return EncroachmentAnalysisResult(
                case_id=case_id,
                detection_id=detection.detection_id,
                class_id=detection.class_id,
                class_name=detection.class_name,
                parcel_id=parcel.parcel_id,
                row_id=row.row_id,
                status=STATUS_PERMISSIBLE,
                action_required=ACTION_NONE,
                severity="NONE",
                confidence=detection.confidence,
                metrics=None,
                encroachment_polygon_geojson=None,
                disclaimer=ACADEMIC_DISCLAIMER,
            )

        # potential_encroachment = outside_private ∩ government_road_ROW
        potential_encroachment = outside_private.intersection(row_geom)

        encroachment_area = potential_encroachment.area if not potential_encroachment.is_empty else 0.0

        # 4. Threshold & Decision Logic
        if encroachment_area >= min_area_threshold:
            frontage = self._compute_frontage_width(potential_encroachment, row_geom)
            max_depth = self._compute_max_projection_depth(potential_encroachment, parcel_geom)
            overlap_pct = (encroachment_area / structure_geom.area) * 100.0 if structure_geom.area > 0 else 0.0
            severity = self._determine_severity(encroachment_area, max_depth)

            metrics = EncroachmentMetrics(
                area_sqm=round(encroachment_area, 3),
                frontage_m=round(frontage, 3),
                max_projection_m=round(max_depth, 3),
                overlap_ratio_pct=round(min(overlap_pct, 100.0), 2),
            )

            enc_geojson = mapping(potential_encroachment)

            return EncroachmentAnalysisResult(
                case_id=case_id,
                detection_id=detection.detection_id,
                class_id=detection.class_id,
                class_name=detection.class_name,
                parcel_id=parcel.parcel_id,
                row_id=row.row_id,
                status=STATUS_POTENTIAL_ENCROACHMENT,
                action_required=ACTION_FIELD_VERIFICATION,
                severity=severity,
                confidence=detection.confidence,
                metrics=metrics,
                encroachment_polygon_geojson=enc_geojson,
                disclaimer=ACADEMIC_DISCLAIMER,
            )
        else:
            return EncroachmentAnalysisResult(
                case_id=case_id,
                detection_id=detection.detection_id,
                class_id=detection.class_id,
                class_name=detection.class_name,
                parcel_id=parcel.parcel_id,
                row_id=row.row_id,
                status=STATUS_PERMISSIBLE,
                action_required=ACTION_NONE,
                severity="NONE",
                confidence=detection.confidence,
                metrics=None,
                encroachment_polygon_geojson=None,
                disclaimer=ACADEMIC_DISCLAIMER,
            )
