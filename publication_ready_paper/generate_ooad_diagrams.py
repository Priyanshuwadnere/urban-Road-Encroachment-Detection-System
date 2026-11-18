import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

out_dir = Path(r"e:\Urban Road Encroachment Detection System\publication_ready_paper\figures")
out_dir.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. USE CASE DIAGRAM
# -------------------------------------------------------------
def generate_use_case_diagram():
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # System boundary box
    rect = patches.FancyBboxPatch((2.6, 0.4), 6.8, 7.2, boxstyle="round,pad=0.1",
                                  ec="#1A365D", fc="#F7FAFC", lw=2, linestyle='--')
    ax.add_patch(rect)
    ax.text(6.0, 7.3, "Urban Road Encroachment Detection System (Boundary)",
            ha='center', va='center', fontsize=12, fontweight='bold', color="#1A365D")

    # Actors
    actors = [
        {"name": "Municipal\nSurveyor", "pos": (1.0, 6.0), "icon_y": 6.3},
        {"name": "GIS Spatial\nAnalyst", "pos": (1.0, 2.5), "icon_y": 2.8},
        {"name": "Enforcement\nSquad", "pos": (11.0, 5.5), "icon_y": 5.8},
        {"name": "System\nAdministrator", "pos": (11.0, 2.0), "icon_y": 2.3},
    ]

    for act in actors:
        x, y = act["pos"]
        iy = act["icon_y"]
        # draw stick figure
        ax.plot(x, iy + 0.35, 'o', color="#2B6CB0", markersize=14)
        ax.plot([x, x], [iy + 0.25, iy - 0.15], color="#2B6CB0", lw=2)
        ax.plot([x - 0.2, x + 0.2], [iy + 0.1, iy + 0.1], color="#2B6CB0", lw=2)
        ax.plot([x, x - 0.2], [iy - 0.15, iy - 0.45], color="#2B6CB0", lw=2)
        ax.plot([x, x + 0.2], [iy - 0.15, iy - 0.45], color="#2B6CB0", lw=2)
        ax.text(x, y - 0.8, act["name"], ha='center', va='center', fontsize=9.5, fontweight='bold', color="#2D3748")

    # Use cases (ellipses)
    use_cases = [
        {"id": "UC1", "text": "Upload Orthophoto\n& Cadastral Data", "pos": (4.5, 6.4), "actor_left": 0},
        {"id": "UC2", "text": "Configure Statutory\nROW & Calibration", "pos": (7.5, 6.4), "actor_left": 0},
        {"id": "UC3", "text": "Execute YOLOv8n-seg\nDeep Segmentation", "pos": (4.5, 4.8), "actor_left": 1},
        {"id": "UC4", "text": "Run Spatial Set Algebra\n& Violation Attribution", "pos": (7.5, 4.8), "actor_left": 1},
        {"id": "UC5", "text": "Inspect Metric Severity\n& Linear Chainage", "pos": (4.5, 3.2), "actor_right": 0},
        {"id": "UC6", "text": "Generate Evidentiary\nLegal Notice (PDF)", "pos": (7.5, 3.2), "actor_right": 0},
        {"id": "UC7", "text": "Manage Cadastre Master\n& System Audit Logs", "pos": (6.0, 1.4), "actor_right": 1},
    ]

    for uc in use_cases:
        ux, uy = uc["pos"]
        ellipse = patches.Ellipse((ux, uy), 2.4, 0.95, ec="#2B6CB0", fc="#EDF2F7", lw=1.5)
        ax.add_patch(ellipse)
        ax.text(ux, uy, uc["text"], ha='center', va='center', fontsize=8.5, fontweight='semibold', color="#1A202C")

    # Connect lines
    lines = [
        ((1.0, 6.0), (3.3, 6.4)),   # Surveyor -> UC1
        ((1.0, 6.0), (6.3, 6.4)),   # Surveyor -> UC2
        ((1.0, 2.5), (3.3, 4.8)),   # Analyst -> UC3
        ((1.0, 2.5), (6.3, 4.8)),   # Analyst -> UC4
        ((1.0, 2.5), (3.3, 3.2)),   # Analyst -> UC5
        ((11.0, 5.5), (8.7, 3.2)),  # Enforcement -> UC6
        ((11.0, 5.5), (5.7, 3.2)),  # Enforcement -> UC5
        ((11.0, 2.0), (7.2, 1.4)),  # Admin -> UC7
    ]
    for start, end in lines:
        ax.plot([start[0], end[0]], [start[1], end[1]], color="#718096", lw=1.2)

    # <<include>> line between UC3 and UC4
    ax.annotate("", xy=(6.3, 4.8), xytext=(5.7, 4.8),
                arrowprops=dict(arrowstyle="->", color="#C53030", lw=1.2, ls="--"))
    ax.text(6.0, 5.05, "<<include>>", ha='center', va='center', fontsize=7, color="#C53030", fontweight='bold')

    plt.tight_layout()
    plt.savefig(out_dir / "use_case_diagram.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated use_case_diagram.png")

