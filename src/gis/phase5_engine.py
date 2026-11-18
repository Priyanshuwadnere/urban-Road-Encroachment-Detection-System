r"""
Phase 5 GIS Encroachment Spatial Engine.
Executes georeferenced spatial set operations, property parcel assignment,
chainage calculations, severity classifications, and CSV/GeoJSON exports.

Vector Set Algebra:
  outside_private = detected_structure \ legal_property_boundary
  potential_encroachment = outside_private ∩ government_road_ROW
"""

import os
import csv
import json
import uuid
from typing import Optional, Dict, Any, List, Tuple, Union
from shapely.geometry import shape, mapping, Polygon, MultiPolygon, LineString, Point
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
from src.core.schemas import EncroachmentMetrics
from src.core.exceptions import InvalidGeometryError
from src.gis.validator import ReferenceDataValidator
from src.gis.gis_models import (
    PropertyMasterRecord,
    RoadMasterRecord,
    DetectedObjectGISRecord,
    Phase5EncroachmentResult,
)


class Phase5GISEngine:
    """Core spatial analysis engine for Phase 5 GIS Road ROW & Property Boundary Analysis."""

    def __init__(
        self,
        parcels: Optional[List[PropertyMasterRecord]] = None,
        road_row: Optional[RoadMasterRecord] = None,
    ):
        """
        Initialize GIS engine with cadastral parcels and road ROW master records.
        """
        self.parcels = parcels or []
        self.road_row = road_row
        self.parcel_shapes: Dict[str, Polygon] = {}
        for p in self.parcels:
            try:
                geom = shape(p.geometry_geojson)
                if not geom.is_valid:
                    geom = geom.buffer(0)
                self.parcel_shapes[p.parcel_id] = geom
            except Exception:
                pass

        self.row_shape: Optional[Polygon] = None
        self.centerline_shape: Optional[LineString] = None
        if self.road_row and self.road_row.geometry_geojson:
            try:
                g = shape(self.road_row.geometry_geojson)
                if not g.is_valid:
                    g = g.buffer(0)
                self.row_shape = g
            except Exception:
                pass

        if self.road_row and self.road_row.centerline_geojson:
            try:
                cl = shape(self.road_row.centerline_geojson)
                if isinstance(cl, LineString):
                    self.centerline_shape = cl
            except Exception:
                pass

        self.carriageway_shape: Optional[Polygon] = None
        self.side_margins_shape: Optional[Polygon] = None
        if self.road_row and self.road_row.carriageway_geojson:
            try:
                cw = shape(self.road_row.carriageway_geojson)
                if not cw.is_valid:
                    cw = cw.buffer(0)
                self.carriageway_shape = cw
            except Exception:
                pass

        if self.row_shape is not None and self.carriageway_shape is not None:
            try:
                sm = self.row_shape.difference(self.carriageway_shape)
                if not sm.is_valid:
                    sm = sm.buffer(0)
                self.side_margins_shape = sm
            except Exception:
                pass

    @staticmethod
    def coords_to_polygon(coords: List[Tuple[float, float]]) -> Polygon:
        """Convert a list of (x, y) coordinates into a valid Shapely Polygon."""
        if len(coords) < 3:
            raise InvalidGeometryError(f"Polygon requires at least 3 vertices, got {len(coords)}")
        poly = Polygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty:
            raise InvalidGeometryError("Resulting polygon is empty.")
        return poly

    def assign_property(self, structure_geom: Polygon) -> Optional[PropertyMasterRecord]:
        """
        Assign a physical structure detection to the most appropriate legal property parcel based on max overlap.
        """
        if not self.parcels or structure_geom.is_empty:
            return None

        best_parcel = None
        max_overlap_area = 0.0

        for parcel in self.parcels:
            p_geom = self.parcel_shapes.get(parcel.parcel_id)
            if p_geom and not p_geom.is_empty:
                inter = structure_geom.intersection(p_geom)
                if not inter.is_empty and inter.area > max_overlap_area:
                    max_overlap_area = inter.area
                    best_parcel = parcel

        if best_parcel is None:
            # Fallback to minimum distance if no overlap
            min_dist = float("inf")
            for parcel in self.parcels:
                p_geom = self.parcel_shapes.get(parcel.parcel_id)
                if p_geom and not p_geom.is_empty:
                    dist = structure_geom.distance(p_geom)
                    if dist < min_dist:
                        min_dist = dist
                        best_parcel = parcel

        return best_parcel

    def calculate_chainage(self, geom: Any) -> Tuple[float, str]:
        """
        Calculate perpendicular chainage distance (m) along road centerline line and format string.
        Format: '0+042.6' for 42.6m along centerline.
        """
        if self.centerline_shape is None or geom.is_empty:
            return 0.0, "0+000.0"

        centroid = geom.centroid
        dist_m = float(self.centerline_shape.project(centroid))
        km = int(dist_m // 1000)
        m = dist_m % 1000
        formatted_str = f"{km}+{m:05.1f}"
        return round(dist_m, 2), formatted_str

    @staticmethod
    def compute_frontage_width(encroachment_geom: Any, row_geom: Any) -> float:
        """Estimate frontage width (m) along the road corridor boundary line."""
        if encroachment_geom.is_empty:
            return 0.0

        shared_edge = encroachment_geom.boundary.intersection(row_geom.boundary)
        if not shared_edge.is_empty and shared_edge.length > 0.001:
            return float(shared_edge.length)

        # Fallback to bounding box dimension along Y (or max side)
        minx, miny, maxx, maxy = encroachment_geom.bounds
        frontage = maxy - miny
        if frontage > 0.001:
            return float(frontage)
        return float(encroachment_geom.area ** 0.5)

    @staticmethod
    def compute_max_projection_depth(encroachment_geom: Any, parcel_geom: Optional[Polygon]) -> float:
        """Calculate maximum projection depth (m) perpendicular from parcel boundary into ROW."""
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
                pt_geom = Point(pt)
                dist = parcel_boundary.distance(pt_geom)
                if dist > max_dist:
                    max_dist = dist

        return float(max_dist)

    @staticmethod
    def determine_severity(area_sqm: float, max_depth_m: float) -> str:
        """Determine engineering severity classification."""
        if area_sqm >= 10.0 or max_depth_m >= 2.0:
            return "CRITICAL"
        elif area_sqm >= 5.0 or max_depth_m >= 1.0:
            return "HIGH"
        elif area_sqm >= 2.0 or max_depth_m >= 0.5:
            return "MODERATE"
        elif area_sqm > 0.0:
            return "MINOR"
        return "NONE"

    def analyze_detection(
        self,
        detection: DetectedObjectGISRecord,
        override_parcel: Optional[PropertyMasterRecord] = None,
        min_area_threshold: float = MIN_ENCROACHMENT_AREA_SQM,
    ) -> Phase5EncroachmentResult:
        r"""
        Execute GIS Encroachment Analysis for a single detected physical structure.

        Formula:
          outside_private = detected_structure \ legal_property_boundary
          potential_encroachment = outside_private ∩ government_road_ROW
        """
        case_id = f"ENC-{uuid.uuid4().hex[:8].upper()}"

        # 1. Structure geometry creation
        try:
            structure_geom = self.coords_to_polygon(detection.map_polygon)
        except Exception:
            structure_geom = self.coords_to_polygon(detection.pixel_polygon)

        # 2. Parcel assignment
        parcel = override_parcel or self.assign_property(structure_geom)
        parcel_geom = self.parcel_shapes.get(parcel.parcel_id) if parcel else None

        # 3. Layer Validation Check
        if parcel is None or self.row_shape is None or parcel_geom is None:
            return Phase5EncroachmentResult(
                case_id=case_id,
                detection_id=detection.detection_id,
                frame_id=detection.frame_id,
                sequence_id=detection.sequence_id,
                class_id=detection.class_id,
                class_name=detection.class_name,
                structure_concept=detection.structure_concept,
                data_provenance=detection.data_provenance,
                parcel_id=parcel.parcel_id if parcel else None,
                row_id=self.road_row.row_id if self.road_row else None,
                status=STATUS_REFERENCE_REQUIRED,
                action_required=ACTION_SUPPLY_REFERENCE,
                severity="UNKNOWN",
                confidence=detection.confidence,
                chainage_m=None,
                chainage_str=None,
                metrics=None,
                encroachment_polygon_geojson=None,
                disclaimer=ACADEMIC_DISCLAIMER,
            )

        # 4. GIS Set Operations
        # outside_private = detected_structure \ legal_property_boundary
        outside_private = structure_geom.difference(parcel_geom)

        if outside_private.is_empty:
            chainage_m, chainage_str = self.calculate_chainage(structure_geom)
            return Phase5EncroachmentResult(
                case_id=case_id,
                detection_id=detection.detection_id,
                frame_id=detection.frame_id,
                sequence_id=detection.sequence_id,
                class_id=detection.class_id,
                class_name=detection.class_name,
                structure_concept=detection.structure_concept,
                data_provenance=detection.data_provenance,
                parcel_id=parcel.parcel_id,
                row_id=self.road_row.row_id,
                status=STATUS_PERMISSIBLE,
                action_required=ACTION_NONE,
                severity="NONE",
                confidence=detection.confidence,
                chainage_m=chainage_m,
                chainage_str=chainage_str,
                metrics=None,
                encroachment_polygon_geojson=None,
                disclaimer=ACADEMIC_DISCLAIMER,
            )

        # potential_encroachment = outside_private ∩ government_road_ROW
        potential_encroachment = outside_private.intersection(self.row_shape)
        encroachment_area = potential_encroachment.area if not potential_encroachment.is_empty else 0.0

        # 5. Threshold & Metrics Calculation
        if encroachment_area >= min_area_threshold:
            frontage = self.compute_frontage_width(potential_encroachment, self.row_shape)
            max_depth = self.compute_max_projection_depth(potential_encroachment, parcel_geom)
            overlap_pct = (encroachment_area / structure_geom.area) * 100.0 if structure_geom.area > 0 else 0.0
            severity = self.determine_severity(encroachment_area, max_depth)
            chainage_m, chainage_str = self.calculate_chainage(potential_encroachment)

            # Determine corridor zone: Footpath, Paved Road, or Between Paved Road & Footpath
            encroachment_zone = "FOOTPATH"
            if not potential_encroachment.is_empty:
                cw_area = 0.0
                sm_area = 0.0
                if self.carriageway_shape is not None:
                    inter_cw = potential_encroachment.intersection(self.carriageway_shape)
                    cw_area = inter_cw.area if not inter_cw.is_empty else 0.0
                if self.side_margins_shape is not None:
                    inter_sm = potential_encroachment.intersection(self.side_margins_shape)
                    sm_area = inter_sm.area if not inter_sm.is_empty else 0.0

                if cw_area > 0.05 and sm_area > 0.05:
                    encroachment_zone = "BETWEEN_PAVED_ROAD_AND_FOOTPATH"
                elif cw_area > 0.05:
                    encroachment_zone = "PAVED_ROAD"
                else:
                    encroachment_zone = "FOOTPATH"

            metrics = EncroachmentMetrics(
                area_sqm=round(encroachment_area, 3),
                frontage_m=round(frontage, 3),
                max_projection_m=round(max_depth, 3),
                overlap_ratio_pct=round(min(overlap_pct, 100.0), 2),
            )

            enc_geojson = mapping(potential_encroachment)

            return Phase5EncroachmentResult(
                case_id=case_id,
                detection_id=detection.detection_id,
                frame_id=detection.frame_id,
                sequence_id=detection.sequence_id,
                class_id=detection.class_id,
                class_name=detection.class_name,
                structure_concept=detection.structure_concept,
                data_provenance=detection.data_provenance,
                parcel_id=parcel.parcel_id,
                row_id=self.road_row.row_id,
                status=STATUS_POTENTIAL_ENCROACHMENT,
                action_required=ACTION_FIELD_VERIFICATION,
                severity=severity,
                confidence=detection.confidence,
                chainage_m=chainage_m,
                chainage_str=chainage_str,
                metrics=metrics,
                encroachment_zone=encroachment_zone,
                encroachment_polygon_geojson=enc_geojson,
                disclaimer=ACADEMIC_DISCLAIMER,
            )
        else:
            chainage_m, chainage_str = self.calculate_chainage(structure_geom)
            return Phase5EncroachmentResult(
                case_id=case_id,
                detection_id=detection.detection_id,
                frame_id=detection.frame_id,
                sequence_id=detection.sequence_id,
                class_id=detection.class_id,
                class_name=detection.class_name,
                structure_concept=detection.structure_concept,
                data_provenance=detection.data_provenance,
                parcel_id=parcel.parcel_id,
                row_id=self.road_row.row_id,
                status=STATUS_PERMISSIBLE,
                action_required=ACTION_NONE,
                severity="NONE",
                confidence=detection.confidence,
                chainage_m=chainage_m,
                chainage_str=chainage_str,
                metrics=None,
                encroachment_polygon_geojson=None,
                disclaimer=ACADEMIC_DISCLAIMER,
            )

    @staticmethod
    def export_to_csv(results: List[Phase5EncroachmentResult], file_path: str) -> None:
        """Export analysis results to CSV file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        fieldnames = [
            "case_id",
            "detection_id",
            "frame_id",
            "sequence_id",
            "class_id",
            "class_name",
            "structure_concept",
            "data_provenance",
            "parcel_id",
            "row_id",
            "status",
            "action_required",
            "severity",
            "confidence",
            "chainage_m",
            "chainage_str",
            "area_sqm",
            "frontage_m",
            "max_projection_m",
            "overlap_ratio_pct",
            "disclaimer",
        ]
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                row = {
                    "case_id": r.case_id,
                    "detection_id": r.detection_id,
                    "frame_id": r.frame_id or "",
                    "sequence_id": r.sequence_id or "",
                    "class_id": r.class_id,
                    "class_name": r.class_name,
                    "structure_concept": r.structure_concept or r.class_name,
                    "data_provenance": r.data_provenance,
                    "parcel_id": r.parcel_id or "",
                    "row_id": r.row_id or "",
                    "status": r.status,
                    "action_required": r.action_required,
                    "severity": r.severity,
                    "confidence": r.confidence,
                    "chainage_m": r.chainage_m if r.chainage_m is not None else "",
                    "chainage_str": r.chainage_str or "",
                    "area_sqm": r.metrics.area_sqm if r.metrics else 0.0,
                    "frontage_m": r.metrics.frontage_m if r.metrics else 0.0,
                    "max_projection_m": r.metrics.max_projection_m if r.metrics else 0.0,
                    "overlap_ratio_pct": r.metrics.overlap_ratio_pct if r.metrics else 0.0,
                    "disclaimer": r.disclaimer,
                }
                writer.writerow(row)

    @staticmethod
    def export_to_geojson(results: List[Phase5EncroachmentResult], file_path: str) -> None:
        """Export encroaching geometries to GeoJSON FeatureCollection."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        features = []
        for r in results:
            if r.status == STATUS_POTENTIAL_ENCROACHMENT and r.encroachment_polygon_geojson:
                feature = {
                    "type": "Feature",
                    "properties": {
                        "case_id": r.case_id,
                        "detection_id": r.detection_id,
                        "class_name": r.class_name,
                        "structure_concept": r.structure_concept or r.class_name,
                        "data_provenance": r.data_provenance,
                        "parcel_id": r.parcel_id,
                        "row_id": r.row_id,
                        "status": r.status,
                        "action_required": r.action_required,
                        "severity": r.severity,
                        "chainage_str": r.chainage_str,
                        "encroachment_zone": r.encroachment_zone or "FOOTPATH",
                        "area_sqm": r.metrics.area_sqm if r.metrics else 0.0,
                        "frontage_m": r.metrics.frontage_m if r.metrics else 0.0,
                        "max_projection_m": r.metrics.max_projection_m if r.metrics else 0.0,
                        "disclaimer": r.disclaimer,
                    },
                    "geometry": r.encroachment_polygon_geojson,
                }
                features.append(feature)

        geojson_data = {
          "type": "FeatureCollection",
          "name": "08_POTENTIAL_ENCROACHMENT",
          "disclaimer": ACADEMIC_DISCLAIMER,
          "features": features,
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f, indent=2)
