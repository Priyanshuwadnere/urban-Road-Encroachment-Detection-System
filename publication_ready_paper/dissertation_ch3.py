import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from publication_ready_paper.dissertation_ch1_ch2 import (
    add_heading_1, add_heading_2, add_heading_3, add_body_p
)

def build_chapter_3(doc, figures_dir):
    add_heading_1(doc, "Chapter 3: Methodology and Implementation")
    
    add_body_p(
        doc,
        "This chapter presents the comprehensive architectural design, mathematical formulation, and software engineering implementation "
        "of the proposed Urban Road Encroachment Detection System. The framework resolves the semantic-legal disconnect by decoupling "
        "deep neural instance segmentation from authoritative cadastral vector geometry. This section details the hardware and software "
        "specifications, dataset preparation protocols, coordinate homography mapping, YOLOv8n-seg neural network architecture, vector set algebra, "
        "linear road chainage projection algorithms, and the interactive municipal decision-support dashboard."
    )

    add_heading_2(doc, "3.1 System Architecture and Block Diagram")
    add_body_p(
        doc,
        "The overall system architecture is designed as a modular, decoupled cyber-physical pipeline organized into seven sequential stages, "
        "spanning optical remote sensing, coordinate homography, deep instance segmentation, vector GIS analytics, and legal notice generation. "
        "Figure 1.1 illustrates the complete operational workflow."
    )

    # Embed Figure 1.1 (Workflow)
    fig1_path = os.path.join(figures_dir, "fig1_workflow.jpg")
    if os.path.exists(fig1_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(fig1_path, width=Inches(6.2))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        r_c = p_cap.add_run("Figure 1.1: Seven-stage cyber-physical workflow for urban road corridor compliance monitoring")
        r_c.font.name = "Times New Roman"
        r_c.font.size = Pt(10)
        r_c.font.bold = True

    add_body_p(
        doc,
        "As depicted in Figure 1.2, the production deployment is structured into five distinct architectural tiers: "
        "(i) Presentation Layer (interactive Leaflet.js map viewer, sidebar inspection drawer, and administrative controls), "
        "(ii) Application Service Layer (FastAPI asynchronous REST API endpoints exposing segmentation, GIS analysis, and export services), "
        "(iii) Spatial Computing Engine (Shapely computational geometry implementing planar sweep set operations), "
        "(iv) Academic Relational Database (SQLite database managing property deeds, road ROW corridors, and violation records), and "
        "(v) Deep Learning Vision Pipeline (PyTorch YOLOv8n-seg model for sub-meter structural contour delineation)."
    )

    # Embed Figure 1.2 (Architecture)
    fig2_path = os.path.join(figures_dir, "fig2_architecture.jpg")
    if os.path.exists(fig2_path):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_before = Pt(8)
        p_img2.paragraph_format.space_after = Pt(4)
        run_img2 = p_img2.add_run()
        run_img2.add_picture(fig2_path, width=Inches(6.2))
        
        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap2.paragraph_format.space_after = Pt(12)
        r_c2 = p_cap2.add_run("Figure 1.2: Decoupled microservice architecture: Presentation, REST API, Spatial Engine, and Deep Learning Vision Pipeline")
        r_c2.font.name = "Times New Roman"
        r_c2.font.size = Pt(10)
        r_c2.font.bold = True

    add_heading_2(doc, "3.2 Hardware Description")
    add_body_p(
        doc,
        "The system was engineered and benchmarked under both development workstation conditions and simulated edge-deployment targets. "
        "Table 3.1 details the development workstation configuration and the target embedded compute platforms for onboard municipal drone integration."
    )

    # Table 3.1: Hardware Specs
    p_tbl_cap = doc.add_paragraph()
    p_tbl_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tc = p_tbl_cap.add_run("Table 3.1: Corridor hardware development and edge-deployment specifications")
    r_tc.font.name = "Times New Roman"
    r_tc.font.size = Pt(10)
    r_tc.font.bold = True

    h_table = doc.add_table(rows=1, cols=3)
    h_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, h in enumerate(["Hardware Subsystem", "Development Workstation", "Target Drone Edge Hardware"]):
        c = h_table.rows[0].cells[idx]
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.font.bold = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    hw_rows = [
        ("Processor (CPU)", "AMD Ryzen 7 5800H @ 3.20 GHz (8 Cores, 16 Threads)", "NVIDIA Jetson Orin Nano (6-core Arm Cortex-A78AE)"),
        ("Memory (RAM)", "16.0 GB DDR4-3200 MHz", "8.0 GB 128-bit LPDDR5 (68 GB/s)"),
        ("Graphics Accelerator", "Integrated AMD Radeon Graphics (CPU Inference Mode)", "1024-core NVIDIA Ampere GPU with 32 Tensor Cores"),
        ("Primary Storage", "512 GB PCIe NVMe M.2 Solid State Drive", "64 GB MicroSDXC UHS-I / NVMe M.2 2280 SSD"),
        ("UAV Platform Equivalent", "DJI Matrice 300 RTK / Quadcopter Simulation Platform", "Low-altitude commercial survey drone (<2.0 kg MTOW)"),
        ("Optical Sensor Payload", "Nadir RGB optical camera (20 MP equivalent, mechanical shutter)", "Stabilized 4K RGB gimbal camera (GSD ~ 5 cm/pixel)")
    ]
    for row in hw_rows:
        r_cells = h_table.add_row().cells
        for col_idx, text in enumerate(row):
            p = r_cells[col_idx].paragraphs[0]
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            if col_idx == 0:
                r.font.bold = True

    add_heading_2(doc, "3.3 Software Description, Flowchart / Algorithm")
    add_body_p(
        doc,
        "The software architecture is implemented using an asynchronous, microservice-inspired Python stack. Table 3.2 details the "
        "software frameworks, package versions, and architectural responsibilities."
    )

    # Table 3.2: Software Stack
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    p_tbl_cap2 = doc.add_paragraph()
    p_tbl_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tc2 = p_tbl_cap2.add_run("Table 3.2: Software frameworks, libraries, versions, and architectural responsibilities")
    r_tc2.font.name = "Times New Roman"
    r_tc2.font.size = Pt(10)
    r_tc2.font.bold = True

    s_table = doc.add_table(rows=1, cols=3)
    s_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, h in enumerate(["Software Component", "Version / Runtime", "Architectural Role / Responsibility"]):
        c = s_table.rows[0].cells[idx]
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.font.bold = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sw_rows = [
        ("Python Runtime", "Python 3.14.4 (64-bit)", "Core execution environment and algorithmic computation"),
        ("Deep Learning Framework", "PyTorch 2.14.0+cpu", "Tensor computation and neural network graph execution"),
        ("Computer Vision Core", "Ultralytics 8.4.149 (YOLOv8)", "YOLOv8n-seg model architecture, training, and mask inference"),
        ("Computational Geometry", "Shapely 2.0.7 (GEOS 3.11.2)", "Planar vector set algebra (union, difference, intersection, buffering)"),
        ("Backend Web Framework", "FastAPI 0.115.0 & Uvicorn", "Asynchronous RESTful API endpoints and background task workers"),
        ("Relational Database", "SQLite 3.45.1", "ACID-compliant storage of deeds, cadastral layers, and encroachment records"),
        ("Frontend GIS Dashboard", "Leaflet.js 1.9.4 & HTML5/CSS3", "Interactive vector layer visualization, polygon styling, and filtering"),
        ("Automated Test Suite", "Pytest 8.3.4", "Test-driven verification suite covering 86 automated pipeline tests")
    ]
    for row in sw_rows:
        r_cells = s_table.add_row().cells
        for col_idx, text in enumerate(row):
            p = r_cells[col_idx].paragraphs[0]
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            if col_idx == 0:
                r.font.bold = True

    add_heading_3(doc, "Algorithm 1: Automated Spatial Compliance and Attribution Pipeline")
    add_body_p(
        doc,
        "Algorithm 1 formalizes the complete operational decision logic that transforms an aerial image and vector GIS layers into "
        "attributed municipal encroachment records."
    )

    # Algorithm Box / Code Block
    alg_text = (
        "Algorithm 1: Automated Spatial Road ROW Compliance Analysis\n"
        "----------------------------------------------------------------------------------------------------\n"
        "Input: Aerial Image I, Cadastral Parcels P = {P_1, ..., P_K}, Statutory ROW R_ROW,\n"
        "       Centerline Curve L_center, Road Zones (C_paved, M_footpath), Affine Matrix A,\n"
        "       Area Noise Tolerance Threshold tau_area = 0.10 m^2.\n"
        "Output: Set of verified municipal corridor violation records E_cases.\n"
        "----------------------------------------------------------------------------------------------------\n"
        " 1: Initialize E_cases = {}\n"
        " 2: I_norm, lambda, dx, dy = LetterboxPreprocessing(I, target_size=(192, 192))\n"
        " 3: D = YOLOv8n_seg_Inference(I_norm, conf_threshold=0.0016)\n"
        " 4: for each detected instance d in D do:\n"
        " 5:     s_px = InverseLetterbox(d.mask_polygon, lambda, dx, dy)\n"
        " 6:     if CountVertices(s_px) < 3 then continue end if\n"
        " 7:     S_metric = AffineCoordinateTransform(s_px, A)\n"
        " 8:     if not S_metric.is_valid then S_metric = S_metric.buffer(0) end if\n"
        " 9:     P_star = argmax_{P_k in P} Area(S_metric n P_k)   // Find parent parcel\n"
        "10:     if P_star is None then continue end if\n"
        "11:     O = S_metric \\ P_star.geometry                    // Vector difference: outside private deed\n"
        "12:     E = O n R_ROW                                      // Vector intersection: public corridor breach\n"
        "13:     if O is empty or Area(E) < tau_area then continue end if\n"
        "14:     a_cw = Area(E n C_paved)\n"
        "15:     a_fp = Area(E n M_footpath)\n"
        "16:     if a_cw > 0.05 and a_fp > 0.05 then zone = 'ROAD_MARGIN'\n"
        "17:     else if a_cw > 0.05 then zone = 'PAVED_ROAD'\n"
        "18:     else zone = 'FOOTPATH' end if\n"
        "19:     A_enc = Area(E)\n"
        "20:     w_front = ComputeFrontageWidth(E, P_star.geometry)\n"
        "21:     d_proj = ComputeMaximumProjectionDepth(E, P_star.geometry)\n"
        "22:     d_chain, station_str = ProjectCenterlineChainage(Centroid(E), L_center)\n"
        "23:     severity = DetermineSeverityClass(A_enc, d_proj)\n"
        "24:     record = CreateDossier(P_star.id, zone, A_enc, w_front, d_proj, station_str, severity)\n"
        "25:     E_cases = E_cases U {record}\n"
        "26: end for\n"
        "27: return E_cases\n"
        "----------------------------------------------------------------------------------------------------"
    )
    p_alg = doc.add_paragraph()
    p_alg.paragraph_format.line_spacing = 1.15
    p_alg.paragraph_format.space_before = Pt(6)
    p_alg.paragraph_format.space_after = Pt(12)
    r_alg = p_alg.add_run(alg_text)
    r_alg.font.name = "Courier New"
    r_alg.font.size = Pt(8.5)

    add_heading_2(doc, "3.4 Dataset Preparation and Ingestion")
    add_body_p(
        doc,
        "The empirical study area models an 85-meter corridor within a simulated Indian residential and commercial colony "
        "measuring approximately 180 m × 150 m. The dataset was constructed using continuous, simulated UAV flight video sequences "
        "captured with nadir camera angles and nominal 2.0-meter camera waypoint translations along the corridor axis. "
        "The complete dataset comprises 90 distinct frames divided into three chronological sequences of 30 frames each:\n"
        "• Sequence 1 (R001_SEQ01): Frames 001 to 030, designated strictly for Training.\n"
        "• Sequence 2 (R001_SEQ02): Frames 031 to 060, designated strictly for Validation.\n"
        "• Sequence 3 (R001_SEQ03): Frames 061 to 090, designated strictly as the Held-Out Test split."
    )
    add_body_p(
        doc,
        "Crucially, splitting the dataset at the sequence level rather than performing random frame shuffling prevents temporal and "
        "spatial leakage: adjacent video frames share near-identical background textures, so random shuffling would result in "
        "artificially inflated evaluation metrics."
    )

    add_heading_2(doc, "3.5 Image Preprocessing and Homography Mapping")
    add_body_p(
        doc,
        "Raw image tiles extracted from the drone sequences feature resolutions varying between 170×136 pixels and 171×154 pixels. "
        "To standardize input tensors for deep neural inference without distorting geometric aspect ratios, an adaptive letterbox "
        "transformation is applied. The transformation scales the input frame by a uniform factor lambda = min(W_target / W_orig, H_target / H_orig) "
        "and pads the remaining borders with neutral grey (114, 114, 114) pixels."
    )
    add_body_p(
        doc,
        "To project segmented image coordinates into metric cadastral space, an affine transformation matrix A in R^{3 x 3} is computed:"
    )
    # Math
    p_m1 = doc.add_paragraph()
    p_m1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_m1 = p_m1.add_run(
        "[ X ]   [ a_11  a_12  a_13 ] [ u ]\n"
        "[ Y ] = [ a_21  a_22  a_23 ] [ v ]\n"
        "[ 1 ]   [   0     0     1  ] [ 1 ]"
    )
    r_m1.font.name = "Times New Roman"
    r_m1.font.size = Pt(11)
    r_m1.font.bold = True

    add_body_p(
        doc,
        "Under orthorectified nadir projection with pixel scale factors s_x, s_y (meters per pixel) and origin offset (X_0, Y_0):\n"
        "X = X_0 + u * s_x\n"
        "Y = Y_0 + (H - v) * s_y\n"
        "The transformation is verified to be non-singular and invertible by enforcing det(A) = a_11 * a_22 - a_12 * a_21 != 0."
    )

    add_heading_2(doc, "3.6 Annotation and Quality Assurance Procedures")
    add_body_p(
        doc,
        "All 90 frames were manually annotated with high-density polygonal contours adhering to a strict 8-class architectural taxonomy: "
        "building (permanent residential/commercial massing), staircase, shop_extension, veranda, shed, ramp, awning, and compound_wall. "
        "A rigorous, multi-stage automated quality assurance audit script (annotation_auditor.py) evaluated all 551 annotated instances against "
        "three strict validation rules:\n"
        "1. Minimum Area Rule: Polygons with an area less than 15 square pixels are flagged as potential annotation noise.\n"
        "2. Vertex Count Rule: Polygons with fewer than 4 vertices or self-intersecting segments are rejected as invalid geometries.\n"
        "3. Image Boundary Rule: Polygons touching the extreme image edge (within 2 pixels of the frame border) are flagged as questionable "
        "due to potential occlusion truncation."
    )

    add_heading_2(doc, "3.7 Computer Vision Model Architecture")
    add_body_p(
        doc,
        "We implement the edge-optimized YOLOv8n-seg instance segmentation network. YOLOv8n-seg is an anchor-free single-stage detector "
        "featuring 3.26 million parameters and 12.0 GFLOPs at nominal resolution. The architecture comprises three integrated subsystems:\n"
        "• Backbone: A modified CSPDarknet53 network featuring cross-stage partial connections (C2f modules) and spatial pyramid pooling fast "
        "(SPPF) to extract multi-scale visual features while preserving spatial gradients.\n"
        "• Neck: A Path Aggregation Network (PANet) with Feature Pyramid Network (FPN) pathways that blends high-level semantic context with "
        "low-level localization features across three spatial scales (P3, P4, P5).\n"
        "• Segmentation Head: A dual-branch head that decouples box regression/classification from mask generation. The prototype branch "
        "(Proto) computes 32 high-resolution prototype mask tensors across the image, while the detection heads predict scalar mask coefficients. "
        "Final instance masks are generated via linear matrix multiplication followed by sigmoid thresholding."
    )

    add_heading_2(doc, "3.8 Training and Inference Pipeline")
    add_body_p(
        doc,
        "The model was trained from pre-trained COCO initial weights using stochastic gradient descent (SGD) with momentum (0.937) and weight "
        "decay (0.0005). The loss objective minimizes a multi-task composite loss function L_total = lambda_box * L_box + lambda_cls * L_cls + "
        "lambda_dfl * L_dfl + lambda_seg * L_seg, where L_seg is formulated as the pixel-wise binary cross-entropy between predicted instance "
        "masks and ground-truth rasterized polygons."
    )

    add_heading_2(doc, "3.9 Evaluation Methodology")
    add_body_p(
        doc,
        "Model segmentation quality is evaluated using standard PASCAL VOC and MS COCO metrics: Precision (P), Recall (R), F1-Score, and "
        "Mean Average Precision (mAP) computed at an Intersection-over-Union (IoU) threshold of 0.50 (mAP_50) and averaged across IoU thresholds "
        "from 0.50 to 0.95 in 0.05 increments (mAP_50-95)."
    )

    add_heading_2(doc, "3.10 GIS-Based Spatial Analysis & Vector Algebra")
    add_body_p(
        doc,
        "The core innovation of the proposed framework is the computational geometry engine (Phase5GISEngine). Once instance masks are "
        "transformed into metric space, the engine executes planar set algebra using the Weiler-Atherton clipping algorithm implemented via GEOS/Shapely:\n"
        "1. Parcel Allocation: Each detected physical structure S_j is associated with its deeded cadastral parcel P_j^* by maximizing shared areal overlap: "
        "P_j^* = argmax_{P_k in P} Area(S_j n P_k).\n"
        "2. Private Setback Isolation: The vector difference O_j = S_j \\ P_j^* isolates the portion of the physical structure residing outside the legal deed.\n"
        "3. Statutory ROW Intrusion: The intersection E_j = O_j n R_ROW extracts the exact statutory corridor encroachment polygon.\n"
        "4. Municipal Tolerance Threshold: If Area(E_j) >= tau_area (where tau_area = 0.10 m²), the structure is flagged as an actionable violation. "
        "Structures with Area(E_j) < 0.10 m² or O_j = empty set are classified as compliant, producing zero false positives."
    )

    add_heading_2(doc, "3.11 Multi-Zone Corridor Model and Municipal Attribution")
    add_body_p(
        doc,
        "The statutory Road Right-of-Way (R_ROW, width 9.00 m) is partitioned into a 6.00 m paved carriageway (C_paved) and dual 1.50 m "
        "pedestrian sidewalks (M_west, M_east). When a violation E_j is confirmed, the engine computes four critical legal enforcement parameters:\n"
        "• Encroached Area A_enc = double_integral_{E_j} dx dy (m²).\n"
        "• Frontage Width w_front = H^1(partial E_j n partial P_j^*) (meters along parcel boundary).\n"
        "• Maximum Projection Depth d_proj = sup_{x in E_j} inf_{y in partial P_j^*} ||x - y||_2 (meters perpendicular into ROW).\n"
        "• Footpath Obstruction Ratio rho_obstruction = min(100.0, d_proj / 1.50 m * 100%).\n"
        "• Linear Road Chainage Station: The centroid of E_j is projected onto the surveyed road centerline L_center, computing the exact "
        "scalar distance along the corridor and formatting it in standard civil engineering stationing: Station = K + M (e.g., 0+011.0).\n\n"
        "Engineering Severity Rule: Violations are stratified into municipal priority tiers: CRITICAL (A_enc >= 10 m² or d_proj >= 2.0 m), "
        "HIGH (A_enc >= 5.0 m² or d_proj >= 1.0 m), MODERATE (A_enc >= 2.0 m² or d_proj >= 0.5 m), and MINOR (A_enc > 0 m²)."
    )

    add_heading_2(doc, "3.12 Dashboard and Decision Support Interface")
    add_body_p(
        doc,
        "To enable municipal engineers to audit results without GIS expertise, an enterprise web dashboard was developed. Built with "
        "FastAPI, SQLite, and Leaflet.js, the dashboard features a multi-layer interactive map rendering cadastral parcel bounds (cyan dashed lines), "
        "statutory ROW corridors (solid red lines), road centerlines with 5-meter chainage markers, and color-coded encroachment polygons. "
        "The dashboard provides one-click export of GeoJSON feature layers, CSV tabular summaries, and auto-generated HTML/PDF legal notices "
        "ready for municipal enforcement squads."
    )

    add_heading_2(doc, "3.13 Testing and Verification Suite")
    add_body_p(
        doc,
        "To ensure production-grade reliability, the entire pipeline is backed by an automated 86-test pytest verification suite. "
        "The test suite covers: (i) geometric manifoldness and polygon self-intersection validation, (ii) affine transformation reversibility "
        "ensuring ||A^{-1}(A(x)) - x|| < 10^{-6}, (iii) cadastral non-intersection proofs verifying that compliant structures produce null "
        "encroachments, and (iv) database schema and REST API response integrity under simulated load."
    )

    add_heading_2(doc, "3.14 Chapter Summary")
    add_body_p(
        doc,
        "This chapter articulated the mathematical and software engineering design of the proposed framework. By decoupling YOLOv8n-seg "
        "optical instance segmentation from Shapely vector set algebra, the system achieves sub-meter geometric compliance verification, "
        "computes standardized road chainage stationing, and outputs legally defensible audit dossiers. The empirical evaluation of this "
        "pipeline is presented in Chapter 4."
    )
    doc.add_page_break()
    print("Chapter 3 built successfully.")
