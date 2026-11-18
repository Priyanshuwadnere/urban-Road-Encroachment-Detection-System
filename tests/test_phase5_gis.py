"""
Unit tests for Phase 5 GIS Road ROW & Property Boundary Analysis.
Tests layer validities, set algebra, synthetic test cases E-01 and E-02,
chainage calculations, decision states, export files, and academic disclaimers.
"""

import os
import json
import csv
import pytest
from shapely.geometry import shape

from src.config import (
    STATUS_POTENTIAL_ENCROACHMENT,
    STATUS_PERMISSIBLE,
    STATUS_REFERENCE_REQUIRED,
    ACTION_FIELD_VERIFICATION,
    ACTION_NONE,
    ACTION_SUPPLY_REFERENCE,
    ACADEMIC_DISCLAIMER,
)
from src.gis.gis_models import (
    PropertyMasterRecord,
    RoadMasterRecord,
    DetectedObjectGISRecord,
    Phase5EncroachmentResult,
)
from src.gis.phase5_engine import Phase5GISEngine
from src.gis.e01_e02_validator import SyntheticReferenceValidator
from src.gis.map_visualizer import GISMapVisualizer


@pytest.fixture
def sample_parcels():
    with open("dataset/gis_layers/01_PROPERTY_BOUNDARY.geojson", "r", encoding="utf-8") as f:
        data = json.load(f)
    return [
        PropertyMasterRecord(
            parcel_id=feat["properties"]["parcel_id"],
            owner_name_synthetic=feat["properties"]["owner_name_synthetic"],
            address_synthetic=feat["properties"]["address_synthetic"],
            area_sqm=feat["properties"]["area_sqm"],
            geometry_geojson=feat["geometry"],
        )
        for feat in data["features"]
    ]


@pytest.fixture
def sample_road_row():
    with open("dataset/gis_layers/02_ROAD_ROW.geojson", "r", encoding="utf-8") as f:
        row_data = json.load(f)["features"][0]
    with open("dataset/gis_layers/03_ROAD_CENTERLINE.geojson", "r", encoding="utf-8") as f:
        cl_data = json.load(f)["features"][0]
    with open("dataset/gis_layers/04_EXISTING_CARRIAGEWAY.geojson", "r", encoding="utf-8") as f:
        cw_data = json.load(f)["features"][0]

    return RoadMasterRecord(
        row_id=row_data["properties"]["row_id"],
        road_name=row_data["properties"]["road_name"],
        legal_width_m=row_data["properties"]["legal_width_m"],
        geometry_geojson=row_data["geometry"],
        centerline_geojson=cl_data["geometry"],
        carriageway_geojson=cw_data["geometry"],
    )


@pytest.fixture
def gis_engine(sample_parcels, sample_road_row):
    return Phase5GISEngine(parcels=sample_parcels, road_row=sample_road_row)


def test_01_geojson_layer_validity():
    """Verify geometry validity of all 5 GeoJSON reference layers."""
    layer_files = [
        "dataset/gis_layers/01_PROPERTY_BOUNDARY.geojson",
        "dataset/gis_layers/02_ROAD_ROW.geojson",
        "dataset/gis_layers/03_ROAD_CENTERLINE.geojson",
        "dataset/gis_layers/04_EXISTING_CARRIAGEWAY.geojson",
        "dataset/gis_layers/09_CHAINAGE.geojson",
    ]
    for filepath in layer_files:
        assert os.path.exists(filepath), f"Missing layer file: {filepath}"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("type") == "FeatureCollection"
        assert len(data.get("features", [])) > 0
        for feat in data["features"]:
            geom = shape(feat["geometry"])
            assert geom.is_valid, f"Invalid geometry in {filepath}"


def test_02_structure_inside_property(gis_engine):
    """Verify structure 100% inside private property yields WITHIN PERMISSIBLE BOUNDARY."""
    # Structure inside Parcel P-01 (X: 0-20, Y: 0-6) -> X: 2-10, Y: 1-4
    det = DetectedObjectGISRecord(
        detection_id="DET-INSIDE-P01",
        class_id=0,
        class_name="building",
        confidence=0.95,
        pixel_polygon=[(10.0, 10.0), (20.0, 10.0), (20.0, 20.0), (10.0, 20.0), (10.0, 10.0)],
        map_polygon=[(2.0, 1.0), (10.0, 1.0), (10.0, 4.0), (2.0, 4.0), (2.0, 1.0)],
    )
    res = gis_engine.analyze_detection(det)
    assert res.status == STATUS_PERMISSIBLE
    assert res.action_required == ACTION_NONE
    assert res.metrics is None
    assert res.encroachment_polygon_geojson is None


