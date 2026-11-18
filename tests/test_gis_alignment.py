"""
Automated Verification Suite for GIS Alignment and Spatial Accuracy.
Verifies:
1. Image dimensions (1024x723) and Leaflet image bounds.
2. Polygon vertex transformations between image pixels and map space.
3. Two reference polygons (E-01 and E-02) overlay their intended physical structures.
4. Relative polygon positions and physical 36-pixel (1.85m) spacing are preserved without artificial gap.
5. GeoJSON coordinate systems and validity.
6. Strict separation between Synthetic Benchmarks and YOLO Predictions.
7. Absence of fabricated encroachment results when reference data is missing.
8. Backend layer endpoints and dashboard integration.
"""

import os
import json
import pytest
import numpy as np
from shapely.geometry import shape, Polygon, Point

from fastapi.testclient import TestClient
from src.backend.app import app
from src.config import (
    ACADEMIC_DISCLAIMER,
    STATUS_POTENTIAL_ENCROACHMENT,
    STATUS_REFERENCE_REQUIRED,
    ACTION_SUPPLY_REFERENCE,
    ACTION_FIELD_VERIFICATION,
)
from src.gis.transform import CoordinateTransformer
from src.gis.phase5_engine import Phase5GISEngine
from src.gis.e01_e02_validator import SyntheticReferenceValidator

client = TestClient(app)

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GIS_LAYERS_DIR = os.path.join(WORKSPACE_DIR, "dataset", "gis_layers")
IMAGE_PATH = os.path.join(WORKSPACE_DIR, "dataset", "gis_outputs", "original_drone_survey.jpg")


def test_01_image_dimensions_and_bounds():
    """Verify image dimensions are exactly 1024x723 and aspect ratio is preserved."""
    import cv2
    assert os.path.exists(IMAGE_PATH), f"Original drone survey image missing at {IMAGE_PATH}"
    img = cv2.imread(IMAGE_PATH)
    assert img is not None, "Failed to read original drone survey image"
    h, w = img.shape[:2]
    assert w == 1024, f"Expected image width 1024, got {w}"
    assert h == 723, f"Expected image height 723, got {h}"
    aspect_ratio = w / h
    assert abs(aspect_ratio - (1024.0 / 723.0)) < 1e-4


def test_02_known_polygon_vertices_transformation():
    """Verify coordinate transformation between image pixels (u, v) and metric map space (X, Y)."""
    transformer = CoordinateTransformer.create_uav_calibrated_transformer(
        image_width=1024.0,
        image_height=723.0,
        gsd_m_per_px=0.054545,
        road_centerline_px=475.0,
        metric_centerline_x=24.5,
        metric_datum_y=40.0,
    )

    # Road centerline top and bottom
    top_center_px = [(475.0, 0.0)]
    metric_top = transformer.pixel_to_map(top_center_px)[0]
    assert abs(metric_top[0] - 24.5) < 0.01  # Centerline X = 24.5m
    assert abs(metric_top[1] - 40.0) < 0.01  # Datum Y = 40.0m

    # Reversibility test
    recovered = transformer.map_to_pixel([metric_top])[0]
    assert abs(recovered[0] - 475.0) < 1e-4
    assert abs(recovered[1] - 0.0) < 1e-4

    # E-01 vertex mapping to East corridor of road ROW
    e01_vertex = [(545.0, 117.0)]
    metric_e01 = transformer.pixel_to_map(e01_vertex)[0]
    assert metric_e01[0] > 24.5, "E-01 must be to the East of centerline (X > 24.5)"
    assert abs(transformer.map_to_pixel([metric_e01])[0][0] - 545.0) < 1e-4


