"""
Reference Layer Validator.
Checks presence, completeness, and geometry validity of reference layers
(Cadastral Parcel boundary GeoJSON and Road ROW Corridor GeoJSON).
"""

from typing import Dict, Any, Tuple, Optional
from shapely.geometry import shape
from shapely.validation import explain_validity
from src.config import STATUS_REFERENCE_REQUIRED, ACTION_SUPPLY_REFERENCE
from src.core.schemas import CadastralParcel, RoadROW


class ReferenceDataValidator:
    """Validates vector reference data layers before GIS spatial analysis."""

    @staticmethod
    def validate_geojson_geometry(geojson_dict: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check if GeoJSON geometry is parseable and valid."""
        try:
            geom = shape(geojson_dict)
            if geom.is_empty:
                return False, "Geometry is empty."
            if not geom.is_valid:
                return False, f"Invalid geometry: {explain_validity(geom)}"
            if geom.geom_type not in ["Polygon", "MultiPolygon"]:
                return False, f"Geometry type must be Polygon or MultiPolygon, got {geom.geom_type}"
            return True, None
        except Exception as e:
            return False, f"Failed to parse GeoJSON geometry: {str(e)}"

    @classmethod
    def validate_layers(
        cls,
        parcel: Optional[CadastralParcel],
        row: Optional[RoadROW]
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Check if both legal parcel boundary and road ROW reference layers are present and valid.
        Returns:
            (is_valid: bool, status: str, detail_message: Optional[str])
        """
        if parcel is None and row is None:
            return False, STATUS_REFERENCE_REQUIRED, "Both legal parcel boundary and road ROW reference data are missing."
        if parcel is None:
            return False, STATUS_REFERENCE_REQUIRED, "Legal property parcel reference data is missing."
        if row is None:
            return False, STATUS_REFERENCE_REQUIRED, "Government road ROW corridor reference data is missing."

        parcel_valid, parcel_err = cls.validate_geojson_geometry(parcel.geometry_geojson)
        if not parcel_valid:
            return False, STATUS_REFERENCE_REQUIRED, f"Parcel geometry error: {parcel_err}"

        row_valid, row_err = cls.validate_geojson_geometry(row.geometry_geojson)
        if not row_valid:
            return False, STATUS_REFERENCE_REQUIRED, f"Road ROW geometry error: {row_err}"

        return True, "REFERENCE_DATA_VALID", None
