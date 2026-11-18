import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(18)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.bold = True
    return p

def add_body_p(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p

def build_chapter_1(doc):
    add_heading_1(doc, "Chapter 1: Introduction")
    
    add_body_p(
        doc,
        "Urban roadways are critical municipal infrastructure assets that govern the economic efficiency, public safety, "
        "and overall liveability of contemporary cities. In rapidly expanding metropolitan areas and secondary townships "
        "across developing nations—most notably in South Asia, Southeast Asia, and Latin America—public road corridors are "
        "subjected to chronic, progressive structural encroachments. Property owners, commercial establishments, and informal "
        "vendors routinely extend physical, permanent, and semi-permanent structures beyond statutory cadastral boundaries "
        "into the gazetted Road Right-of-Way (ROW). These violations manifest as extended metal shop awnings, elevated entrance "
        "ramps, masonry compound walls, cantilevered verandas, and raised commercial display platforms. This introductory chapter "
        "establishes the municipal and technological context of the project, articulates the core problem statement, outlines the "
        "primary research questions and contributions, and details the structural organization of this dissertation."
    )

    add_heading_2(doc, "1.1 Background of the Project Topic")
    add_body_p(
        doc,
        "The management of urban public infrastructure in Indian municipal bodies (such as Municipal Corporations and Nagarpalikas) "
        "is governed by statutory Town and Country Planning Acts, Municipal Corporation Acts, and National Urban Transport Policies. "
        "Under these statutory frameworks, urban roadways are legally designated as non-alienable public easements. The Road Right-of-Way "
        "is legally partitioned into specific functional components, including the paved carriageway dedicated to vehicular movement, "
        "kerb transition margins, storm-water drainage conduits, and reserved pedestrian sidewalks."
    )
    add_body_p(
        doc,
        "Despite well-defined master plans, enforcing corridor compliance remains an intractable governance challenge. The conventional "
        "operational workflow in Indian urban local bodies relies on periodic manual inspections conducted by municipal junior engineers "
        "and ward-level tax inspectors. Ground-level surveys using measuring tapes or total stations are labor-intensive, geographically "
        "fragmented, and intrinsically vulnerable to subjective interpretation. Furthermore, when municipal authorities issue eviction "
        "or demolition notices, aggrieved property owners frequently challenge the enforcement in civil courts, alleging arbitrary "
        "targeting and disputing the accuracy of the surveyed boundary line. The absence of an immutable, georeferenced, and mathematically "
        "verifiable evidence base results in prolonged judicial litigation and administrative inertia."
    )
    add_body_p(
        doc,
        "Concurrently, the rapid proliferation of small commercial Unmanned Aerial Vehicles (UAVs) and high-resolution digital cameras "
        "has revolutionized remote sensing. Drone photogrammetry offers sub-5 cm Ground Sampling Distance (GSD), high temporal frequency, "
        "and zero interference with active street traffic. Combined with national digital land initiatives—such as the Government of India's "
        "SVAMITVA scheme (Survey of Villages and Mapping with Improvised Technology in Village Areas)—authoritative cadastral records are "
        "becoming digitally accessible in vector formats. However, bridging the technological gap between raw aerial drone imagery and "
        "legally actionable cadastral enforcement remains an unaddressed engineering bottleneck."
    )

    add_heading_2(doc, "1.2 Motivation and Scope of the Report")
    add_body_p(
        doc,
        "The primary motivation of this project is to eliminate the legal and technical ambiguity surrounding road encroachment enforcement "
        "by developing an automated, test-driven spatial decision-support prototype. By uniting modern computer vision (deep instance segmentation) "
        "with computational geometry (vector set algebra), this project aims to provide municipal engineers with an automated pipeline that can:"
    )
    
    bullets = [
        "Ingest aerial drone orthophotos and extract physical structural boundaries without manual tracing.",
        "Transform raw pixel coordinates into a metric Cartesian GIS coordinate frame via homography.",
        "Execute formal vector set difference and intersection operations against authoritative cadastral parcels and Road ROW corridors.",
        "Compute exact municipal engineering metrics, including encroached polygon area (m²), lateral projection depth (m), frontage width (m), road centerline chainage stationing, and footpath blockage ratio (%).",
        "Generate auditable, non-repudiable legal notice dossiers backed by an interactive Leaflet GIS dashboard."
    ]
    for b in bullets:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(b)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)

    add_body_p(
        doc,
        "Scope and Academic Prototype Boundaries: This capstone research project is developed as an academic engineering prototype. "
        "The empirical study area is based on an 85-meter corridor within a simulated residential colony (180 m × 150 m) captured through "
        "synthetic drone-style video sequences with moving nadir viewpoints and nominal 2 m camera increments. The report transparently "
        "evaluates the performance, limitations, and verification of this prototype under controlled benchmark conditions, and outlines "
        "the requisite operational steps (DGPS georeferencing, true orthophoto orthorectification, and human-in-the-loop review) required "
        "before full-scale municipal field deployment."
    )

    add_heading_2(doc, "1.3 Problem Statement")
    add_body_p(
        doc,
        "A prevailing and critical error in applied artificial intelligence is the framing of road encroachment detection as an end-to-end "
        "computer vision problem. Numerous recent publications train deep neural networks directly on annotated bounding boxes labeled "
        "as 'encroachment'. We argue that this formulation is fundamentally and theoretically flawed:"
    )
    add_body_p(
        doc,
        "1. Physical Equivalence: An awning, entrance ramp, veranda shed, or compound wall is an architecturally identical visual pattern "
        "whether it is constructed entirely within a lawful private property setback or illegally extends into the public road right-of-way.\n"
        "2. Optical Invisibility of Legal Deeds: An optical sensor records only reflected electromagnetic radiance (RGB intensities). "
        "A camera cannot observe property deed boundaries, statutory right-of-way gazette notifications, or municipal building permission limits.\n"
        "3. Relational Legal Nature: Consequently, 'encroachment' is not an optical visual class or material texture; it is a spatial-legal "
        "topological relationship between a physical structure and a statutory jurisdiction boundary."
    )
    add_body_p(
        doc,
        "Therefore, the formal problem addressed in this dissertation is: How can computer vision and cadastral computational geometry be "
        "formally decoupled such that physical structures are segmented purely from optical characteristics, mapped into metric space via inverse "
        "affine transformation, and evaluated against authoritative vector boundaries using topological set algebra without generating false "
        "positives on lawful private setbacks?"
    )

    add_heading_2(doc, "1.4 Salient Contributions")
    add_body_p(
        doc,
        "The primary engineering and scientific contributions of this capstone research include:"
    )
    conts = [
        ("Decoupled Cyber-Physical Architecture: ", "Formalized a modular separation of concerns between visual instance segmentation (YOLOv8n-seg) and cadastral vector set algebra (Shapely computational geometry), preventing false positive classifications on lawful private building extensions."),
        ("Multi-Zone Corridor Spatial Model: ", "Formulated a closed-form geometric partition of the statutory Road ROW into a 6.00 m paved vehicular carriageway, two 1.50 m pedestrian sidewalks, and kerb transition margins, enabling severity-stratified municipal enforcement."),
        ("Automated Municipal Attribution Engine: ", "Implemented continuous scalar projection of encroaching polygon centroids onto the road centerline curve, automatically computing standard civil engineering chainage stations (e.g., 0+011.0), frontage width, projection depth, and footpath obstruction percentage."),
        ("Rigorous Evidence-Based Verification: ", "Conducted an exhaustive data sufficiency audit resolving class imbalance across 551 annotated structural instances, and established an 86-test automated pytest verification suite guaranteeing zero polygon self-intersection and boundary non-leakage.")
    ]
    for ctitle, cdesc in conts:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(4)
        r_t = p.add_run(ctitle)
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(11)
        r_t.font.bold = True
        r_d = p.add_run(cdesc)
        r_d.font.name = "Times New Roman"
        r_d.font.size = Pt(11)

    add_heading_2(doc, "1.5 Organization of the Report")
    add_body_p(
        doc,
        "The remainder of this dissertation is organized into five subsequent chapters:\n\n"
        "Chapter 2: Literature Survey provides an exhaustive review of 16 peer-reviewed journal and conference publications covering "
        "UAV photogrammetry, deep instance segmentation, cadastral GIS, and spatial computing, synthesizing findings into a structured "
        "comparison table and articulating the identified research gap.\n\n"
        "Chapter 3: Methodology and Implementation details the complete system architecture, hardware specifications, software stack, "
        "dataset curation, YOLOv8n-seg network architecture, affine coordinate registration, computational geometry algorithms, and the "
        "FastAPI/Leaflet decision-support platform.\n\n"
        "Chapter 4: Results and Analysis presents the empirical evaluation, including dataset audit statistics, model precision-recall "
        "curves, confusion matrices, spatial engine accuracy against benchmark ground truths, and a systematic error analysis.\n\n"
        "Chapter 5: Advantages, Limitations and Applications critically analyzes the operational benefits, technological limitations "
        "(such as relief displacement and legacy cadastral distortions), and potential municipal governance applications.\n\n"
        "Chapter 6: Conclusion and Future Scope summarizes the research outcomes and outlines a prioritized roadmap for scaling the "
        "system to multi-camera city-scale drone operations."
    )
    doc.add_page_break()
    print("Chapter 1 built successfully.")