# -------------------------------------------------------------
# 2. CLASS DIAGRAM
# -------------------------------------------------------------
def generate_class_diagram():
    fig, ax = plt.subplots(figsize=(13, 8.5), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    classes = [
        {
            "title": "YOLOSegmentor",
            "pos": (0.5, 5.5), "w": 3.4, "h": 2.6,
            "attrs": ["- model_path: str", "- conf_threshold: float = 0.0016", "- input_size: Tuple[int, int]"],
            "methods": ["+ load_model(): void", "+ letterbox(img: Mat): Tuple", "+ predict(img: Mat): List[Detection]", "+ postprocess(preds: Any): Mask"]
        },
        {
            "title": "CoordinateTransformer",
            "pos": (4.5, 5.5), "w": 3.8, "h": 2.6,
            "attrs": ["- affine_matrix: Matrix3x3", "- crs_target: str = 'EPSG:32643'", "- scale_ratio: float"],
            "methods": ["+ pixel_to_metric(poly: Polygon): Polygon", "+ metric_to_pixel(poly: Polygon): Polygon", "+ inverse_letterbox(coords): Polygon"]
        },
        {
            "title": "SpatialEngine",
            "pos": (9.0, 5.5), "w": 3.5, "h": 2.6,
            "attrs": ["- rtree_index: STRtree", "- min_area_threshold: float = 0.10", "- frontage_tolerance: float = 0.05"],
            "methods": ["+ associate_parcel(s: Polygon): Parcel", "+ compute_difference(s, p): Polygon", "+ extract_row_breach(d, r): Polygon", "+ compute_attribution(e, p, l): Dict"]
        },
        {
            "title": "CadastralParcel",
            "pos": (0.5, 1.2), "w": 3.4, "h": 3.0,
            "attrs": ["+ parcel_id: str", "+ owner_name: str", "+ statutory_area_sqm: float", "+ geometry_metric: Polygon"],
            "methods": ["+ get_boundary(): LineString", "+ get_centroid(): Point", "+ intersects(other): bool"]
        },
        {
            "title": "EncroachmentRecord",
            "pos": (4.5, 1.2), "w": 3.8, "h": 3.0,
            "attrs": ["+ case_id: str", "+ parcel_id: str", "+ structure_class: str", "+ area_sqm: float", "+ frontage_m: float", "+ max_projection_m: float", "+ chainage_station: str", "+ severity_tier: str"],
            "methods": ["+ to_dict(): Dict", "+ to_geojson(): str", "+ get_legal_status(): str"]
        },
        {
            "title": "DatabaseManager",
            "pos": (9.0, 1.2), "w": 3.5, "h": 3.0,
            "attrs": ["- db_path: Path", "- connection_pool: Any", "- is_connected: bool"],
            "methods": ["+ store_detection(det: Dict): void", "+ persist_case(rec: Encroachment): void", "+ query_case_by_id(id: str): Dict", "+ write_audit_log(act, det): void"]
        }
    ]

    for c in classes:
        x, y = c["pos"]
        w, h = c["w"], c["h"]
        # Outer box
        rect = patches.Rectangle((x, y), w, h, ec="#2B6CB0", fc="#FFFFFF", lw=1.5)
        ax.add_patch(rect)
        # Header banner
        header = patches.Rectangle((x, y + h - 0.55), w, 0.55, ec="#2B6CB0", fc="#2B6CB0", lw=1.5)
        ax.add_patch(header)
        ax.text(x + w / 2, y + h - 0.28, c["title"], ha='center', va='center',
                fontsize=9.5, fontweight='bold', color="#FFFFFF")

        # Attributes
        curr_y = y + h - 0.75
        for attr in c["attrs"]:
            ax.text(x + 0.12, curr_y, attr, ha='left', va='center', fontsize=7.5, fontfamily='monospace', color="#2D3748")
            curr_y -= 0.24

        # Divider
        ax.plot([x, x + w], [curr_y - 0.05, curr_y - 0.05], color="#CBD5E0", lw=1)
        curr_y -= 0.22

        # Methods
        for m in c["methods"]:
            ax.text(x + 0.12, curr_y, m, ha='left', va='center', fontsize=7.5, fontfamily='monospace', color="#1A202C")
            curr_y -= 0.24

    # Connectors
    # YOLOSegmentor -> CoordinateTransformer
    ax.annotate("", xy=(4.5, 6.8), xytext=(3.9, 6.8),
                arrowprops=dict(arrowstyle="->", color="#4A5568", lw=1.5))
    # CoordinateTransformer -> SpatialEngine
    ax.annotate("", xy=(9.0, 6.8), xytext=(8.3, 6.8),
                arrowprops=dict(arrowstyle="->", color="#4A5568", lw=1.5))
    # SpatialEngine -> EncroachmentRecord (dependency / instantiation)
    ax.annotate("", xy=(6.4, 4.2), xytext=(10.2, 5.5),
                arrowprops=dict(arrowstyle="->", color="#C53030", lw=1.5, ls="--"))
    ax.text(8.5, 4.8, "<<creates>>", ha='center', va='center', fontsize=7.5, color="#C53030", fontweight='bold')
    # CadastralParcel -> SpatialEngine (aggregation)
    ax.annotate("", xy=(9.5, 5.5), xytext=(2.5, 4.2),
                arrowprops=dict(arrowstyle="->", color="#4A5568", lw=1.5))
    ax.text(4.2, 4.9, "1..* aggregates", ha='center', va='center', fontsize=7.5, color="#4A5568")
    # EncroachmentRecord -> DatabaseManager
    ax.annotate("", xy=(9.0, 2.7), xytext=(8.3, 2.7),
                arrowprops=dict(arrowstyle="->", color="#4A5568", lw=1.5))
    ax.text(8.65, 2.9, "persists", ha='center', va='center', fontsize=7.5, color="#4A5568")

    plt.tight_layout()
    plt.savefig(out_dir / "class_diagram.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated class_diagram.png")

# -------------------------------------------------------------
# 3. SEQUENCE DIAGRAM
# -------------------------------------------------------------
def generate_sequence_diagram():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')

    lifelines = [
        {"name": "Client / UI", "x": 1.2},
        {"name": "API Gateway\n(FastAPI)", "x": 3.4},
        {"name": "YOLOSegmentor\n(Vision Model)", "x": 5.6},
        {"name": "SpatialEngine\n(GEOS / Shapely)", "x": 8.0},
        {"name": "Database\n(SQLite / GIS)", "x": 10.4},
    ]

    # Draw header boxes and lifelines
    for ll in lifelines:
        x = ll["x"]
        rect = patches.FancyBboxPatch((x - 0.9, 6.7), 1.8, 0.65, boxstyle="round,pad=0.05",
                                      ec="#2B6CB0", fc="#2B6CB0")
        ax.add_patch(rect)
        ax.text(x, 7.02, ll["name"], ha='center', va='center', fontsize=8, fontweight='bold', color="#FFFFFF")
        # Lifeline dash
        ax.plot([x, x], [0.6, 6.7], color="#A0AEC0", linestyle="--", lw=1.2)

    messages = [
        {"y": 6.2, "from": 1.2, "to": 3.4, "label": "1. POST /api/pipeline/run (image, cadastre)", "ret": False},
        {"y": 5.7, "from": 3.4, "to": 5.6, "label": "2. predict(image_norm, conf=0.0016)", "ret": False},
        {"y": 5.2, "from": 5.6, "to": 3.4, "label": "3. return masks & confidence scores", "ret": True},
        {"y": 4.6, "from": 3.4, "to": 8.0, "label": "4. process_encroachment(masks, cadastre, ROW)", "ret": False},
        {"y": 4.1, "from": 8.0, "to": 8.0, "label": "5. Affine transform & R-tree parent matching", "self": True},
        {"y": 3.6, "from": 8.0, "to": 8.0, "label": "6. Boolean diff (S \ P) & ROW intersection", "self": True},
        {"y": 3.0, "from": 8.0, "to": 8.0, "label": "7. Metric attribution (depth, frontage, chainage)", "self": True},
        {"y": 2.4, "from": 8.0, "to": 10.4, "label": "8. persist_cases(E_cases) & write_audit_log()", "ret": False},
        {"y": 1.9, "from": 10.4, "to": 8.0, "label": "9. ACK: commit OK", "ret": True},
        {"y": 1.4, "from": 8.0, "to": 3.4, "label": "10. return structured violation records", "ret": True},
        {"y": 0.9, "from": 3.4, "to": 1.2, "label": "11. 200 OK: JSON compliance payload & GeoJSON", "ret": True},
    ]

    for msg in messages:
        y = msg["y"]
        x1 = msg["from"]
        x2 = msg["to"]
        is_ret = msg.get("ret", False)
        is_self = msg.get("self", False)

        if is_self:
            # Self arrow loop
            ax.annotate("", xy=(x1 + 0.05, y - 0.22), xytext=(x1 + 0.05, y),
                        arrowprops=dict(arrowstyle="->", color="#2B6CB0", lw=1.2, connectionstyle="arc,angleA=0,armA=30,rad=10"))
            ax.text(x1 + 0.45, y - 0.1, msg["label"], ha='left', va='center', fontsize=7.5, color="#2D3748")
        else:
            style = "->"
            ls = "--" if is_ret else "-"
            col = "#2B6CB0" if not is_ret else "#319795"
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle=style, color=col, lw=1.3, linestyle=ls))
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, y + 0.14, msg["label"], ha='center', va='center', fontsize=7.5, fontweight='semibold', color="#1A202C")

    plt.tight_layout()
    plt.savefig(out_dir / "sequence_diagram.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated sequence_diagram.png")