def test_03_two_reference_polygons_overlay_intended_structures():
    """Verify reference polygons overlay the intended physical structures on East side of road."""
    e_layer_path = os.path.join(GIS_LAYERS_DIR, "08_POTENTIAL_ENCROACHMENT_IMAGE.geojson")
    assert os.path.exists(e_layer_path)

    with open(e_layer_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data["features"]
    assert len(features) == 2, "Expected exactly 2 reference encroachment features"

    feat_e01 = next(f for f in features if f["properties"]["benchmark_id"] == "E-01")
    feat_e02 = next(f for f in features if f["properties"]["benchmark_id"] == "E-02")

    poly_e01 = shape(feat_e01["geometry"])
    poly_e02 = shape(feat_e02["geometry"])

    # In Leaflet coordinates [lng, lat] = [u, 723 - v]:
    # E-01 bounding box: u in [542, 616], v in [108, 226] => lat in [497, 615]
    bounds_e01 = poly_e01.bounds  # minx, miny, maxx, maxy (lng_min, lat_min, lng_max, lat_max)
    assert bounds_e01[0] >= 540.0 and bounds_e01[2] <= 620.0, f"E-01 lng bounds mismatch: {bounds_e01}"
    assert bounds_e01[1] >= 490.0 and bounds_e01[3] <= 620.0, f"E-01 lat bounds mismatch: {bounds_e01}"

    # E-02 bounding box: u in [550, 650], v in [262, 412] => lat in [311, 465]
    bounds_e02 = poly_e02.bounds
    assert bounds_e02[0] >= 548.0 and bounds_e02[2] <= 655.0, f"E-02 lng bounds mismatch: {bounds_e02}"
    assert bounds_e02[1] >= 310.0 and bounds_e02[3] <= 465.0, f"E-02 lat bounds mismatch: {bounds_e02}"

    # Both must lie on the East side of the road centerline (u > 460)
    assert bounds_e01[0] > 460.0
    assert bounds_e02[0] > 460.0


def test_04_relative_positions_and_spacing_preserved():
    """Verify E-01 is North of E-02 and true 36-pixel physical spacing is preserved without artificial gap."""
    e_layer_path = os.path.join(GIS_LAYERS_DIR, "08_POTENTIAL_ENCROACHMENT_IMAGE.geojson")
    with open(e_layer_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    feat_e01 = next(f for f in data["features"] if f["properties"]["benchmark_id"] == "E-01")
    feat_e02 = next(f for f in data["features"] if f["properties"]["benchmark_id"] == "E-02")

    poly_e01 = shape(feat_e01["geometry"])
    poly_e02 = shape(feat_e02["geometry"])

    # E-01 centroid must be North (higher lat) of E-02 centroid
    cent_e01 = poly_e01.centroid
    cent_e02 = poly_e02.centroid
    assert cent_e01.y > cent_e02.y, f"E-01 (lat={cent_e01.y}) must be North of E-02 (lat={cent_e02.y})"

    # Vertical gap in Leaflet coordinates (lat = 723 - v):
    # E-01 min lat is bottom of E-01 (~498)
    # E-02 max lat is top of E-02 (~461)
    # True gap: ~37 pixels (~1.85m), NOT an artificial 7.5m / 150px gap!
    e01_min_lat = poly_e01.bounds[1]
    e02_max_lat = poly_e02.bounds[3]
    lat_gap = e01_min_lat - e02_max_lat

    assert 30.0 <= lat_gap <= 45.0, f"Expected physical gap between 30 and 45 pixels, got {lat_gap}"
    assert not poly_e01.intersects(poly_e02), "E-01 and E-02 must remain separate distinct polygons"


def test_05_geojson_coordinate_systems_validity():
    """Verify all image-aligned GeoJSON layers have valid geometries within the 1024x723 image canvas."""
    layer_names = [
        "08_POTENTIAL_ENCROACHMENT_IMAGE.geojson",
        "02_ROAD_ROW_IMAGE.geojson",
        "04_EXISTING_CARRIAGEWAY_IMAGE.geojson",
        "03_ROAD_CENTERLINE_IMAGE.geojson",
        "09_CHAINAGE_IMAGE.geojson",
        "01_PROPERTY_BOUNDARY_IMAGE.geojson",
        "10_YOLO_PREDICTIONS_IMAGE.geojson",
    ]

    for lname in layer_names:
        lpath = os.path.join(GIS_LAYERS_DIR, lname)
        assert os.path.exists(lpath), f"Layer file {lname} missing"
        with open(lpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) > 0

        for feat in data["features"]:
            geom = shape(feat["geometry"])
            assert geom.is_valid, f"Invalid geometry in {lname}: {feat['properties']}"
            bounds = geom.bounds
            # lng must be within [0, 1024], lat within [0, 723]
            assert 0.0 <= bounds[0] <= 1024.0, f"X out of bounds in {lname}: {bounds[0]}"
            assert 0.0 <= bounds[2] <= 1024.0, f"X out of bounds in {lname}: {bounds[2]}"
            assert 0.0 <= bounds[1] <= 723.0, f"Y out of bounds in {lname}: {bounds[1]}"
            assert 0.0 <= bounds[3] <= 723.0, f"Y out of bounds in {lname}: {bounds[3]}"


def test_06_benchmark_and_yolo_strict_separation():
    """Verify Synthetic Benchmark geometries and YOLO predictions are strictly separated."""
    bench_path = os.path.join(GIS_LAYERS_DIR, "08_POTENTIAL_ENCROACHMENT_IMAGE.geojson")
    yolo_path = os.path.join(GIS_LAYERS_DIR, "10_YOLO_PREDICTIONS_IMAGE.geojson")

    with open(bench_path, "r", encoding="utf-8") as f:
        bench_data = json.load(f)
    with open(yolo_path, "r", encoding="utf-8") as f:
        yolo_data = json.load(f)

    # Benchmark features must have SYNTHETIC_GIS_REFERENCE_BENCHMARK provenance
    for feat in bench_data["features"]:
        props = feat["properties"]
        assert props["data_provenance"] == "SYNTHETIC_GIS_REFERENCE_BENCHMARK"
        assert "YOLO" not in props["data_provenance"]
        assert props["status"] == STATUS_POTENTIAL_ENCROACHMENT

    # YOLO features must have YOLO_MODEL_PREDICTION provenance and NOT have encroachment determination
    for feat in yolo_data["features"]:
        props = feat["properties"]
        assert props["data_provenance"] == "YOLO_MODEL_PREDICTION"
        assert props["model_architecture"] == "YOLOv8n-seg"
        assert "status" not in props or props.get("status") != STATUS_POTENTIAL_ENCROACHMENT
        assert "BENCHMARK" not in props["data_provenance"]


def test_07_gis_analysis_missing_reference_behavior():
    """Verify GIS analysis does NOT produce fabricated encroachment results when reference data is missing."""
    from src.gis.gis_models import RoadMasterRecord
    with open(os.path.join(GIS_LAYERS_DIR, "02_ROAD_ROW.geojson"), "r", encoding="utf-8") as f:
        row_feat = json.load(f)["features"][0]
    road_row = RoadMasterRecord(
        row_id=row_feat["properties"]["row_id"],
        road_name=row_feat["properties"]["road_name"],
        legal_width_m=row_feat["properties"]["legal_width_m"],
        geometry_geojson=row_feat["geometry"],
    )
    # Engine with road ROW but NO parcels
    engine_no_parcels = Phase5GISEngine(parcels=[], road_row=road_row)
    det = SyntheticReferenceValidator.get_test_case_e01_detection()
    res = engine_no_parcels.analyze_detection(det)
    assert res.status == STATUS_REFERENCE_REQUIRED
    assert res.action_required == ACTION_SUPPLY_REFERENCE
    assert "REFERENCE DATA REQUIRED" in res.status


def test_08_backend_layer_endpoints_and_dashboard_integration():
    """Verify backend endpoints serve image-aligned and metric layers with HTTP 200."""
    layers_to_test = [
        "08_POTENTIAL_ENCROACHMENT_IMAGE",
        "02_ROAD_ROW_IMAGE",
        "04_EXISTING_CARRIAGEWAY_IMAGE",
        "03_ROAD_CENTERLINE_IMAGE",
        "09_CHAINAGE_IMAGE",
        "01_PROPERTY_BOUNDARY_IMAGE",
        "05_BUILDING_FOOTPRINTS_IMAGE",
        "10_YOLO_PREDICTIONS_IMAGE",
        "01_PROPERTY_BOUNDARY",
        "02_ROAD_ROW",
        "08_POTENTIAL_ENCROACHMENT",
    ]

    for l_name in layers_to_test:
        resp = client.get(f"/api/layers/{l_name}")
        assert resp.status_code == 200, f"Endpoint /api/layers/{l_name} returned {resp.status_code}"
        data = resp.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) > 0

    # Test summary and encroachments endpoints
    sum_resp = client.get("/api/summary")
    assert sum_resp.status_code == 200
    assert sum_resp.json()["potential_encroachment_cases_count"] >= 2

    enc_resp = client.get("/api/encroachments")
    assert enc_resp.status_code == 200
    assert enc_resp.json()["count"] >= 2


def test_09_building_footprints_layer_validity():
    """Verify 05_BUILDING_FOOTPRINTS_IMAGE exists with 10 verified building structures."""
    bld_path = os.path.join(GIS_LAYERS_DIR, "05_BUILDING_FOOTPRINTS_IMAGE.geojson")
    assert os.path.exists(bld_path)

    with open(bld_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 10

    for feat in data["features"]:
        props = feat["properties"]
        geom = shape(feat["geometry"])
        assert geom.is_valid
        assert props["data_provenance"] == "VERIFIED_PHYSICAL_BUILDING_FOOTPRINT"
        assert props["status"] == "WITHIN PERMISSIBLE BOUNDARY"
        assert props["setback_from_row_m"] > 0.0


def test_10_no_property_boundary_slices_through_buildings():
    """Verify that cadastral parcel boundaries do NOT cut through or overlap rooftops."""
    bld_path = os.path.join(GIS_LAYERS_DIR, "05_BUILDING_FOOTPRINTS_IMAGE.geojson")
    parcel_path = os.path.join(GIS_LAYERS_DIR, "01_PROPERTY_BOUNDARY_IMAGE.geojson")

    with open(bld_path, "r", encoding="utf-8") as f:
        blds = json.load(f)["features"]
    with open(parcel_path, "r", encoding="utf-8") as f:
        parcels = json.load(f)["features"]

    for b_feat in blds:
        b_id = b_feat["properties"]["building_id"]
        p_id = b_feat["properties"]["parcel_id"]
        b_poly = shape(b_feat["geometry"])

        # Matching parcel must completely enclose the building footprint
        p_feat = next(p for p in parcels if p["properties"]["parcel_id"] == p_id)
        p_poly = shape(p_feat["geometry"])

        assert p_poly.contains(b_poly), f"Building {b_id} is not fully contained in parcel {p_id}"
        overlap = p_poly.intersection(b_poly).area / b_poly.area
        assert overlap >= 0.999, f"Building {b_id} sliced by parcel {p_id}"


def test_11_encroachment_spatial_set_rule():
    """Verify outside_private = structure - parcel and potential_encroachment = outside_private ∩ ROW."""
    bld_path = os.path.join(GIS_LAYERS_DIR, "05_BUILDING_FOOTPRINTS_IMAGE.geojson")
    parcel_path = os.path.join(GIS_LAYERS_DIR, "01_PROPERTY_BOUNDARY_IMAGE.geojson")
    row_path = os.path.join(GIS_LAYERS_DIR, "02_ROAD_ROW_IMAGE.geojson")
    enc_path = os.path.join(GIS_LAYERS_DIR, "08_POTENTIAL_ENCROACHMENT_IMAGE.geojson")

    with open(bld_path, "r", encoding="utf-8") as f:
        blds = json.load(f)["features"]
    with open(parcel_path, "r", encoding="utf-8") as f:
        parcels = json.load(f)["features"]
    with open(row_path, "r", encoding="utf-8") as f:
        row_poly = shape(json.load(f)["features"][0]["geometry"])
    with open(enc_path, "r", encoding="utf-8") as f:
        encs = json.load(f)["features"]

    # 1. All building footprints must have 0 encroachment into road ROW
    for b_feat in blds:
        b_poly = shape(b_feat["geometry"])
        p_poly = shape(next(p for p in parcels if p["properties"]["parcel_id"] == b_feat["properties"]["parcel_id"])["geometry"])
        outside_private = b_poly.difference(p_poly)
        in_row = outside_private.intersection(row_poly)
        assert in_row.area == 0.0, f"Building {b_feat['properties']['building_id']} incorrectly overlaps ROW"

    # 2. Both reference benchmarks E-01 and E-02 must have positive encroachment into road ROW
    for e_feat in encs:
        e_poly = shape(e_feat["geometry"])
        p_poly = shape(next(p for p in parcels if p["properties"]["parcel_id"] == e_feat["properties"]["parcel_id"])["geometry"])
        outside_private = e_poly.difference(p_poly)
        in_row = outside_private.intersection(row_poly)
        assert in_row.area > 0.0, f"Benchmark {e_feat['properties']['benchmark_id']} does not project into ROW"


def test_12_road_centerline_and_corridor_alignment():
    """Verify road centerline, carriageway, legal ROW, and 1.5m side margins are strictly aligned and consistent."""
    cl_path = os.path.join(GIS_LAYERS_DIR, "03_ROAD_CENTERLINE_IMAGE.geojson")
    cw_path = os.path.join(GIS_LAYERS_DIR, "04_EXISTING_CARRIAGEWAY_IMAGE.geojson")
    row_path = os.path.join(GIS_LAYERS_DIR, "02_ROAD_ROW_IMAGE.geojson")
    sm_path = os.path.join(GIS_LAYERS_DIR, "06_SIDE_MARGINS_IMAGE.geojson")

    assert os.path.exists(cl_path)
    assert os.path.exists(cw_path)
    assert os.path.exists(row_path)
    assert os.path.exists(sm_path)

    with open(cl_path, "r", encoding="utf-8") as f:
        cl_data = json.load(f)["features"][0]
    with open(cw_path, "r", encoding="utf-8") as f:
        cw_data = json.load(f)["features"][0]
    with open(row_path, "r", encoding="utf-8") as f:
        row_data = json.load(f)["features"][0]
    with open(sm_path, "r", encoding="utf-8") as f:
        sm_data = json.load(f)["features"]

    cl_geom = shape(cl_data["geometry"])
    cw_geom = shape(cw_data["geometry"])
    row_geom = shape(row_data["geometry"])

    # 1. Geometries must be valid
    assert cl_geom.is_valid
    assert cw_geom.is_valid
    assert row_geom.is_valid
    assert len(sm_data) == 2

    # 2. Centerline must span full visible height from lat=723 to lat=0
    cl_coords = list(cl_geom.coords)
    assert len(cl_coords) == 2
    top_pt, bot_pt = cl_coords[0], cl_coords[1]
    assert abs(top_pt[1] - 723.0) < 1.0, f"Centerline top lat should be 723, got {top_pt[1]}"
    assert abs(bot_pt[1] - 0.0) < 1.0, f"Centerline bot lat should be 0, got {bot_pt[1]}"

    # Calibrated Centerline u at top (v=0) should be 492.5, and at bot (v=723) should be 500.0
    assert 490.0 <= top_pt[0] <= 495.0, f"Centerline top u out of range: {top_pt[0]}"
    assert 498.0 <= bot_pt[0] <= 503.0, f"Centerline bot u out of range: {bot_pt[0]}"

    # 3. ROW must contain Carriageway completely (row_poly.contains(cw_poly))
    assert row_geom.contains(cw_geom), "Legal ROW corridor must completely enclose paved carriageway"

    # 4. Dimension checks:
    # Space between two red lines is Road (Paved Carriageway):
    #   Top (lat=723.0): u_LR = 440.0, u_RR = 544.0 => Road width = 104.0 px (~5.47 m)
    #   Bot (lat=0.0):   u_LR = 426.5, u_RR = 573.0 => Road width = 146.5 px (~7.71 m)
    # Space between yellow and red lines is Footpath:
    #   West Footpath: Top = 19.0 px (~1.00 m), Bot = 13.5 px (~0.71 m)
    #   East Footpath: Top = 29.0 px (~1.53 m), Bot = 29.0 px (~1.53 m)
    # Total ROW bounded by outer yellow lines:
    #   Top = 152.0 px (~8.00 m), Bot = 189.0 px (~9.95 m)
    cw_coords = cw_geom.exterior.coords
    cw_top_u_vals = [pt[0] for pt in cw_coords if abs(pt[1] - 723.0) < 1.0]
    cw_top_width = max(cw_top_u_vals) - min(cw_top_u_vals)
    assert abs(cw_top_width - 104.0) < 1.0, f"Expected 104px road width at top, got {cw_top_width}"

    row_coords_list = row_geom.exterior.coords
    row_top_u_vals = [pt[0] for pt in row_coords_list if abs(pt[1] - 723.0) < 1.0]
    row_top_width = max(row_top_u_vals) - min(row_top_u_vals)
    assert abs(row_top_width - 152.0) < 1.0, f"Expected 152px ROW width at top, got {row_top_width}"

    # Verify footpaths at top:
    left_fp_top = min(cw_top_u_vals) - min(row_top_u_vals)
    right_fp_top = max(row_top_u_vals) - max(cw_top_u_vals)
    assert abs(left_fp_top - 19.0) < 1.0, f"Expected 19.0px west footpath at top, got {left_fp_top}"
    assert abs(right_fp_top - 29.0) < 1.0, f"Expected 29.0px east footpath at top, got {right_fp_top}"

    # Verify bottom (lat=0.0):
    cw_bot_u_vals = [pt[0] for pt in cw_coords if abs(pt[1] - 0.0) < 1.0]
    cw_bot_width = max(cw_bot_u_vals) - min(cw_bot_u_vals)
    assert abs(cw_bot_width - 146.5) < 1.0, f"Expected 146.5px road width at bot, got {cw_bot_width}"

    row_bot_u_vals = [pt[0] for pt in row_coords_list if abs(pt[1] - 0.0) < 1.0]
    row_bot_width = max(row_bot_u_vals) - min(row_bot_u_vals)
    assert abs(row_bot_width - 189.0) < 1.0, f"Expected 189px ROW width at bot, got {row_bot_width}"

    left_fp_bot = min(cw_bot_u_vals) - min(row_bot_u_vals)
    right_fp_bot = max(row_bot_u_vals) - max(cw_bot_u_vals)
    assert abs(left_fp_bot - 13.5) < 1.0, f"Expected 13.5px west footpath at bot, got {left_fp_bot}"
    assert abs(right_fp_bot - 29.0) < 1.0, f"Expected 29.0px east footpath at bot, got {right_fp_bot}"

    # 5. Verify Side Margins Layer features and spatial decomposition
    sm_west_geom = shape(next(f for f in sm_data if f["properties"]["corridor_side"] == "West")["geometry"])
    sm_east_geom = shape(next(f for f in sm_data if f["properties"]["corridor_side"] == "East")["geometry"])

    assert sm_west_geom.is_valid
    assert sm_east_geom.is_valid
    assert row_geom.contains(sm_west_geom)
    assert row_geom.contains(sm_east_geom)
    assert cw_geom.intersection(sm_west_geom).area == 0.0
    assert cw_geom.intersection(sm_east_geom).area == 0.0

    # Area partition identity: ROW area = CW area + West margin area + East margin area
    total_partition_area = cw_geom.area + sm_west_geom.area + sm_east_geom.area
    assert abs(row_geom.area - total_partition_area) < 1.0

    # 6. Verify API layer endpoint for side margins
    res = client.get("/api/layers/06_SIDE_MARGINS_IMAGE")
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["name"] == "06_SIDE_MARGINS_IMAGE"
    assert len(res_data["features"]) == 2


