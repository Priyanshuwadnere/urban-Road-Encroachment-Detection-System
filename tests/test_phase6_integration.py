"""
Integration tests for Phase 6 Urban Road Encroachment Detection System.
Tests end-to-end workflow: GIS layers -> FastAPI endpoints -> SQLite Database
-> Encroachment Analysis -> HTML Report -> File Exports.
"""

import os
import json
import pytest
from fastapi.testclient import TestClient

from src.backend.app import app
from src.backend.db import get_db_connection
from src.config import ACADEMIC_DISCLAIMER, STATUS_POTENTIAL_ENCROACHMENT, ACTION_FIELD_VERIFICATION

client = TestClient(app)


def test_01_full_system_integration():
    """Verify complete end-to-end data pipeline integration."""
    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200

    # 2. Check DB Seeding
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM properties")
    assert cursor.fetchone()[0] == 10
    cursor.execute("SELECT COUNT(*) FROM encroachment_cases")
    assert cursor.fetchone()[0] >= 2
    conn.close()

    # 3. Check Summary Dashboard Endpoint
    res_sum = client.get("/api/summary")
    assert res_sum.status_code == 200
    sum_data = res_sum.json()
    assert sum_data["properties_count"] == 10
    assert abs(sum_data["potential_encroachment_area_sqm"] - 9.60) < 0.1

    # 4. Execute Custom GIS Analysis via POST /api/analyze
    custom_payload = {
        "detection_id": "INTEG-TEST-DET-01",
        "frame_id": "INTEG_FRAME_001.jpg",
        "sequence_id": "INTEG_SEQ01",
        "class_id": 5,
        "class_name": "ramp",
        "structure_concept": "ramp / entrance projection",
        "data_provenance": "INTEGRATION_TEST_PAYLOAD",
        "confidence": 0.95,
        "pixel_polygon": [(10.0, 10.0), (50.0, 10.0), (50.0, 50.0), (10.0, 50.0), (10.0, 10.0)],
        "map_polygon": [(27.8, 8.5), (33.0, 8.5), (33.0, 13.5), (27.8, 13.5), (27.8, 8.5)],
    }
    res_analyze = client.post("/api/analyze", json=custom_payload)
    assert res_analyze.status_code == 200
    res_data = res_analyze.json()["result"]
    assert res_data["status"] == STATUS_POTENTIAL_ENCROACHMENT
    assert res_data["action_required"] == ACTION_FIELD_VERIFICATION
    assert abs(res_data["metrics"]["area_sqm"] - 6.00) < 0.01

    # 5. Report Generation & Export Integrity
    res_report = client.get("/api/report")
    assert res_report.status_code == 200
    assert ACADEMIC_DISCLAIMER in res_report.text

    res_csv = client.get("/api/export/csv")
    assert res_csv.status_code == 200
    assert "case_id" in res_csv.text

    res_geojson = client.get("/api/export/geojson")
    assert res_geojson.status_code == 200
    assert "FeatureCollection" in res_geojson.text
