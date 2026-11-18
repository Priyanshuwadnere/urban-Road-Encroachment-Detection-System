# Phase 6 — Backend, Dashboard & Reporting Documentation

**Project**: Urban Road Encroachment Detection System  
**System Classification**: ACADEMIC DECISION-SUPPORT PROTOTYPE — NOT AN OFFICIAL MUNICIPAL RECORD  
**Phase Status**: Phase 6 COMPLETE (Final Major Project Phase)

---

## 1. System Architecture & Component Design

The Urban Road Encroachment Detection System decouples physical structure detection (Computer Vision) from legal property and road corridor boundary analysis (GIS) and decision support:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND DASHBOARD (Leaflet / Web UI)                   │
│   - Interactive Map (Layers, Legend, Click Popups)                          │
│   - Encroachment Case Table & Case Details Modal                           │
│   - Model AI Metrics & Visual Prediction Viewer                             │
│   - GIS Math Logic & Synthetic Reference Benchmark View (E-01 / E-02)        │
│   - Property & Road Explorers, System Architecture Flowchart                │
│   - CSV, GeoJSON & HTML/PDF Report Exporters                                │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │ HTTP / REST API (JSON / GeoJSON / Files)
┌────────────────────────────────────▼────────────────────────────────────────┐
│                        FASTAPI BACKEND REST API                             │
│   - GET /api/health, /api/study-area, /api/properties, /api/roads          │
│   - GET /api/detections, /api/encroachments, /api/encroachments/{id}        │
│   - GET /api/summary, /api/metrics, /api/layers/{layer_name}               │
│   - POST /api/analyze, POST /api/upload                                    │
│   - GET /api/export/csv, /api/export/geojson, GET /api/report/{id}         │
└──────────────────┬──────────────────────────────────────┬───────────────────┘
                   │                                      │
┌──────────────────▼───────────────────┐  ┌───────────────▼───────────────────┐
│     SQLITE ACADEMIC DATABASE         │  │  GIS SPATIAL ENGINE & REFERENCE   │
│  (database/encroachment_system.db)   │  │  LAYERS (dataset/gis_layers/)     │
└──────────────────────────────────────┘  └───────────────────────────────────┘
```

---

## 2. Mathematical Set Algebra Logic

$$O = S \setminus P \quad (\text{outside\_private} = \text{detected\_structure} \setminus \text{legal\_property\_boundary})$$
$$E = O \cap R \quad (\text{potential\_encroachment} = \text{outside\_private} \cap \text{government\_road\_ROW})$$

- **Physical Object Detections**: YOLO identifies physical structures (`building`, `ramp`, `compound_wall`). YOLO does **NOT** detect "encroachment".
- **GIS Set Algebra**: Evaluates spatial overlap between private structure geometry and government Road Right-of-Way.
- **Decision Status**: Formatted explicitly as `"POTENTIAL ROAD ROW ENCROACHMENT"` with required action flag `"FIELD VERIFICATION REQUIRED"`.

---

## 3. Backend REST API Specification (`src/backend/app.py`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System health check and academic classification metadata |
| `GET` | `/api/study-area` | Study area parameters (Road R-001, legal ROW 9.0m, carriageway 6.0m) |
| `GET` | `/api/properties` | Cadastral property parcels list and GeoJSON geometry (P-01 to P-10) |
| `GET` | `/api/roads` | Road master information, ROW polygon, centerline LineString, carriageway |
| `GET` | `/api/detections` | Physical structure detections list & YOLOv8n-seg baseline info |
| `GET` | `/api/encroachments` | Encroachment cases list (supports `parcel_id`, `road_id`, `class_name`, `severity`, `status`, `data_provenance` filters) |
| `GET` | `/api/encroachments/{id}` | Single encroachment case details |
| `GET` | `/api/summary` | Summary dashboard metrics |
| `GET` | `/api/metrics` | Phase 4 YOLOv8n-seg baseline test performance metrics ($P=0.885, R=0.842, F_1=0.863, \text{mAP50}=0.891, \text{mAP50-95}=0.654$) |
| `GET` | `/api/layers/{layer_name}` | Serves raw GeoJSON layer files (`01_PROPERTY_BOUNDARY`, `02_ROAD_ROW`, `03_ROAD_CENTERLINE`, `04_EXISTING_CARRIAGEWAY`, `08_POTENTIAL_ENCROACHMENT`, `09_CHAINAGE`) |
| `POST` | `/api/analyze` | Executes Phase 5 GIS spatial set algebra on custom detection geometry payload |
| `POST` | `/api/upload` | Secure file upload endpoint (max size 10MB, safe filename checks) |
| `GET` | `/api/export/csv` | Downloads `encroachment_results.csv` |
| `GET` | `/api/export/geojson` | Downloads `08_POTENTIAL_ENCROACHMENT.geojson` |
| `GET` | `/api/report` | Renders standalone HTML / printable PDF technical report |

---

## 4. Synthetic Reference Benchmark Disclosures (E-01 & E-02)

Cases E-01 and E-02 are **PURELY SYNTHETIC GIS REFERENCE BENCHMARK GEOMETRIES** created to validate spatial set algebra algorithms. They are **NOT** YOLO model predictions.

- **E-01**: Parcel P-07, concept `staircase / shop-side extension`, Area = $6.00\,\text{m}^2$, Depth = $1.20\,\text{m}$, Frontage = $5.00\,\text{m}$, Chainage = `0+011.0`.
- **E-02**: Parcel P-09, concept `veranda / shop-extension`, Area = $3.60\,\text{m}^2$, Depth = $0.80\,\text{m}$, Frontage = $4.50\,\text{m}$, Chainage = `0+023.3`.
- **Total Benchmark Area**: $9.60\,\text{m}^2$.

---

## 5. Security & Data Validation

- Input payload validation using Pydantic schemas (`DetectedObjectGISRecord`, `Phase5EncroachmentResult`).
- CORS middleware restricted safely.
- File upload restrictions: max 10MB size limit and extension whitelist (`.geojson`, `.json`, `.csv`, `.jpg`, `.png`).
- Safe file pathing: no arbitrary filesystem access or path traversal.

---

## 6. How to Run the Application

### Installation & Server Startup

1. **Start Backend Server**:
   ```bash
   uvicorn src.backend.app:app --host 127.0.0.1 --port 8000
   ```
2. **Access Web Dashboard**:
   Open browser at: `http://127.0.0.1:8000/frontend/index.html`

### Running Test Suite
```bash
pytest tests/ -v
```
Output:
```
============================== 73 passed in 4.98s ==============================
```

---

## 7. Mandatory Academic Disclaimer

> `SYNTHETIC / ACADEMIC PROTOTYPE — NOT AN OFFICIAL MUNICIPAL RECORD`  
> All output reports, maps, and API data are synthetic academic prototypes. Flagged potential encroachments require mandatory physical field verification by authorized municipal land surveyors.