def build_chapter_2(doc):
    add_heading_1(doc, "Chapter 2: Literature Survey")
    
    add_body_p(
        doc,
        "The automated monitoring of urban road corridor compliance intersects three rapidly evolving technological domains: "
        "(i) high-resolution Unmanned Aerial Vehicle (UAV) remote sensing and photogrammetry, (ii) contemporary deep learning architectures "
        "for aerial instance segmentation, and (iii) Geographic Information Systems (GIS) spatial computing and cadastral analytics. "
        "This chapter provides an exhaustive, critical analysis of foundational and recent literature across these three domains, presents "
        "a structured comparative synthesis, and defines the precise research gap addressed by this dissertation."
    )

    add_heading_2(doc, "2.1 Introduction to the Research Area")
    add_body_p(
        doc,
        "Historically, urban land administration and infrastructure monitoring relied on satellite remote sensing (e.g., Landsat, Sentinel, "
        "QuickBird) or manned aerial photography. While satellite platforms provide regional coverage, their spatial resolution "
        "(0.5 m to 30 m/pixel) and rigid orbital revisit schedules are fundamentally inadequate for detecting sub-meter architectural encroachments "
        "such as a 0.80 m awning overhang or a 1.20 m concrete ramp. The emergence of lightweight civil UAVs equipped with stabilized "
        "optical gimbals has bridged this spatial divide, enabling on-demand photogrammetric surveys with ground sampling distances below 5 cm/pixel."
    )
    add_body_p(
        doc,
        "Concurrently, the field of computer vision has transitioned from hand-engineered features (e.g., SIFT, HOG, Canny edge detectors) "
        "to deep Convolutional Neural Networks (CNNs) and Vision Transformers. Within urban remote sensing, the primary focus has centered "
        "on building footprint extraction and road surface segmentation. However, the application of instance segmentation to municipal "
        "regulatory compliance introduces unique theoretical challenges that cannot be resolved solely through higher neural network capacity."
    )

    add_heading_2(doc, "2.2 Detailed Literature Survey")
    add_body_p(
        doc,
        "This section reviews 16 seminal and contemporary research papers, critically evaluating their methodology, datasets, reported "
        "performance, and operational limitations in the context of urban road corridor monitoring:"
    )

    papers = [
        ("Colomina & Molina (2014) [1]", "Unmanned aerial systems for photogrammetry and remote sensing: A review",
         "The authors conducted an exhaustive survey of UAS photogrammetry, detailing platform aerodynamics, payload sensor integration, "
         "and structure-from-motion (SfM) processing pipelines. They demonstrated that low-altitude drone surveys achieve geometric accuracy "
         "comparable to classical terrestrial photogrammetry at a fraction of the operational cost. However, the survey focused strictly on "
         "raw sensor data acquisition and orthomosaic generation, noting that automated extraction of functional municipal features remained "
         "an open challenge requiring advanced computer vision."),
         
        ("Nex & Remondino (2014) [2]", "UAV for 3D mapping applications: a review",
         "This work analyzed the technological maturation of UAVs in 3D urban mapping. The authors evaluated dense point-cloud generation "
         "from overlapping aerial imagery, establishing best practices for ground control point (GCP) placement and flight path planning. "
         "The primary limitation identified was the reliance on manual visual interpretation of point clouds and meshes for urban feature "
         "classification, creating a severe operational bottleneck in municipal management."),

        ("Yurtseven (2019) [3]", "Determination of roadside urban assets with high-resolution UAV photogrammetry",
         "Yurtseven investigated the use of sub-3 cm UAV imagery for inventorying urban road furniture, light poles, and curb lines in "
         "Turkish municipalities. Using photogrammetric point clouds, the author manually digitized roadside infrastructure and evaluated "
         "spatial accuracy against total station benchmarks. While proving the feasibility of drone-based asset detection, the methodology "
         "lacked automated segmentation algorithms and did not incorporate cadastral parcel layers or Right-of-Way legal boundaries."),

        ("He et al. (2017) [4]", "Mask R-CNN",
         "The authors introduced Mask R-CNN, extending Faster R-CNN by adding a parallel branch for predicting pixel-level segmentation masks "
         "alongside bounding box classification. Evaluated on the COCO benchmark, the model achieved state-of-the-art instance segmentation. "
         "While widely adopted in aerial building extraction, its two-stage proposal-generation architecture incurs significant computational "
         "overhead, limiting real-time deployment on edge computing platforms onboard drones."),

        ("Ronneberger et al. (2015) [5]", "U-Net: Convolutional networks for biomedical image segmentation",
         "U-Net introduced an encoder-decoder architecture with skip connections that preserve high-resolution spatial details across feature "
         "abstractions. Heavily adapted for satellite land-cover mapping, U-Net produces semantic segmentation rasters. However, semantic "
         "segmentation merges adjacent contiguous structures into monolithic pixel masks, failing to separate individual architectural "
         "instances (e.g., distinguishing an awning from the underlying building massing), which is essential for legal ownership attribution."),

        ("Kirillov et al. (2024) [6]", "Segment Anything",
         "Meta AI introduced the Segment Anything Model (SAM), a visual foundation model trained on over 1 billion masks across 11 million "
         "images. SAM demonstrated unprecedented zero-shot generalization across diverse optical domains using geometric prompts (points, "
         "boxes). However, SAM requires external prompt generators for automated inference, possesses substantial model parameter weight "
         "(over 600M parameters), and remains completely unaware of cadastral legal parcel bounds."),

        ("Chen et al. (2024) [7]", "RSPrompter: Learning to prompt for remote sensing instance segmentation based on visual foundation model",
         "Chen et al. proposed RSPrompter, integrating SAM with automated prompt learning heads tailored for Earth observation images. Evaluated "
         "on NWPU VHR-10 and SSDD datasets, the model achieved high mask accuracy on aerial targets without human bounding-box prompts. Nonetheless, "
         "the network requires high-end server GPUs, processes images in heavy offline batches, and does not perform spatial coordinate projection "
         "into local cadastral reference systems."),

        ("Li et al. (2024) [8]", "A review of building extraction from remote sensing imagery: Geometrical structures and semantic attributes",
         "This comprehensive survey critically evaluated deep learning architectures for building footprint extraction across SpaceNet, WHU, "
         "and aerial datasets. The authors categorized approaches into contour refinement, polygon regularization, and multi-task learning. "
         "A key finding was that virtually all modern models focus exclusively on rooftop outline geometry, completely omitting legal property "
         "boundaries or right-of-way easement intersections."),

        ("Jocher et al. (2023) [9]", "Ultralytics YOLOv8",
         "Ultralytics released YOLOv8, introducing an anchor-free single-stage object detector and instance segmentation architecture. YOLOv8n-seg "
         "utilizes a modified CSPDarknet53 backbone with a C2f feature aggregation neck and a prototype mask generation head. Operating with only "
         "3.2 million parameters, YOLOv8n-seg achieves real-time inference (>70 FPS on CPU at small input resolutions), making it exceptionally "
         "suited for edge drone processing."),

        ("Wang et al. (2024) [10]", "YOLOv9: Learning what you want to learn using programmable gradient information",
         "Wang et al. addressed information loss across deep feedforward networks by introducing Programmable Gradient Information (PGI) and "
         "Generalized Efficient Layer Aggregation Networks (GELAN). Evaluated on MS COCO, YOLOv9 achieved superior parameter efficiency. "
         "However, the model was optimized for object bounding box detection and lacks lightweight, real-time instance segmentation heads for edge UAVs."),

        ("Wang et al. (2024) [11]", "YOLOv10: Real-time end-to-end object detection",
         "YOLOv10 eliminated the latency penalty of Non-Maximum Suppression (NMS) by implementing dual-label assignments (one-to-many for training, "
         "one-to-one for inference). While achieving state-of-the-art detection efficiency, official instance segmentation heads remain under active "
         "development, and the model lacks specialized attention heads for irregular, tiny roadside architectural extensions."),

        ("Zhang et al. (2024) [12]", "FFCA-YOLO for small object detection in remote sensing images",
         "Zhang et al. designed FFCA-YOLO to address small, dense object detection in aerial imagery (VisDrone, DOTA). The network incorporates "
         "Feature-Fusion Coordinate Attention (FFCA) and a dedicated small-object detection layer. While achieving significant mAP gains on tiny "
         "vehicles and pedestrians, the network outputs axis-aligned bounding boxes rather than segmented polygon contours, preventing exact "
         "encroachment area calculation."),

        ("Liu et al. (2025) [13]", "MFAE-YOLO: Multifeature attention-enhanced network for remote sensing images object detection",
         "Published in IEEE TGRS, MFAE-YOLO introduces multi-scale receptive field attention to resolve background clutter in complex aerial "
         "scenes. The architecture demonstrates excellent precision in separating natural vegetation from man-made structures. However, the model "
         "shares the standard limitation of being an optical detector devoid of vector cadastral integration."),

        ("Wang et al. (2025) [14]", "SCENE-YOLO: A one-stage remote sensing object detection network with scene supervision",
         "Wang et al. proposed SCENE-YOLO, utilizing scene-level contextual guidance to disambiguate object classes in dense urban environments. "
         "While reducing false detections in complex surroundings, the network cannot differentiate between lawful private structures and "
         "statutory corridor violations because legal boundaries are invisible to optical context heads."),

        ("Verma et al. (2024) [15]", "Urban roadside obstacle detection using mobile laser scanning and deep learning",
         "Verma et al. combined vehicle-mounted Mobile Laser Scanning (MLS) point clouds with YOLOv7 to detect roadside obstacles, utility poles, "
         "and tree branches in urban corridors. While providing millimeter-level 3D spatial measurements, vehicle-mounted LiDAR suffers from severe "
         "occlusion by parked vehicles, cannot observe lateral boundaries behind perimeter walls, and requires prohibitively expensive mobile mapping hardware."),

        ("Fleischmann & Arribas-Bel (2024) [16]", "Spatially explicit deep learning for urban land-use and morphometric classification",
         "This work established spatially explicit Graph Neural Networks (GNNs) combining cadastral vector parcels with satellite rasters for "
         "urban morphometric classification across European cities. The authors proved that urban spatial analysis must treat buildings and parcels "
         "as topologically linked contiguous units. However, their macroscopic approach operates at regional block levels (0.5 m/pixel) and cannot "
         "perform sub-meter edge detection of individual commercial shop frontages.")
    ]

    for ptitle, pfull, pbody in papers:
        add_heading_3(doc, ptitle + ": " + pfull)
        add_body_p(doc, pbody)

    add_heading_2(doc, "2.3 Comparative Analysis of Existing Methods")
    add_body_p(
        doc,
        "Table 2.1 provides a structured comparative synthesis of the analyzed literature against the proposed capstone framework, "
        "evaluating spatial resolution, core methodology, computational overhead, and jurisdictional cadastral boundary awareness."
    )

    # Comparative Table
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    p_tbl_cap = doc.add_paragraph()
    p_tbl_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tc = p_tbl_cap.add_run("Table 2.1: Systematic comparative synthesis of state-of-the-art literature vs. proposed framework")
    r_tc.font.name = "Times New Roman"
    r_tc.font.size = Pt(10)
    r_tc.font.bold = True

    c_table = doc.add_table(rows=1, cols=5)
    c_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Study & Year", "Methodology / Network", "Data Modality / GSD", "Primary Focus", "Cadastral / ROW Awareness"]
    for i, h in enumerate(headers):
        cell = c_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.font.bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    data_rows = [
        ("Yurtseven (2019) [3]", "SfM Photogrammetry (Manual Digitization)", "UAV RGB (<3 cm/px)", "Roadside Asset Inventory", "None (Manual Asset Mapping)"),
        ("He et al. (2017) [4]", "Mask R-CNN (Two-stage proposals)", "Standard Optical (COCO)", "Generic Instance Segmentation", "None (Pure Vision Class)"),
        ("Chen et al. (2024) [7]", "RSPrompter (Foundation Model + SAM)", "Satellite / Aerial (0.5–2.0 m/px)", "Remote Sensing Segmentation", "None (No Vector Integration)"),
        ("Zhang et al. (2024) [12]", "FFCA-YOLO (Coordinate Attention)", "Aerial Drone (VisDrone)", "Tiny Object Bounding Box", "None (Bounding Boxes Only)"),
        ("Verma et al. (2024) [15]", "Mobile Laser Scanning + YOLOv7", "Vehicle Mobile LiDAR (3D)", "Roadside Obstacle Detection", "None (Sensor Occluded by Traffic)"),
        ("Fleischmann (2024) [16]", "Spatially Explicit GNN + CNN", "Cadastre + Satellite (0.5 m/px)", "Urban Morphometric Typology", "Macroscopic Parcel Level Only"),
        ("Proposed Framework", "YOLOv8n-seg + Inverse Affine + Vector Set Algebra", "UAV Survey (~5 cm/px, 1024x723)", "Sub-Meter Road ROW Compliance", "Full Closed-Form Cadastral & ROW Algebra")
    ]

    for row in data_rows:
        r_cells = c_table.add_row().cells
        for col_idx, text in enumerate(row):
            p = r_cells[col_idx].paragraphs[0]
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            if col_idx == 0 and "Proposed" in text:
                r.font.bold = True

    add_heading_2(doc, "2.4 Research Gap")
    add_body_p(
        doc,
        "A rigorous synthesis of the existing literature reveals a clear, persistent research gap at the intersection of deep visual remote "
        "sensing and municipal legal administration:\n\n"
        "1. The Semantic-Legal Disconnect: Advanced deep learning architectures (YOLOv8, YOLOv9, SAM, RSPrompter) predict optical object classes "
        "with exceptional pixel boundary accuracy, but operate in complete isolation from legal property lines and statutory easement boundaries. "
        "Consequently, pure computer vision systems cannot discern whether a detected structure is permissible or unlawful.\n\n"
        "2. The GIS Digitization Bottleneck: Commercial Geographic Information Systems (such as ArcGIS and QGIS) possess robust computational "
        "geometry tools to calculate polygon intersections, but cannot automatically segment physical building structures from dynamic aerial drone feeds in real time.\n\n"
        "3. Lack of Sub-Meter Municipal Attribution: Existing urban monitoring tools fail to partition road corridors into functional zones "
        "(paved carriageway vs. pedestrian sidewalks) or compute legally mandated civil engineering metrics (linear road chainage stationing, "
        "transverse projection depth, and shared frontage width) required to issue formal eviction and notice orders."
    )

    add_heading_2(doc, "2.5 Chapter Summary")
    add_body_p(
        doc,
        "This chapter reviewed 16 major research contributions across UAV remote sensing, deep instance segmentation, and spatial cadastral GIS. "
        "While visual segmentation accuracy and drone photogrammetric capabilities have advanced dramatically, existing systems universally fail "
        "to decouple visual segmentation from statutory cadastral set algebra. The proposed capstone project addresses this precise gap by "
        "establishing a unified, end-to-end framework coupling an edge-optimized YOLOv8n-seg network with a Shapely vector computational geometry "
        "engine, as detailed in Chapter 3."
    )
    doc.add_page_break()
    print("Chapter 2 built successfully.")
