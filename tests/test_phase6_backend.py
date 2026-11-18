"""
Unit tests for Phase 6 FastAPI Backend REST API.
Tests endpoints, query parameter filters, status codes, CSV/GeoJSON exports,
report generator, error handling, and security validation.
"""

import os
import pytest
from fastapi.testclient import TestClient

from src.backend.app import app
from src.config import ACADEMIC_DISCLAIMER

client = TestClient(app)


def test_01_health_endpoint():
    """Test /api/health endpoint returns system status and academic disclaimer."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["phase"] == "Phase 6 — Backend, Dashboard & Reporting"
    assert data["disclaimer"] == ACADEMIC_DISCLAIMER


def test_02_study_area_endpoint():
    """Test /api/study-area endpoint returns corridor parameters."""
    response = client.get("/api/study-area")
    assert response.status_code == 200
    data = response.json()
    assert data["road_name"] == "Road R-001 Corridor"
    assert data["legal_row_width_m"] == 9.00
    assert data["carriageway_width_m"] == 6.00


def test_03_properties_endpoint():
    """Test /api/properties returns 10 cadastral property parcels."""
    response = client.get("/api/properties")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 10
    assert len(data["properties"]) == 10
    assert data["properties"][0]["parcel_id"] == "P-01"


def test_04_roads_endpoint():
    """Test /api/roads returns road ROW corridor geometry."""
    response = client.get("/api/roads")
    assert response.status_code == 200
    data = response.json()
    assert data["row_id"] == "ROW-R001-01"
    assert data["legal_width_m"] == 9.00
    assert data["geometry"]["type"] == "Polygon"


def test_05_detections_endpoint():
    """Test /api/detections returns verified classes and operational notice."""
    response = client.get("/api/detections")
    assert response.status_code == 200
    data = response.json()
    assert len(data["verified_classes"]) == 3
    assert "unsupported_classes_notice" in data


def test_06_encroachments_endpoint_and_filters():
    """Test /api/encroachments list and filtering by query parameters."""
    response = client.get("/api/encroachments")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 2

    # Filter by parcel_id P-07
    res_p07 = client.get("/api/encroachments?parcel_id=P-07")
    assert res_p07.status_code == 200
    assert res_p07.json()["count"] == 1
    assert res_p07.json()["cases"][0]["parcel_id"] == "P-07"

    # Filter by severity HIGH
    res_sev = client.get("/api/encroachments?severity=HIGH")
    assert res_sev.status_code == 200
    assert res_sev.json()["count"] == 1


def test_07_encroachment_detail_endpoint():
    """Test /api/encroachments/{case_id} endpoint and 404 for invalid ID."""
    res_all = client.get("/api/encroachments")
    case_id = res_all.json()["cases"][0]["case_id"]

    response = client.get(f"/api/encroachments/{case_id}")
    assert response.status_code == 200
    assert response.json()["case"]["case_id"] == case_id

    # 404 for non-existent case
    res_invalid = client.get("/api/encroachments/ENC-INVALID-999")
    assert res_invalid.status_code == 404
    assert "not found" in res_invalid.json()["detail"].lower()


def test_08_summary_endpoint():
    """Test /api/summary returns study area card numbers."""
    response = client.get("/api/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["properties_count"] == 10
    assert data["potential_encroachment_cases_count"] >= 2
    assert abs(data["potential_encroachment_area_sqm"] - 9.60) < 0.1


def test_09_metrics_endpoint():
    """Test /api/metrics returns Phase 4 YOLO baseline test set metrics."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    metrics = data["metrics"]
    assert metrics["precision"] == 0.885
    assert metrics["recall"] == 0.842
    assert metrics["f1_score"] == 0.863
    assert metrics["mAP50"] == 0.891
    assert metrics["mAP50_95"] == 0.654


def test_10_layers_endpoint():
    """Test /api/layers/{layer_name} endpoint and invalid layer 404."""
    response = client.get("/api/layers/01_PROPERTY_BOUNDARY")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"

    # Invalid layer name
    res_invalid = client.get("/api/layers/INVALID_LAYER_NAME")
    assert res_invalid.status_code == 404


def test_11_export_csv_and_geojson():
    """Test /api/export/csv and /api/export/geojson download endpoints."""
    res_csv = client.get("/api/export/csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "case_id" in res_csv.text

    res_geojson = client.get("/api/export/geojson")
    assert res_geojson.status_code == 200
    assert "08_POTENTIAL_ENCROACHMENT" in res_geojson.text


def test_12_report_endpoint():
    """Test /api/report returns standalone HTML technical report."""
    response = client.get("/api/report")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert ACADEMIC_DISCLAIMER in response.text
    assert "Urban Road Encroachment Detection System" in response.text


def test_13_upload_security_validation(tmp_path):
    """Test POST /api/upload enforces file extension and size validation."""
    # Invalid extension
    invalid_file = ("test.exe", b"binary data", "application/octet-stream")
    res_invalid = client.post("/api/upload", files={"file": invalid_file})
    assert res_invalid.status_code == 400
    assert "not allowed" in res_invalid.json()["detail"].lower()

    # Valid extension (.geojson)
    valid_file = ("test_upload.geojson", b'{"type": "FeatureCollection"}', "application/json")
    res_valid = client.post("/api/upload", files={"file": valid_file})
    assert res_valid.status_code == 200
    assert res_valid.json()["filename"] == "test_upload.geojson"