def test_03_structure_outside_row(gis_engine):
    """Verify structure outside the road ROW yields WITHIN PERMISSIBLE BOUNDARY."""
    # Structure far west X: -10 to -5, Y: 0-5
    det = DetectedObjectGISRecord(
        detection_id="DET-OUTSIDE-ROW",
        class_id=0,
        class_name="building",
        confidence=0.90,
        pixel_polygon=[(5.0, 5.0), (15.0, 5.0), (15.0, 15.0), (5.0, 15.0), (5.0, 5.0)],
        map_polygon=[(-10.0, 0.0), (-5.0, 0.0), (-5.0, 5.0), (-10.0, 5.0), (-10.0, 0.0)],
    )
    res = gis_engine.analyze_detection(det)
    assert res.status == STATUS_PERMISSIBLE
    assert res.action_required == ACTION_NONE


def test_04_synthetic_e01_analysis(gis_engine):
    """Verify Synthetic Reference Benchmark Case E-01 (Parcel P-07) metrics."""
    det_e01 = SyntheticReferenceValidator.get_test_case_e01_detection()
    res = gis_engine.analyze_detection(det_e01)

    assert res.status == STATUS_POTENTIAL_ENCROACHMENT
    assert res.action_required == ACTION_FIELD_VERIFICATION
    assert res.parcel_id == "P-07"
    assert res.data_provenance == "SYNTHETIC_GIS_REFERENCE_BENCHMARK"
    assert "awning" in res.structure_concept.lower() or "shop" in res.structure_concept.lower()
    assert res.metrics is not None
    assert abs(res.metrics.area_sqm - 6.00) < 0.01
    assert abs(res.metrics.max_projection_m - 1.20) < 0.01
    assert abs(res.metrics.frontage_m - 5.00) < 0.01
    assert res.severity in ["HIGH", "CRITICAL", "MODERATE"]


def test_05_synthetic_e02_analysis(gis_engine):
    """Verify Synthetic Reference Benchmark Case E-02 (Parcel P-08) metrics."""
    det_e02 = SyntheticReferenceValidator.get_test_case_e02_detection()
    res = gis_engine.analyze_detection(det_e02)

    assert res.status == STATUS_POTENTIAL_ENCROACHMENT
    assert res.action_required == ACTION_FIELD_VERIFICATION
    assert res.parcel_id in ["P-08", "P-09"]
    assert res.data_provenance == "SYNTHETIC_GIS_REFERENCE_BENCHMARK"
    assert "veranda" in res.structure_concept.lower() or "shop" in res.structure_concept.lower()
    assert res.metrics is not None
    assert abs(res.metrics.area_sqm - 3.60) < 0.01
    assert abs(res.metrics.max_projection_m - 0.80) < 0.01
    assert abs(res.metrics.frontage_m - 4.50) < 0.01


def test_06_total_encroachment_sum(gis_engine):
    """Verify total encroached area sum across E-01 and E-02 equals 9.60 m²."""
    res_e01, res_e02, total_area = SyntheticReferenceValidator.validate_e01_e02(gis_engine)
    assert abs(total_area - 9.60) < 0.01


def test_07_chainage_calculation(gis_engine):
    """Verify numeric chainage formatting (e.g. 42.6 -> 0+042.6)."""
    geom = shape({"type": "Point", "coordinates": [24.5, 42.6]})
    dist_m, chainage_str = gis_engine.calculate_chainage(geom)
    assert dist_m == 42.6
    assert chainage_str == "0+042.6"


def test_08_missing_property_layer(sample_road_row):
    """Verify missing parcel layer yields REFERENCE DATA REQUIRED."""
    engine = Phase5GISEngine(parcels=[], road_row=sample_road_row)
    det = SyntheticReferenceValidator.get_test_case_e01_detection()
    res = engine.analyze_detection(det)
    assert res.status == STATUS_REFERENCE_REQUIRED
    assert res.action_required == ACTION_SUPPLY_REFERENCE


def test_09_missing_row_layer(sample_parcels):
    """Verify missing road ROW layer yields REFERENCE DATA REQUIRED."""
    engine = Phase5GISEngine(parcels=sample_parcels, road_row=None)
    det = SyntheticReferenceValidator.get_test_case_e01_detection()
    res = engine.analyze_detection(det)
    assert res.status == STATUS_REFERENCE_REQUIRED
    assert res.action_required == ACTION_SUPPLY_REFERENCE


