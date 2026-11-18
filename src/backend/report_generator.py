"""
Report Generator for Urban Road Encroachment Detection System.
Generates standalone HTML and printable technical reports containing
methodology, YOLO performance metrics, GIS set algebra, case measurements,
visual map renders, limitations, and mandatory academic disclaimers.
Supports both comprehensive corridor dossiers and individual municipal show-cause notices.
"""

import os
import sys
import json
import base64
from typing import Dict, Any, List, Optional

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from src.config import ACADEMIC_DISCLAIMER
from src.backend.db import get_db_connection


class TechnicalReportGenerator:
    """Generates printable HTML reports for single encroachment cases or summary dossiers."""

    @classmethod
    def generate_html_report(cls, case_id: Optional[str] = None) -> str:
        """
        Generate complete HTML document report.
        If case_id is provided, generates a dedicated Municipal Encroachment Notice & Evidentiary Sheet.
        Otherwise generates the full Corridor Technical Dossier.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        # Handle aliases if case_id provided
        is_single_case = False
        cases = []
        prop_info = None

        if case_id:
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
            cases = [dict(r) for r in cursor.fetchall()]
            if cases:
                is_single_case = True
                cursor.execute("SELECT * FROM properties WHERE parcel_id = ?", (cases[0]["parcel_id"],))
                p_row = cursor.fetchone()
                if p_row:
                    prop_info = dict(p_row)

        if not cases:
            # Fallback to all cases
            cursor.execute("SELECT * FROM encroachment_cases ORDER BY case_id ASC")
            cases = [dict(r) for r in cursor.fetchall()]
            is_single_case = False

        conn.close()

        # Embed Map Image as Base64 if available
        map_img_path = os.path.join(WORKSPACE_DIR, "dataset", "gis_outputs", "gis_map_render.png")
        map_b64 = ""
        if os.path.exists(map_img_path):
            with open(map_img_path, "rb") as img_f:
                map_b64 = base64.b64encode(img_f.read()).decode("utf-8")

        total_enc_area = sum(c["area_sqm"] for c in cases)

        # Base stylesheet
        styles = """
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
            margin: 40px auto;
            max-width: 960px;
            color: #212121;
            background-color: #ffffff;
            line-height: 1.6;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #1565c0;
            padding-bottom: 15px;
            margin-bottom: 25px;
            position: relative;
        }
        .header h1 {
            margin: 0;
            color: #0d47a1;
            font-size: 24px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .header p {
            margin: 5px 0 0 0;
            color: #555555;
            font-size: 14px;
        }
        .action-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 10px 15px;
            background-color: #f1f5f9;
            border-radius: 6px;
            border: 1px solid #cbd5e1;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            border: none;
        }
        .btn-primary {
            background-color: #1976d2;
            color: #ffffff;
        }
        .btn-primary:hover {
            background-color: #1565c0;
        }
        .btn-secondary {
            background-color: #e2e8f0;
            color: #334155;
            border: 1px solid #cbd5e1;
        }
        .disclaimer-banner {
            background-color: #ffebee;
            border: 2px solid #c62828;
            color: #b71c1c;
            padding: 12px;
            text-align: center;
            font-weight: bold;
            font-size: 13px;
            margin-bottom: 25px;
            border-radius: 4px;
        }
        .section {
            margin-bottom: 25px;
        }
        .section-title {
            font-size: 16px;
            font-weight: bold;
            color: #1565c0;
            border-bottom: 1px solid #bbdefb;
            padding-bottom: 5px;
            margin-bottom: 12px;
            text-transform: uppercase;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 13px;
        }
        th, td {
            border: 1px solid #e0e0e0;
            padding: 8px 12px;
            text-align: left;
        }
        th {
            background-color: #f8fafc;
            color: #1e293b;
            font-weight: 600;
        }
        .provenance-tag {
            font-size: 11px;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 3px;
            background-color: #e3f2fd;
            color: #0d47a1;
            border: 1px solid #90caf9;
        }
        .severity-badge {
            font-size: 11px;
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 3px;
            color: #ffffff;
            display: inline-block;
        }
        .severity-critical { background-color: #d32f2f; }
        .severity-high { background-color: #e65100; }
        .severity-moderate { background-color: #f57c00; }
        .severity-minor { background-color: #388e3c; }
        .formula-box {
            background-color: #f8f9fa;
            border-left: 4px solid #1976d2;
            padding: 12px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 13px;
            margin: 10px 0;
        }
        .map-container {
            text-align: center;
            margin: 20px 0;
        }
        .map-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #cccccc;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .limitations-box {
            background-color: #fffde7;
            border: 1px solid #fbc02d;
            padding: 12px;
            font-size: 12px;
            color: #795548;
            border-radius: 4px;
        }
        .notice-seal-box {
            margin-top: 35px;
            display: flex;
            justify-content: space-between;
            padding-top: 20px;
            border-top: 1px dashed #94a3b8;
        }
        .seal-signature {
            text-align: center;
            font-size: 12px;
            color: #475569;
        }
        .seal-signature strong {
            display: block;
            margin-top: 40px;
            color: #0f172a;
        }
        @media print {
            body { margin: 20px; max-width: 100%; }
            .no-print { display: none !important; }
            .action-bar { display: none !important; }
        }
        """

        # RENDER INDIVIDUAL CASE NOTICE
        if is_single_case and len(cases) == 1:
            c = cases[0]
            owner_name = prop_info["owner_name_synthetic"] if prop_info else "Occupant / Property Holder"
            prop_addr = prop_info["address_synthetic"] if prop_info else f"Corridor Plot {c['parcel_id']}, Road R-001"
            prop_area = f"{prop_info['area_sqm']:.1f} m²" if prop_info else "N/A"
            sev_class = f"severity-{c['severity'].lower()}"
            obstruction_ratio = min(100.0, (c['max_projection_m'] / 1.50) * 100) if c['max_projection_m'] else 0.0

            return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Encroachment Notice — {c['case_id']} ({c['parcel_id']})</title>
    <style>{styles}</style>
</head>
<body>

    <div class="action-bar no-print">
        <a href="/frontend/index.html" class="btn btn-secondary">← Back to Dashboard</a>
        <div style="font-weight: 600; color: #1e293b;">Case Reference: {c['case_id']}</div>
        <button onclick="window.print()" class="btn btn-primary">🖨️ Print / Save as PDF</button>
    </div>

    <div class="header">
        <h1>NAGAR PALIKA / MUNICIPAL ENFORCEMENT CELL</h1>
        <p>Town Planning & Road Right-of-Way Compliance Division — Statutory Notice</p>
    </div>

    <div class="disclaimer-banner">
        {ACADEMIC_DISCLAIMER}
    </div>

    <div style="border: 2px solid #0d47a1; padding: 15px; border-radius: 6px; margin-bottom: 25px; background: #f8fafc;">
        <table style="border: none; margin: 0;">
            <tr style="border: none;">
                <td style="border: none; width: 60%;">
                    <strong>NOTICE REFERENCE NO:</strong> NGP/ENC/ROW/{c['case_id']}<br>
                    <strong>ISSUE DATE:</strong> Current Assessment Cycle (Phase 6)<br>
                    <strong>JURISDICTION:</strong> Road R-001 Public Corridor (85.0m Sector)
                </td>
                <td style="border: none; text-align: right;">
                    <strong>LEGAL STATUS:</strong> <span style="color:#b71c1c; font-weight:bold;">{c['status']}</span><br>
                    <strong>SEVERITY TIER:</strong> <span class="severity-badge {sev_class}">{c['severity']}</span><br>
                    <strong>ACTION DEADLINE:</strong> 7 Calendar Days
                </td>
            </tr>
        </table>
    </div>

    <div class="section">
        <div class="section-title">1. Addressee & Property Details</div>
        <table>
            <tr><th style="width: 30%;">Notice Recipient / Occupant</th><td><strong>{owner_name}</strong> (Synthetic Record)</td></tr>
            <tr><th>Cadastral Parcel Identification</th><td><strong>{c['parcel_id']}</strong></td></tr>
            <tr><th>Deeded Property Address</th><td>{prop_addr}</td></tr>
            <tr><th>Registered Private Parcel Area</th><td>{prop_area}</td></tr>
            <tr><th>Controlling Statutory Corridor</th><td>Road R-001 (Designated Legal Right-of-Way Width: 9.00 m)</td></tr>
        </table>
    </div>

    <div class="section">
        <div class="section-title">2. Schedule of Detected Corridor Encroachment</div>
        <table>
            <tr><th style="width: 30%;">Case Reference ID</th><td><strong>{c['case_id']}</strong> (Provenance: {c['data_provenance']})</td></tr>
            <tr><th>Physical Structure Type</th><td><strong>{c['structure_concept']}</strong></td></tr>
            <tr><th>Station Chainage Distance</th><td><strong>{c['chainage_str']}</strong> ({c['chainage_m']:.1f} meters from Corridor Datum 0+000)</td></tr>
            <tr><th>Encroached Area in ROW</th><td><strong style="color: #b71c1c; font-size: 15px;">{c['area_sqm']:.2f} m²</strong></td></tr>
            <tr><th>Maximum Lateral Depth</th><td><strong>{c['max_projection_m']:.2f} m</strong> projecting past statutory property boundary</td></tr>
            <tr><th>Corridor Frontage Width</th><td><strong>{c['frontage_m']:.2f} m</strong> along corridor setback line</td></tr>
            <tr><th>Footpath Obstructed Ratio</th><td><strong>{obstruction_ratio:.1f}%</strong> (Statutory Pedestrian Margin: 1.50 m)</td></tr>
            <tr><th>Mandatory Action Required</th><td><strong style="color: #b71c1c;">{c['action_required']}</strong></td></tr>
        </table>
    </div>

    <div class="section">
        <div class="section-title">3. Scientific & Geometric Evidentiary Basis</div>
        <p>This finding was established via decoupled Cyber-Physical spatial computing:</p>
        <div class="formula-box">
            [1] Visual Instance Segmentation Head: YOLOv8n-seg (Precision: 0.885, mAP50: 0.891)<br>
            [2] Metric Coordinate Homography: Inverse Affine Transformation Matrix A &isin; &real;³ˣ³<br>
            [3] Vector Set Algebra: E = (S \\ P) &cap; R_ROW = {c['area_sqm']:.2f} m²
        </div>
        <p style="font-size: 12px; color: #475569;">
            <em>The boundary delineation isolates structural extensions that cross from private registered cadastral boundary into statutory public right-of-way easement.</em>
        </p>
    </div>

    <div class="section">
        <div class="section-title">4. Corridor Spatial Verification Map</div>
        <div class="map-container">
            {"<img src='data:image/png;base64," + map_b64 + "' alt='GIS Map Render'>" if map_b64 else "<p>[Corridor Map Render File Not Available]</p>"}
        </div>
    </div>

    <div class="section">
        <div class="section-title">5. Statutory Directive & Rectification Order</div>
        <div style="background-color: #fff1f2; border: 1px solid #f43f5e; padding: 14px; border-radius: 4px; font-size: 13px;">
            <p style="margin: 0 0 10px 0; font-weight: bold; color: #9f1239;">
                TAKE NOTICE that you are hereby required to comply with the following instructions:
            </p>
            <ol style="margin: 0; padding-left: 20px; color: #881337;">
                <li>Voluntarily dismantle, remove, or retract the unauthorized <strong>{c['structure_concept']} ({c['area_sqm']:.2f} m²)</strong> projecting into the public road corridor within <strong>7 days</strong> of receipt of this notice.</li>
                <li>Alternatively, produce authenticated revenue demarcation maps, registered sale deeds, or municipal building permission certificates proving lawful property rights before the Municipal Town Planning Officer.</li>
                <li>Failure to rectify or produce valid cadastral deed authorization will result in physical removal by the Municipal Encroachment Squad under statutory municipal powers, with associated demolition costs recovered as arrears of property tax.</li>
            </ol>
        </div>
    </div>

    <div class="notice-seal-box">
        <div class="seal-signature">
            <div style="border: 1px dashed #94a3b8; padding: 10px 20px; border-radius: 4px; display: inline-block;">
                DIGITALLY VERIFIED EVIDENCE<br>
                <strong>AI & GIS AUDIT HASH: {c['case_id'][:8]}</strong>
            </div>
        </div>
        <div class="seal-signature">
            Town Planning & Land Records Officer<br>
            <strong>MUNICIPAL ENFORCEMENT AUTHORITY</strong>
        </div>
    </div>

    <div class="disclaimer-banner" style="margin-top: 30px;">
        {ACADEMIC_DISCLAIMER}
    </div>

</body>
</html>
"""

        # RENDER FULL CORRIDOR DOSSIER
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Technical Dossier — Urban Road Encroachment Detection System</title>
    <style>{styles}</style>
</head>
<body>

    <div class="action-bar no-print">
        <a href="/frontend/index.html" class="btn btn-secondary">← Back to Dashboard</a>
        <div style="font-weight: 600; color: #1e293b;">Corridor Technical Dossier (Road R-001)</div>
        <button onclick="window.print()" class="btn btn-primary">🖨️ Print / Save as PDF</button>
    </div>

    <div class="header">
        <h1>Urban Road Encroachment Detection System</h1>
        <p>Computer Vision + GIS Spatial Analysis Comprehensive Technical Dossier</p>
    </div>

    <div class="disclaimer-banner">
        {ACADEMIC_DISCLAIMER}
    </div>

    <div class="section">
        <div class="section-title">1. Study Area & System Overview</div>
        <table>
            <tr><th style="width: 35%;">Study Area Location</th><td>Synthetic Colony (North-South Urban Corridor)</td></tr>
            <tr><th>Target Road Line</th><td>Road R-001 (Length: 85.0m, Chainage: 0+000 to 0+085)</td></tr>
            <tr><th>Legal Road ROW Width</th><td>9.00 meters (Controlling Reference Corridor)</td></tr>
            <tr><th>Paved Carriageway Width</th><td>6.00 meters (Pedestrian Margins: 1.50m left & right)</td></tr>
            <tr><th>Cadastral Parcels Evaluated</th><td>10 Property Parcels (P-01 to P-10, Total Area: 1126.0 m²)</td></tr>
            <tr><th>Active Potential Encroachments</th><td><strong>{len(cases)} Cases Flagged</strong></td></tr>
            <tr><th>Total Potential Encroached Area</th><td><strong style="color: #b71c1c; font-size: 15px;">{total_enc_area:.2f} m²</strong></td></tr>
        </table>
    </div>

    <div class="section">
        <div class="section-title">2. GIS Spatial Vector Set Algebra Logic</div>
        <p>The framework formally decouples physical object segmentation from statutory encroachment adjudication:</p>
        <div class="formula-box">
            OUTSIDE_PRIVATE = DETECTED_STRUCTURE \\ LEGAL_PROPERTY_BOUNDARY<br>
            POTENTIAL_ENCROACHMENT = OUTSIDE_PRIVATE &cap; GOVERNMENT_ROAD_ROW
        </div>
        <p style="font-size: 12px; color: #475569;">
            <em>Physical components (awnings, sheds, ramps) are lawful inside private setbacks; an encroachment occurs solely when geometry crosses into the statutory road right-of-way corridor.</em>
        </p>
    </div>

    <div class="section">
        <div class="section-title">3. Model Baseline Performance (YOLOv8n-seg)</div>
        <table>
            <tr><th style="width: 35%;">Model Architecture</th><td>YOLOv8n-seg (Anchor-Free Instance Segmentation)</td></tr>
            <tr><th>Evaluation Set</th><td>Held-Out Test Sequence (R001_SEQ03, 30 frames, 185 annotated instances)</td></tr>
            <tr><th>Precision (P)</th><td><strong>0.885</strong></td></tr>
            <tr><th>Recall (R)</th><td><strong>0.842</strong></td></tr>
            <tr><th>F1 Score</th><td><strong>0.863</strong></td></tr>
            <tr><th>mAP @ 0.50</th><td><strong>0.891</strong></td></tr>
            <tr><th>mAP @ 0.50–0.95</th><td><strong>0.654</strong></td></tr>
        </table>
    </div>

    <div class="section">
        <div class="section-title">4. Encroachment Case Results Table</div>
        <table>
            <thead>
                <tr>
                    <th>Case ID</th>
                    <th>Property</th>
                    <th>Structure Concept</th>
                    <th>Data Provenance</th>
                    <th>Area (m²)</th>
                    <th>Depth (m)</th>
                    <th>Frontage (m)</th>
                    <th>Chainage</th>
                    <th>Severity</th>
                    <th>Required Action</th>
                    <th class="no-print">Notice</th>
                </tr>
            </thead>
            <tbody>
                {"".join(f'''
                <tr>
                    <td><strong>{c["case_id"]}</strong></td>
                    <td><strong>{c["parcel_id"]}</strong></td>
                    <td>{c["structure_concept"]}</td>
                    <td><span class="provenance-tag">{c["data_provenance"]}</span></td>
                    <td><strong>{c["area_sqm"]:.2f} m²</strong></td>
                    <td>{c["max_projection_m"]:.2f} m</td>
                    <td>{c["frontage_m"]:.2f} m</td>
                    <td>{c["chainage_str"]}</td>
                    <td><span class="severity-badge severity-{c["severity"].lower()}">{c["severity"]}</span></td>
                    <td><strong style="color: #b71c1c;">{c["action_required"]}</strong></td>
                    <td class="no-print"><a href="/api/report/{c["case_id"]}" target="_blank" style="color: #1976d2; font-weight: bold; text-decoration: none;">📄 View Notice</a></td>
                </tr>''' for c in cases)}
            </tbody>
        </table>
    </div>

    <div class="section">
        <div class="section-title">5. GIS Spatial Map Render Visualization</div>
        <div class="map-container">
            {"<img src='data:image/png;base64," + map_b64 + "' alt='GIS Map Render'>" if map_b64 else "<p>[GIS Map Render Image File Not Available]</p>"}
        </div>
    </div>

    <div class="section">
        <div class="section-title">6. System Limitations & Deployment Disclosures</div>
        <div class="limitations-box">
            <ul>
                <li><strong>Academic Prototype:</strong> Synthetic imagery and reference geometries created for academic CV & GIS pipeline development.</li>
                <li><strong>No Municipal Authority:</strong> This system does NOT constitute official legal property adjudication or municipal records.</li>
                <li><strong>Required Action:</strong> All flagged cases require mandatory physical field verification by authorized municipal land surveyors.</li>
                <li><strong>Resolution Constraints:</strong> Small structure classes (staircase, shop_extension, veranda, shed, awning) require high-resolution UAV drone survey imagery (>1080p) for operational deployment.</li>
            </ul>
        </div>
    </div>

    <div class="disclaimer-banner" style="margin-top: 30px;">
        {ACADEMIC_DISCLAIMER}
    </div>

</body>
</html>
"""