# -------------------------------------------------------------
# 4. ACTIVITY DIAGRAM
# -------------------------------------------------------------
def generate_activity_diagram():
    fig, ax = plt.subplots(figsize=(10, 8.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Start node
    ax.plot(5.0, 8.1, 'o', color="#1A202C", markersize=14)
    ax.text(5.0, 8.35, "Start Analysis Pipeline", ha='center', va='center', fontsize=9, fontweight='bold')

    nodes = [
        {"y": 7.4, "text": "Acquire Orthophoto & Vector Cadastral Boundaries"},
        {"y": 6.6, "text": "Letterbox Preprocessing (192x192) & YOLOv8n-seg Inference"},
        {"y": 5.8, "text": "Inverse Letterbox Mapping & Metric Affine Transformation"},
        {"y": 5.0, "text": "R-tree Spatial Search & Maximum Cadastral Parcel Association"},
        {"y": 4.2, "text": "Perform Boolean Set Difference: Out-of-Bounds O = S \ P"},
        {"y": 3.4, "text": "Intersect with Statutory Road ROW: Breach E = O ∩ R_ROW"},
    ]

    prev_y = 8.1
    for node in nodes:
        y = node["y"]
        rect = patches.FancyBboxPatch((1.8, y - 0.28), 6.4, 0.56, boxstyle="round,pad=0.08",
                                      ec="#2B6CB0", fc="#EDF2F7", lw=1.3)
        ax.add_patch(rect)
        ax.text(5.0, y, node["text"], ha='center', va='center', fontsize=8.5, fontweight='semibold', color="#1A202C")
        ax.annotate("", xy=(5.0, y + 0.28), xytext=(5.0, prev_y - (0.28 if prev_y < 8.0 else 0)),
                    arrowprops=dict(arrowstyle="->", color="#4A5568", lw=1.3))
        prev_y = y

    # Decision Diamond at y = 2.5
    diamond = patches.Polygon([[5.0, 2.75], [6.2, 2.3], [5.0, 1.85], [3.8, 2.3]],
                              closed=True, ec="#DD6B20", fc="#FEEBC8", lw=1.5)
    ax.add_patch(diamond)
    ax.text(5.0, 2.3, "Area(E) >= 0.10 m²?", ha='center', va='center', fontsize=8, fontweight='bold', color="#7B341E")
    ax.annotate("", xy=(5.0, 2.75), xytext=(5.0, 3.12),
                arrowprops=dict(arrowstyle="->", color="#4A5568", lw=1.3))

    # [No / Compliant] branch
    ax.annotate("", xy=(8.5, 2.3), xytext=(6.2, 2.3),
                arrowprops=dict(arrowstyle="->", color="#C53030", lw=1.3))
    ax.text(7.2, 2.45, "No [Compliant]", ha='center', va='center', fontsize=7.5, color="#C53030", fontweight='bold')
    rect_comp = patches.FancyBboxPatch((7.6, 1.2), 1.8, 0.5, boxstyle="round,pad=0.05",
                                      ec="#718096", fc="#F7FAFC", lw=1.2)
    ax.add_patch(rect_comp)
    ax.text(8.5, 1.45, "Log Compliant\nNo Breach", ha='center', va='center', fontsize=7.5, color="#4A5568")
    ax.plot([8.5, 8.5], [2.3, 1.7], color="#C53030", lw=1.3)

    # [Yes / Encroachment] branch
    ax.annotate("", xy=(5.0, 1.35), xytext=(5.0, 1.85),
                arrowprops=dict(arrowstyle="->", color="#276749", lw=1.3))
    ax.text(5.45, 1.6, "Yes [Breach]", ha='center', va='center', fontsize=7.5, color="#276749", fontweight='bold')

    rect_viol = patches.FancyBboxPatch((1.8, 0.8), 6.4, 0.55, boxstyle="round,pad=0.08",
                                      ec="#276749", fc="#E6FFFA", lw=1.3)
    ax.add_patch(rect_viol)
    ax.text(5.0, 1.07, "Compute Frontage, Projection Depth, Chainage Station & Persist Audit Trail",
            ha='center', va='center', fontsize=8, fontweight='bold', color="#234E52")

    # End Bullseye
    ax.plot(5.0, 0.35, 'o', color="#1A202C", markersize=14)
    ax.plot(5.0, 0.35, 'o', color="#FFFFFF", markersize=8)
    ax.plot(5.0, 0.35, 'o', color="#1A202C", markersize=4)
    ax.annotate("", xy=(5.0, 0.45), xytext=(5.0, 0.8),
                arrowprops=dict(arrowstyle="->", color="#4A5568", lw=1.3))

    plt.tight_layout()
    plt.savefig(out_dir / "activity_diagram.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated activity_diagram.png")

# -------------------------------------------------------------
# 5. DATABASE ER DIAGRAM
# -------------------------------------------------------------
def generate_er_diagram():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')

    entities = [
        {
            "name": "PROPERTIES",
            "pos": (0.6, 4.4), "w": 3.2, "h": 2.7,
            "fields": [
                ("parcel_id", "TEXT [PK]", True),
                ("owner_name_synthetic", "TEXT", False),
                ("address_synthetic", "TEXT", False),
                ("area_sqm", "REAL", False),
                ("geometry_json", "TEXT", False),
                ("disclaimer", "TEXT", False),
            ]
        },
        {
            "name": "ROAD_MASTER",
            "pos": (0.6, 0.8), "w": 3.2, "h": 2.9,
            "fields": [
                ("row_id", "TEXT [PK]", True),
                ("road_name", "TEXT", False),
                ("legal_width_m", "REAL", False),
                ("geometry_json", "TEXT", False),
                ("centerline_json", "TEXT", False),
                ("carriageway_json", "TEXT", False),
                ("disclaimer", "TEXT", False),
            ]
        },
        {
            "name": "ENCROACHMENT_CASES",
            "pos": (4.6, 0.8), "w": 4.0, "h": 6.3,
            "fields": [
                ("case_id", "TEXT [PK]", True),
                ("detection_id", "TEXT [FK]", True),
                ("parcel_id", "TEXT [FK]", True),
                ("row_id", "TEXT [FK]", True),
                ("class_name", "TEXT", False),
                ("status", "TEXT", False),
                ("action_required", "TEXT", False),
                ("severity", "TEXT", False),
                ("confidence", "REAL", False),
                ("chainage_m", "REAL", False),
                ("chainage_str", "TEXT", False),
                ("area_sqm", "REAL", False),
                ("frontage_m", "REAL", False),
                ("max_projection_m", "REAL", False),
                ("overlap_ratio_pct", "REAL", False),
                ("encroachment_polygon_json", "TEXT", False),
                ("created_at", "TIMESTAMP", False),
            ]
        },
        {
            "name": "DETECTIONS",
            "pos": (9.2, 4.4), "w": 2.6, "h": 2.7,
            "fields": [
                ("detection_id", "TEXT [PK]", True),
                ("frame_id", "TEXT", False),
                ("class_id", "INTEGER", False),
                ("class_name", "TEXT", False),
                ("confidence", "REAL", False),
                ("pixel_polygon_json", "TEXT", False),
                ("map_polygon_json", "TEXT", False),
            ]
        },
        {
            "name": "AUDIT_LOGS",
            "pos": (9.2, 0.8), "w": 2.6, "h": 2.4,
            "fields": [
                ("log_id", "INT [PK]", True),
                ("action_name", "TEXT", False),
                ("detail_text", "TEXT", False),
                ("created_at", "TIMESTAMP", False),
            ]
        }
    ]

    for ent in entities:
        x, y = ent["pos"]
        w, h = ent["w"], ent["h"]

        # Outer border
        rect = patches.Rectangle((x, y), w, h, ec="#1A365D", fc="#FFFFFF", lw=1.5)
        ax.add_patch(rect)

        # Header
        hdr = patches.Rectangle((x, y + h - 0.45), w, 0.45, ec="#1A365D", fc="#2B6CB0", lw=1.5)
        ax.add_patch(hdr)
        ax.text(x + w / 2, y + h - 0.22, ent["name"], ha='center', va='center',
                fontsize=9, fontweight='bold', color="#FFFFFF")

        curr_y = y + h - 0.65
        for col_name, col_type, is_key in ent["fields"]:
            col_str = f"• {col_name}: {col_type}"
            weight = 'bold' if is_key else 'normal'
            color = "#C53030" if is_key else "#2D3748"
            ax.text(x + 0.12, curr_y, col_str, ha='left', va='center',
                    fontsize=7.2, fontfamily='monospace', fontweight=weight, color=color)
            curr_y -= 0.28

    # Relationships (Crow's foot / 1-to-many lines)
    # PROPERTIES (1) -> ENCROACHMENT_CASES (N)
    ax.annotate("", xy=(4.6, 5.2), xytext=(3.8, 5.2),
                arrowprops=dict(arrowstyle="->", color="#2B6CB0", lw=1.5))
    ax.text(3.9, 5.35, "1", fontsize=8, fontweight='bold', color="#2B6CB0")
    ax.text(4.4, 5.35, "N", fontsize=8, fontweight='bold', color="#2B6CB0")

    # ROAD_MASTER (1) -> ENCROACHMENT_CASES (N)
    ax.annotate("", xy=(4.6, 2.2), xytext=(3.8, 2.2),
                arrowprops=dict(arrowstyle="->", color="#2B6CB0", lw=1.5))
    ax.text(3.9, 2.35, "1", fontsize=8, fontweight='bold', color="#2B6CB0")
    ax.text(4.4, 2.35, "N", fontsize=8, fontweight='bold', color="#2B6CB0")

    # DETECTIONS (1) -> ENCROACHMENT_CASES (N)
    ax.annotate("", xy=(8.6, 5.2), xytext=(9.2, 5.2),
                arrowprops=dict(arrowstyle="->", color="#2B6CB0", lw=1.5))
    ax.text(9.05, 5.35, "1", fontsize=8, fontweight='bold', color="#2B6CB0")
    ax.text(8.75, 5.35, "N", fontsize=8, fontweight='bold', color="#2B6CB0")

    plt.tight_layout()
    plt.savefig(out_dir / "er_diagram.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated er_diagram.png")

if __name__ == "__main__":
    generate_use_case_diagram()
    generate_class_diagram()
    generate_sequence_diagram()
    generate_activity_diagram()
    generate_er_diagram()
    print("All 5 OOAD diagrams successfully generated!")
