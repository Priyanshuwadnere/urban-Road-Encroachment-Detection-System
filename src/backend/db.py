"""
SQLite Database Layer for Phase 6 Decision Support Backend.
Manages persistent storage for cadastral properties, road ROW master records,
physical detections, encroachment analysis cases, and audit logs.
"""

import os
import sys
import sqlite3
import json

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from src.config import ACADEMIC_DISCLAIMER

DB_PATH = os.path.join(WORKSPACE_DIR, "database", "encroachment_system.db")


def get_db_connection() -> sqlite3.Connection:
    """Get SQLite database connection with row factory enabled."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create database tables and seed initial records from GIS layers."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS properties (
        parcel_id TEXT PRIMARY KEY,
        owner_name_synthetic TEXT NOT NULL,
        address_synthetic TEXT NOT NULL,
        area_sqm REAL NOT NULL,
        geometry_json TEXT NOT NULL,
        disclaimer TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS road_master (
        row_id TEXT PRIMARY KEY,
        road_name TEXT NOT NULL,
        legal_width_m REAL NOT NULL,
        geometry_json TEXT NOT NULL,
        centerline_json TEXT,
        carriageway_json TEXT,
        disclaimer TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS detections (
        detection_id TEXT PRIMARY KEY,
        frame_id TEXT,
        sequence_id TEXT,
        class_id INTEGER NOT NULL,
        class_name TEXT NOT NULL,
        structure_concept TEXT,
        data_provenance TEXT NOT NULL,
        confidence REAL NOT NULL,
        pixel_polygon_json TEXT NOT NULL,
        map_polygon_json TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS encroachment_cases (
        case_id TEXT PRIMARY KEY,
        detection_id TEXT NOT NULL,
        frame_id TEXT,
        sequence_id TEXT,
        class_id INTEGER NOT NULL,
        class_name TEXT NOT NULL,
        structure_concept TEXT,
        data_provenance TEXT NOT NULL,
        parcel_id TEXT,
        row_id TEXT,
        status TEXT NOT NULL,
        action_required TEXT NOT NULL,
        severity TEXT NOT NULL,
        confidence REAL NOT NULL,
        chainage_m REAL,
        chainage_str TEXT,
        area_sqm REAL NOT NULL,
        frontage_m REAL NOT NULL,
        max_projection_m REAL NOT NULL,
        overlap_ratio_pct REAL NOT NULL,
        encroachment_polygon_json TEXT,
        disclaimer TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_name TEXT NOT NULL,
        detail_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    seed_db(conn)
    conn.close()


def seed_db(conn: sqlite3.Connection):
    """Seed database with master GeoJSON records if tables are empty."""
    cursor = conn.cursor()

    # 1. Seed Properties
    cursor.execute("SELECT COUNT(*) FROM properties")
    if cursor.fetchone()[0] == 0:
        p_path = r"e:\Urban Road Encroachment Detection System\dataset\gis_layers\01_PROPERTY_BOUNDARY.geojson"
        if os.path.exists(p_path):
            with open(p_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for feat in data.get("features", []):
                props = feat["properties"]
                cursor.execute(
                    "INSERT INTO properties VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        props["parcel_id"],
                        props["owner_name_synthetic"],
                        props["address_synthetic"],
                        props["area_sqm"],
                        json.dumps(feat["geometry"]),
                        ACADEMIC_DISCLAIMER,
                    ),
                )

    # 2. Seed Road Master
    cursor.execute("SELECT COUNT(*) FROM road_master")
    if cursor.fetchone()[0] == 0:
        row_path = r"e:\Urban Road Encroachment Detection System\dataset\gis_layers\02_ROAD_ROW.geojson"
        cl_path = r"e:\Urban Road Encroachment Detection System\dataset\gis_layers\03_ROAD_CENTERLINE.geojson"
        cw_path = r"e:\Urban Road Encroachment Detection System\dataset\gis_layers\04_EXISTING_CARRIAGEWAY.geojson"

        if os.path.exists(row_path):
            with open(row_path, "r", encoding="utf-8") as f:
                row_feat = json.load(f)["features"][0]
            cl_json = None
            if os.path.exists(cl_path):
                with open(cl_path, "r", encoding="utf-8") as f:
                    cl_json = json.dumps(json.load(f)["features"][0]["geometry"])
            cw_json = None
            if os.path.exists(cw_path):
                with open(cw_path, "r", encoding="utf-8") as f:
                    cw_json = json.dumps(json.load(f)["features"][0]["geometry"])

            props = row_feat["properties"]
            cursor.execute(
                "INSERT INTO road_master VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    props["row_id"],
                    props["road_name"],
                    props["legal_width_m"],
                    json.dumps(row_feat["geometry"]),
                    cl_json,
                    cw_json,
                    ACADEMIC_DISCLAIMER,
                ),
            )

    # 3. Seed Encroachment Cases (E-01 and E-02)
    cursor.execute("SELECT COUNT(*) FROM encroachment_cases")
    if cursor.fetchone()[0] == 0:
        # Load from synthetic reference validator or phase5 export
        from src.gis.gis_models import PropertyMasterRecord, RoadMasterRecord
        from src.gis.phase5_engine import Phase5GISEngine
        from src.gis.e01_e02_validator import SyntheticReferenceValidator

        p_path = r"e:\Urban Road Encroachment Detection System\dataset\gis_layers\01_PROPERTY_BOUNDARY.geojson"
        with open(p_path, "r", encoding="utf-8") as f:
            parcels_data = json.load(f)
        parcels = [
            PropertyMasterRecord(
                parcel_id=feat["properties"]["parcel_id"],
                owner_name_synthetic=feat["properties"]["owner_name_synthetic"],
                address_synthetic=feat["properties"]["address_synthetic"],
                area_sqm=feat["properties"]["area_sqm"],
                geometry_geojson=feat["geometry"],
            )
            for feat in parcels_data["features"]
        ]

        row_path = r"e:\Urban Road Encroachment Detection System\dataset\gis_layers\02_ROAD_ROW.geojson"
        cl_path = r"e:\Urban Road Encroachment Detection System\dataset\gis_layers\03_ROAD_CENTERLINE.geojson"
        cw_path = r"e:\Urban Road Encroachment Detection System\dataset\gis_layers\04_EXISTING_CARRIAGEWAY.geojson"

        with open(row_path, "r", encoding="utf-8") as f:
            row_feat = json.load(f)["features"][0]
        with open(cl_path, "r", encoding="utf-8") as f:
            cl_feat = json.load(f)["features"][0]
        with open(cw_path, "r", encoding="utf-8") as f:
            cw_feat = json.load(f)["features"][0]

        road_row = RoadMasterRecord(
            row_id=row_feat["properties"]["row_id"],
            road_name=row_feat["properties"]["road_name"],
            legal_width_m=row_feat["properties"]["legal_width_m"],
            geometry_geojson=row_feat["geometry"],
            centerline_geojson=cl_feat["geometry"],
            carriageway_geojson=cw_feat["geometry"],
        )

        engine = Phase5GISEngine(parcels=parcels, road_row=road_row)
        res_e01, res_e02, _ = SyntheticReferenceValidator.validate_e01_e02(engine)

        for r, fixed_cid in zip([res_e01, res_e02], ["ENC-4A8C13E2", "ENC-FFF7E662"]):
            cursor.execute(
                """
                INSERT INTO encroachment_cases 
                (case_id, detection_id, frame_id, sequence_id, class_id, class_name, structure_concept, 
                 data_provenance, parcel_id, row_id, status, action_required, severity, confidence, 
                 chainage_m, chainage_str, area_sqm, frontage_m, max_projection_m, overlap_ratio_pct, 
                 encroachment_polygon_json, disclaimer)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fixed_cid,
                    r.detection_id,
                    r.frame_id or "",
                    r.sequence_id or "",
                    r.class_id,
                    r.class_name,
                    r.structure_concept or r.class_name,
                    r.data_provenance,
                    r.parcel_id or "",
                    r.row_id or "",
                    r.status,
                    r.action_required,
                    r.severity,
                    r.confidence,
                    r.chainage_m,
                    r.chainage_str or "",
                    r.metrics.area_sqm if r.metrics else 0.0,
                    r.metrics.frontage_m if r.metrics else 0.0,
                    r.metrics.max_projection_m if r.metrics else 0.0,
                    r.metrics.overlap_ratio_pct if r.metrics else 0.0,
                    json.dumps(r.encroachment_polygon_geojson) if r.encroachment_polygon_geojson else None,
                    r.disclaimer,
                ),
            )

    conn.commit()


if __name__ == "__main__":
    init_db()
    print("Database initialized and seeded successfully.")
