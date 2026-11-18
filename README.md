# Urban Road Encroachment Detection System
### Computer Vision + GIS Decision-Support Prototype Application

**System Classification**: ACADEMIC DECISION-SUPPORT PROTOTYPE — NOT AN OFFICIAL MUNICIPAL RECORD  
**Project Status**: Phase 1 to Phase 6 COMPLETE (Final System Deliverable)

---

## 1. Executive Summary & Purpose

The **Urban Road Encroachment Detection System** integrates deep learning computer vision (YOLOv8n-seg instance segmentation) with Geographic Information System (GIS) vector set algebra to detect physical structures from aerial/drone imagery, evaluate their spatial relationship against legal cadastral parcel boundaries and government Road Right-of-Way (ROW) corridors, and report potential road ROW encroachments for physical field verification.

The application serves as an **academic decision-support prototype**. It is **NOT** an official municipal legal adjudication system.

---

## 2. Core Scientific Principles

### Decoupled Architecture
1. **Computer Vision Layer**: "What physical structure is detected?" (`building`, `ramp`, `compound_wall`)
2. **GIS Engine Layer**: "Where is the structure relative to legal property boundaries and road ROW?"
3. **Decision Support Layer**: "Does the spatial overlap indicate a POTENTIAL ROAD ROW ENCROACHMENT requiring field verification?"

### Vector Set Algebra Formula
$$O = S \setminus P \quad (\text{outside\_private} = \text{detected\_structure} \setminus \text{legal\_property\_boundary})$$
$$E = O \cap R \quad (\text{potential\_encroachment} = \text{outside\_private} \cap \text{government\_road\_ROW})$$

---

## 3. Phase Accomplishments Summary

- **Phase 1 — System Architecture & Data Schemas**: Established modular directory structure, Pydantic schemas, coordinate transformer, GIS spatial engine, and validator.
- **Phase 2 — Drone Frame Ingestion**: Extracted 90 synthetic individual frame files from 3 storyboard survey montages (`R001_SEQ01` TRAIN, `R001_SEQ02` VAL, `R001_SEQ03` TEST).
- **Phase 3 — Annotation & Quality Control**: Prepared 551 polygon instances across 90 images, audited ground-truth instances, performed human review priority queue processing (420 approved, 60 corrected, 27 rejected).
- **Phase 4 — YOLO Instance Segmentation**: Evaluated 8-class sufficiency disclosure (5 classes had 0 verified instances), trained baseline `YOLOv8n-seg` model on verified classes (`building`, `ramp`, `compound_wall`). Held-out test evaluation on `R001_SEQ03`: Precision = **0.885**, Recall = **0.842**, F1 = **0.863**, mAP50 = **0.891**, mAP50-95 = **0.654**.
- **Phase 5 — GIS Spatial Analysis**: Created master GeoJSON layers (`01_PROPERTY_BOUNDARY`, `02_ROAD_ROW`, `03_ROAD_CENTERLINE`, `04_EXISTING_CARRIAGEWAY`, `09_CHAINAGE`), executed set algebra on synthetic reference benchmark cases E-01 (Parcel P-07: $6.00\,\text{m}^2$) and E-02 (Parcel P-09: $3.60\,\text{m}^2$), generated map renders, CSV export, and GeoJSON layer export.
- **Phase 6 — Backend, Dashboard & Reporting**: Developed FastAPI REST API, SQLite academic database, Leaflet.js interactive decision-support web dashboard, HTML/PDF report generator, API security, and full 73-test pytest suite.

---

## 4. REST API Specification

- `GET /api/health`: System status & academic classification
- `GET /api/study-area`: Study area metadata (Colony R-001, legal ROW 9.0m, carriageway 6.0m)
- `GET /api/properties`: Cadastral property parcels list and GeoJSON geometry (P-01 to P-10)
- `GET /api/roads`: Road master corridor information & ROW parameters
- `GET /api/detections`: Physical structure detections & YOLO baseline info
- `GET /api/encroachments`: Filterable encroachment cases list
- `GET /api/encroachments/{id}`: Single case detail view
- `GET /api/summary`: Summary dashboard metrics
- `GET /api/metrics`: Phase 4 YOLOv8n-seg baseline test metrics
- `GET /api/layers/{layer_name}`: Serves raw GeoJSON layers
- `POST /api/analyze`: Executes GIS spatial set algebra on custom detection geometry payload
- `POST /api/upload`: Secure file upload endpoint (max size 10MB)
- `GET /api/export/csv`: Downloads `encroachment_results.csv`
- `GET /api/export/geojson`: Downloads `08_POTENTIAL_ENCROACHMENT.geojson`
- `GET /api/report`: Renders standalone HTML / printable PDF technical report

---

## 5. Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- Installed packages: `fastapi`, `uvicorn`, `jinja2`, `shapely`, `pydantic`, `pytest`, `ultralytics`, `torch`, `matplotlib`, `python-multipart`

### 2. Start Application Server
```bash
uvicorn src.backend.app:app --host 127.0.0.1 --port 8000
```

### 3. Open Web Dashboard
Open your browser and navigate to:
```
http://127.0.0.1:8000/frontend/index.html
```

### 4. Run Test Suite
```bash
pytest tests/ -v
```

---

## 6. End-to-End Demonstration Workflow

1. **Launch Web Dashboard**: Open `http://127.0.0.1:8000/frontend/index.html`.
2. **Review Academic Banner**: Note mandatory disclaimer: `SYNTHETIC / ACADEMIC PROTOTYPE — NOT AN OFFICIAL MUNICIPAL RECORD`.
3. **Inspect Interactive GIS Map**: Toggle layers (Parcels, ROW, Carriageway, Centerline, Chainage, Encroachments) and click features to view metadata.
4. **Filter Encroachment Cases Table**: Search by parcel (e.g. `P-07`), severity (`HIGH`), or provenance (`SYNTHETIC_GIS_REFERENCE_BENCHMARK`).
5. **Inspect Single Case Detail**: View spatial set algebra breakdown ($O = S \setminus P$, $E = O \cap R$), depth ($1.20\text{m}$), frontage ($5.00\text{m}$), chainage (`0+011.0`), and action flag (`FIELD VERIFICATION REQUIRED`).
6. **Review Model / AI Metrics**: View Phase 4 baseline YOLOv8n-seg test set metrics ($P=0.885, R=0.842, \text{mAP50}=0.891$) and visual prediction overlay gallery.
7. **Inspect Reference Benchmarks**: View separated E-01 and E-02 reference benchmark section with explicit provenance disclosures.
8. **Export Data & Generate Reports**: Download `encroachment_results.csv`, `08_POTENTIAL_ENCROACHMENT.geojson`, and click `Generate Report` for a printable HTML dossier.

---

## 7. Operational Limitations & Disclaimers

> `SYNTHETIC / ACADEMIC PROTOTYPE — NOT AN OFFICIAL MUNICIPAL RECORD`  
> - **Synthetic Dataset**: Drone imagery frames and cadastral parcel geometries are synthetic academic prototypes.
> - **Resolution Limitation**: Small structure classes (`staircase`, `shop_extension`, `veranda`, `shed`, `awning`) require high-resolution UAV drone survey imagery (>1080p) for operational deployment.
> - **Required Action**: All output cases represent potential encroachments requiring physical field survey verification by authorized municipal land surveyors.
