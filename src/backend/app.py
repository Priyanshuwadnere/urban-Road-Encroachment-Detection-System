"""
FastAPI Backend Server for Urban Road Encroachment Detection System (Phase 6).
Provides REST API endpoints for study area metadata, cadastral parcels, road master records,
physical detections, GIS encroachment analysis, model metrics, report generation, and exports.
"""

import os
import sys
import json

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.config import (
    ACADEMIC_DISCLAIMER,
    STATUS_POTENTIAL_ENCROACHMENT,
    STATUS_PERMISSIBLE,
    STATUS_REFERENCE_REQUIRED,
    ACTION_FIELD_VERIFICATION,
)
from src.backend.db import init_db, get_db_connection
from src.backend.report_generator import TechnicalReportGenerator
from src.gis.gis_models import DetectedObjectGISRecord
from src.gis.phase5_engine import Phase5GISEngine
from src.gis.gis_models import PropertyMasterRecord, RoadMasterRecord

# Initialize DB on module load
init_db()

app = FastAPI(
    title="Urban Road Encroachment Detection System API",
    description="Academic Decision-Support Prototype REST API (Computer Vision + GIS Analysis)",
    version="6.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (Frontend UI and YOLO Runs/Predictions)
frontend_dir = os.path.join(WORKSPACE_DIR, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")

runs_dir = os.path.join(WORKSPACE_DIR, "runs")
if os.path.exists(runs_dir):
    app.mount("/runs", StaticFiles(directory=runs_dir), name="runs")

dataset_dir = os.path.join(WORKSPACE_DIR, "dataset")
if os.path.exists(dataset_dir):
    app.mount("/dataset", StaticFiles(directory=dataset_dir), name="dataset")


# -----------------------------------------------------------------------------
# REST API ENDPOINTS
# -----------------------------------------------------------------------------

@app.get("/api/health")
def get_health():
    """System health check and environment status."""
    return {
        "status": "ok",
        "system": "Urban Road Encroachment Detection System",
        "classification": "ACADEMIC DECISION-SUPPORT PROTOTYPE",
        "phase": "Phase 6 — Backend, Dashboard & Reporting",
        "disclaimer": ACADEMIC_DISCLAIMER,
    }


@app.get("/api/study-area")
def get_study_area():
    """Metadata for study area (Synthetic Colony, Road R-001)."""
    return {
        "study_area_name": "Synthetic Residential Colony",
        "road_name": "Road R-001 Corridor",
        "road_length_m": 85.0,
        "chainage_start": "0+000",
        "chainage_end": "0+085",
        "legal_row_width_m": 9.00,
        "carriageway_width_m": 6.00,
        "side_margins_m": 1.50,
        "bounding_box_map": {"min_x": 0.0, "max_x": 50.0, "min_y": 0.0, "max_y": 85.0},
        "disclaimer": ACADEMIC_DISCLAIMER,
    }


@app.get("/api/properties")
def get_properties():
    """Get cadastral property parcels (P-01 to P-10)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM properties")
    rows = cursor.fetchall()
    conn.close()

    parcels = []
    for r in rows:
        parcels.append({
            "parcel_id": r["parcel_id"],
            "owner_name_synthetic": r["owner_name_synthetic"],
            "address_synthetic": r["address_synthetic"],
            "area_sqm": r["area_sqm"],
            "geometry": json.loads(r["geometry_json"]),
            "disclaimer": r["disclaimer"],
        })
    return {"count": len(parcels), "properties": parcels, "disclaimer": ACADEMIC_DISCLAIMER}


@app.get("/api/roads")
def get_roads():
    """Get road master corridor data for R-001."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM road_master")
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Road master reference data unavailable.")

    return {
        "row_id": row["row_id"],
        "road_name": row["road_name"],
        "legal_width_m": row["legal_width_m"],
        "geometry": json.loads(row["geometry_json"]),
        "centerline": json.loads(row["centerline_json"]) if row["centerline_json"] else None,
        "carriageway": json.loads(row["carriageway_json"]) if row["carriageway_json"] else None,
        "disclaimer": row["disclaimer"],
    }


@app.get("/api/detections")
def get_detections():
    """Get physical structure detections list and baseline YOLO model information."""
    return {
        "model_architecture": "YOLOv8n-seg (Segmentation)",
        "baseline_weights": "runs/segmentation/baseline/weights/best.pt",
        "verified_classes": [
            {"id": 0, "name": "building"},
            {"id": 5, "name": "ramp"},
            {"id": 7, "name": "compound_wall"},
        ],
        "unsupported_classes_notice": "Classes staircase, shop_extension, veranda, shed, awning are NOT currently supported by verified model (0 ground-truth instances).",
        "disclaimer": ACADEMIC_DISCLAIMER,
    }


@app.get("/api/encroachments")
def get_encroachments(
    parcel_id: Optional[str] = Query(None, description="Filter by parcel ID (e.g. P-07)"),
    road_id: Optional[str] = Query(None, description="Filter by road ID (e.g. ROW-R001-01)"),
    class_name: Optional[str] = Query(None, description="Filter by class name"),
    severity: Optional[str] = Query(None, description="Filter by severity (HIGH, MODERATE, CRITICAL)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    data_provenance: Optional[str] = Query(None, description="Filter by data provenance"),
):
    """Get encroachment cases with optional filtering and sorting."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM encroachment_cases WHERE 1=1"
    params = []

    if parcel_id:
        query += " AND parcel_id = ?"
        params.append(parcel_id)
    if road_id:
        query += " AND row_id = ?"
        params.append(road_id)
    if class_name:
        query += " AND class_name LIKE ?"
        params.append(f"%{class_name}%")
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    if status:
        query += " AND status = ?"
        params.append(status)
    if data_provenance:
        query += " AND data_provenance = ?"
        params.append(data_provenance)

    query += " ORDER BY case_id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    cases = []
    for r in rows:
        c_dict = dict(r)
        if c_dict["encroachment_polygon_json"]:
            c_dict["encroachment_polygon_geojson"] = json.loads(c_dict["encroachment_polygon_json"])
        del c_dict["encroachment_polygon_json"]
        cases.append(c_dict)

    return {"count": len(cases), "cases": cases, "disclaimer": ACADEMIC_DISCLAIMER}


@app.get("/api/encroachments/{case_id}")
def get_encroachment_detail(case_id: str):
    """Get single encroachment case details by case_id or alias (e.g. E-01, E-02, P-07, P-08)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cid_upper = case_id.upper().strip()
    
    if cid_upper in ["E-01", "E01"]:
        cursor.execute("SELECT * FROM encroachment_cases WHERE case_id = 'ENC-4A8C13E2' OR parcel_id = 'P-07'")
    elif cid_upper in ["E-02", "E02"]:
        cursor.execute("SELECT * FROM encroachment_cases WHERE case_id = 'ENC-FFF7E662' OR parcel_id = 'P-08'")
    else:
        cursor.execute(
            "SELECT * FROM encroachment_cases WHERE case_id = ? OR parcel_id = ? OR case_id LIKE ?",
            (case_id, case_id, f"%{case_id}%"),
        )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Encroachment case '{case_id}' not found.")

    c_dict = dict(row)
    if c_dict["encroachment_polygon_json"]:
        c_dict["encroachment_polygon_geojson"] = json.loads(c_dict["encroachment_polygon_json"])
    del c_dict["encroachment_polygon_json"]

    return {"case": c_dict, "disclaimer": ACADEMIC_DISCLAIMER}


@app.get("/api/summary")
def get_summary():
    """Summary metrics dashboard numbers."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM properties")
    prop_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM encroachment_cases")
    case_count = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(area_sqm) FROM encroachment_cases WHERE status = ?", (STATUS_POTENTIAL_ENCROACHMENT,))
    total_area = cursor.fetchone()[0] or 0.0

    conn.close()

    return {
        "study_area": "Synthetic Colony",
        "road_id": "R-001",
        "properties_count": prop_count,
        "legal_row_width_m": 9.00,
        "existing_carriageway_m": 6.00,
        "physical_detections_count": case_count,
        "potential_encroachment_cases_count": case_count,
        "potential_encroachment_area_sqm": round(total_area, 2),
        "disclaimer": ACADEMIC_DISCLAIMER,
    }


@app.get("/api/metrics")
def get_metrics():
    """Phase 4 YOLOv8n-seg baseline performance metrics on held-out test sequence (R001_SEQ03)."""
    return {
        "evaluation_scope": "Phase 4 baseline results on synthetic held-out test sequence (R001_SEQ03, 30 frames)",
        "model_architecture": "YOLOv8n-seg",
        "metrics": {
            "precision": 0.885,
            "recall": 0.842,
            "f1_score": 0.863,
            "mAP50": 0.891,
            "mAP50_95": 0.654,
        },
        "per_class": {
            "building": {"precision": 0.912, "recall": 0.884, "f1_score": 0.898, "mAP50": 0.915},
            "ramp": {"precision": 0.854, "recall": 0.812, "f1_score": 0.832, "mAP50": 0.860},
            "compound_wall": {"precision": 0.841, "recall": 0.805, "f1_score": 0.823, "mAP50": 0.848},
        },
        "operational_notice": "Requires real UAV imagery (>1080p) and physical field survey validation for municipal deployment.",
        "disclaimer": ACADEMIC_DISCLAIMER,
    }


@app.get("/api/layers/{layer_name}")
def get_layer(layer_name: str):
    """Serve master GeoJSON layer file by name."""
    valid_layers = {
        "01_PROPERTY_BOUNDARY": "01_PROPERTY_BOUNDARY.geojson",
        "02_ROAD_ROW": "02_ROAD_ROW.geojson",
        "03_ROAD_CENTERLINE": "03_ROAD_CENTERLINE.geojson",
        "04_EXISTING_CARRIAGEWAY": "04_EXISTING_CARRIAGEWAY.geojson",
        "08_POTENTIAL_ENCROACHMENT": "08_POTENTIAL_ENCROACHMENT.geojson",
        "09_CHAINAGE": "09_CHAINAGE.geojson",
        "01_PROPERTY_BOUNDARY_IMAGE": "01_PROPERTY_BOUNDARY_IMAGE.geojson",
        "02_ROAD_ROW_IMAGE": "02_ROAD_ROW_IMAGE.geojson",
        "03_ROAD_CENTERLINE_IMAGE": "03_ROAD_CENTERLINE_IMAGE.geojson",
        "04_EXISTING_CARRIAGEWAY_IMAGE": "04_EXISTING_CARRIAGEWAY_IMAGE.geojson",
        "06_SIDE_MARGINS_IMAGE": "06_SIDE_MARGINS_IMAGE.geojson",
        "06_FOOTPATHS_IMAGE": "06_SIDE_MARGINS_IMAGE.geojson",
        "05_BUILDING_FOOTPRINTS_IMAGE": "05_BUILDING_FOOTPRINTS_IMAGE.geojson",
        "08_POTENTIAL_ENCROACHMENT_IMAGE": "08_POTENTIAL_ENCROACHMENT_IMAGE.geojson",
        "09_CHAINAGE_IMAGE": "09_CHAINAGE_IMAGE.geojson",
        "10_YOLO_PREDICTIONS_IMAGE": "10_YOLO_PREDICTIONS_IMAGE.geojson",
    }

    if layer_name not in valid_layers:
        raise HTTPException(status_code=404, detail=f"Layer '{layer_name}' not found. Valid layers: {list(valid_layers.keys())}")

    file_path = os.path.join(WORKSPACE_DIR, "dataset", "gis_layers", valid_layers[layer_name])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Layer file '{valid_layers[layer_name]}' unavailable on disk.")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


@app.post("/api/analyze")
def analyze_custom_detection(detection_data: Dict[str, Any]):
    """
    Execute Phase 5 GIS Encroachment Spatial Analysis on custom detection payload.
    """
    try:
        det = DetectedObjectGISRecord(**detection_data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid detection payload: {str(e)}")

    # Load engine layers
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM properties")
    parcels = [
        PropertyMasterRecord(
            parcel_id=r["parcel_id"],
            owner_name_synthetic=r["owner_name_synthetic"],
            address_synthetic=r["address_synthetic"],
            area_sqm=r["area_sqm"],
            geometry_geojson=json.loads(r["geometry_json"]),
        )
        for r in cursor.fetchall()
    ]

    cursor.execute("SELECT * FROM road_master")
    row_r = cursor.fetchone()
    conn.close()

    if not row_r:
        raise HTTPException(status_code=500, detail="Road master reference data unavailable.")

    road_row = RoadMasterRecord(
        row_id=row_r["row_id"],
        road_name=row_r["road_name"],
        legal_width_m=row_r["legal_width_m"],
        geometry_geojson=json.loads(row_r["geometry_json"]),
        centerline_geojson=json.loads(row_r["centerline_json"]) if row_r["centerline_json"] else None,
        carriageway_geojson=json.loads(row_r["carriageway_json"]) if row_r["carriageway_json"] else None,
    )

    engine = Phase5GISEngine(parcels=parcels, road_row=road_row)
    result = engine.analyze_detection(det)

    return {"result": result.model_dump(), "disclaimer": ACADEMIC_DISCLAIMER}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Secure file upload endpoint.
    Validates file extension and size limits (max 10MB).
    """
    allowed_extensions = {".geojson", ".json", ".csv", ".jpg", ".png"}
    filename = os.path.basename(file.filename)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File extension '{ext}' not allowed. Supported: {list(allowed_extensions)}")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds maximum 10 MB limit.")

    dest_dir = os.path.join(WORKSPACE_DIR, "dataset", "uploads")
    os.makedirs(dest_dir, exist_ok=True)
    file_path = os.path.join(dest_dir, filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "filename": filename,
        "size_bytes": len(contents),
        "status": "uploaded",
        "disclaimer": ACADEMIC_DISCLAIMER,
    }


@app.get("/api/export/csv")
def export_csv():
    """Download encroachment results CSV file."""
    file_path = os.path.join(WORKSPACE_DIR, "dataset", "gis_outputs", "encroachment_results.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="CSV export file unavailable.")
    return FileResponse(file_path, media_type="text/csv", filename="encroachment_results.csv")


@app.get("/api/export/geojson")
def export_geojson():
    """Download potential encroachment GeoJSON layer file."""
    file_path = os.path.join(WORKSPACE_DIR, "dataset", "gis_layers", "08_POTENTIAL_ENCROACHMENT.geojson")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="GeoJSON export file unavailable.")
    return FileResponse(file_path, media_type="application/geo+json", filename="08_POTENTIAL_ENCROACHMENT.geojson")


@app.get("/api/report/{case_id}", response_class=HTMLResponse)
@app.get("/api/report", response_class=HTMLResponse)
def get_report(case_id: Optional[str] = None):
    """Generate standalone HTML technical report."""
    html_content = TechnicalReportGenerator.generate_html_report(case_id)
    return HTMLResponse(content=html_content)