def test_10_sub_threshold_area(gis_engine):
    """Verify encroached area < MIN_ENCROACHMENT_AREA_SQM yields WITHIN PERMISSIBLE BOUNDARY."""
    # Micro projection: 0.01m projection, 1.0m frontage -> 0.01 m²
    coords = [(28.99, 10.0), (30.0, 10.0), (30.0, 11.0), (28.99, 11.0), (28.99, 10.0)]
    det = DetectedObjectGISRecord(
        detection_id="DET-MICRO",
        class_id=5,
        class_name="ramp",
        confidence=0.85,
        pixel_polygon=[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
        map_polygon=coords,
    )
    res = gis_engine.analyze_detection(det, min_area_threshold=0.1)
    assert res.status == STATUS_PERMISSIBLE


def test_11_metric_bounds(gis_engine):
    """Verify calculated metrics satisfy boundary constraints."""
    det_e01 = SyntheticReferenceValidator.get_test_case_e01_detection()
    res = gis_engine.analyze_detection(det_e01)
    assert res.metrics is not None
    assert res.metrics.area_sqm >= 0.0
    assert res.metrics.frontage_m >= 0.0
    assert res.metrics.max_projection_m >= 0.0
    assert 0.0 <= res.metrics.overlap_ratio_pct <= 100.0


def test_12_pydantic_schema_validation(gis_engine):
    """Verify Pydantic model serialization and deserialization."""
    det_e01 = SyntheticReferenceValidator.get_test_case_e01_detection()
    res = gis_engine.analyze_detection(det_e01)
    dumped = res.model_dump()
    reconstructed = Phase5EncroachmentResult(**dumped)
    assert reconstructed.case_id == res.case_id
    assert reconstructed.disclaimer == ACADEMIC_DISCLAIMER


def test_13_csv_export_integrity(gis_engine, tmp_path):
    """Verify CSV export file generation, headers, and row data."""
    det_e01 = SyntheticReferenceValidator.get_test_case_e01_detection()
    res_e01 = gis_engine.analyze_detection(det_e01)
    csv_file = os.path.join(tmp_path, "test_encroachments.csv")

    Phase5GISEngine.export_to_csv([res_e01], csv_file)
    assert os.path.exists(csv_file)

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 1
        row = reader[0]
        assert row["case_id"] == res_e01.case_id
        assert row["status"] == STATUS_POTENTIAL_ENCROACHMENT
        assert float(row["area_sqm"]) == 6.00
        assert row["disclaimer"] == ACADEMIC_DISCLAIMER


def test_14_geojson_export_integrity(gis_engine, tmp_path):
    """Verify GeoJSON export file generation and FeatureCollection structure."""
    det_e01 = SyntheticReferenceValidator.get_test_case_e01_detection()
    res_e01 = gis_engine.analyze_detection(det_e01)
    geojson_file = os.path.join(tmp_path, "08_POTENTIAL_ENCROACHMENT.geojson")

    Phase5GISEngine.export_to_geojson([res_e01], geojson_file)
    assert os.path.exists(geojson_file)

    with open(geojson_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 1
        feat = data["features"][0]
        assert feat["properties"]["parcel_id"] == "P-07"
        assert feat["properties"]["area_sqm"] == 6.00


def test_15_academic_disclaimer_presence(gis_engine):
    """Verify academic disclaimer is present on all system output schemas."""
    det_e01 = SyntheticReferenceValidator.get_test_case_e01_detection()
    res = gis_engine.analyze_detection(det_e01)
    assert res.disclaimer == ACADEMIC_DISCLAIMER


def test_16_severity_classification():
    """Verify severity categories for various area and projection depth combinations."""
    assert Phase5GISEngine.determine_severity(12.0, 2.5) == "CRITICAL"
    assert Phase5GISEngine.determine_severity(6.0, 1.2) == "HIGH"
    assert Phase5GISEngine.determine_severity(3.0, 0.6) == "MODERATE"
    assert Phase5GISEngine.determine_severity(0.5, 0.2) == "MINOR"
    assert Phase5GISEngine.determine_severity(0.0, 0.0) == "NONE"


def test_17_road_and_footpath_encroachment_zones(gis_engine):
    """Verify that structures in footpath, paved carriageway, or between both are classified as encroachments."""
    det_e01 = SyntheticReferenceValidator.get_test_case_e01_detection()
    res_e01 = gis_engine.analyze_detection(det_e01)
    assert res_e01.status == STATUS_POTENTIAL_ENCROACHMENT
    assert res_e01.encroachment_zone in ["FOOTPATH", "BETWEEN_PAVED_ROAD_AND_FOOTPATH", "PAVED_ROAD"]

