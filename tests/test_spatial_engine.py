"""
Unit tests for GIS Spatial Analysis Engine.
Verifies difference (outside_private = structure - legal_boundary)
and intersection (potential_encroachment = outside_private ∩ government_road_ROW).
"""

import pytest
from src.gis.spatial_engine import EncroachmentSpatialEngine
from src.core.schemas import PhysicalObjectDetection, CadastralParcel, RoadROW
from src.config import (
    STATUS_POTENTIAL_ENCROACHMENT,
    STATUS_PERMISSIBLE,
    STATUS_REFERENCE_REQUIRED,
    ACTION_FIELD_VERIFICATION,
    ACTION_NONE,
    ACTION_SUPPLY_REFERENCE,
    ACADEMIC_DISCLAIMER,
)


@pytest.fixture
def spatial_engine():
    return EncroachmentSpatialEngine()


@pytest.fixture
def parcel_west():
    """Parcel W-101: X in [0.0, 20.0], Y in [40.0, 60.0]"""
    return CadastralParcel(
        parcel_id="PARCEL-W-101",
        owner_name_synthetic="West Owner",
        address_synthetic="101 West Lane",
        geometry_geojson={
            "type": "Polygon",
            "coordinates": [[[0.0, 40.0], [20.0, 40.0], [20.0, 60.0], [0.0, 60.0], [0.0, 40.0]]],
        },
    )


@pytest.fixture
def road_row():
    """Road ROW: X in [20.0, 28.0], Y in [0.0, 100.0]"""
    return RoadROW(
        row_id="ROW-MAIN-01",
        road_name="Main Lane",
        legal_width_m=8.0,
        geometry_geojson={
            "type": "Polygon",
            "coordinates": [[[20.0, 0.0], [28.0, 0.0], [28.0, 100.0], [20.0, 100.0], [20.0, 0.0]]],
        },
    )


def test_encroachment_case_1_shop_extension(spatial_engine, parcel_west, road_row):
    """
    Case 1 (Shop Extension): Structure extends from X=15.0 to X=23.0 (3 meters into ROW).
    Y in [45.0, 55.0] (10m frontage).
    """
    shop_extension_detection = PhysicalObjectDetection(
        detection_id="DET-SHOP-01",
        class_id=2,
        class_name="shop_extension",
        confidence=0.92,
        pixel_polygon=[(300.0, 900.0), (460.0, 900.0), (460.0, 1100.0), (300.0, 1100.0)],
        map_polygon=[(15.0, 45.0), (23.0, 45.0), (23.0, 55.0), (15.0, 55.0)],
    )

    result = spatial_engine.analyze(shop_extension_detection, parcel_west, road_row)

    assert result.status == STATUS_POTENTIAL_ENCROACHMENT
    assert result.action_required == ACTION_FIELD_VERIFICATION
    assert result.class_name == "shop_extension"
    assert result.metrics is not None
    assert result.metrics.area_sqm == pytest.approx(30.0, abs=0.1)  # 3m depth * 10m frontage = 30m²
    assert result.metrics.frontage_m == pytest.approx(10.0, abs=0.1)
    assert result.metrics.max_projection_m == pytest.approx(3.0, abs=0.1)
    assert result.disclaimer == ACADEMIC_DISCLAIMER


def test_permissible_building_inside_parcel(spatial_engine, parcel_west, road_row):
    """
    Building structure entirely inside Parcel W-101: X in [5.0, 18.0], Y in [42.0, 58.0].
    Does NOT extend past X=20.0.
    """
    building_detection = PhysicalObjectDetection(
        detection_id="DET-BLDG-01",
        class_id=0,
        class_name="building",
        confidence=0.95,
        pixel_polygon=[(100.0, 840.0), (360.0, 840.0), (360.0, 1160.0), (100.0, 1160.0)],
        map_polygon=[(5.0, 42.0), (18.0, 42.0), (18.0, 58.0), (5.0, 58.0)],
    )

    result = spatial_engine.analyze(building_detection, parcel_west, road_row)

    assert result.status == STATUS_PERMISSIBLE
    assert result.action_required == ACTION_NONE
    assert result.metrics is None
    assert result.encroachment_polygon_geojson is None
    assert result.disclaimer == ACADEMIC_DISCLAIMER


def test_missing_reference_data_returns_reference_required(spatial_engine):
    """
    When parcel or road ROW reference layers are omitted,
    must return STATUS_REFERENCE_REQUIRED ("REFERENCE DATA REQUIRED").
    """
    detection = PhysicalObjectDetection(
        detection_id="DET-UNK-01",
        class_id=1,
        class_name="staircase",
        confidence=0.88,
        pixel_polygon=[(10.0, 10.0), (20.0, 10.0), (20.0, 20.0), (10.0, 20.0)],
        map_polygon=[(20.0, 40.0), (25.0, 40.0), (25.0, 45.0), (20.0, 45.0)],
    )

    # Missing parcel & ROW
    res_no_ref = spatial_engine.analyze(detection, parcel=None, row=None)
    assert res_no_ref.status == STATUS_REFERENCE_REQUIRED
    assert res_no_ref.action_required == ACTION_SUPPLY_REFERENCE
    assert res_no_ref.metrics is None
    assert res_no_ref.disclaimer == ACADEMIC_DISCLAIMER
