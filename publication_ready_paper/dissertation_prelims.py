import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def build_preliminary_pages(doc):
    # ==========================================
    # PAGE 1: TITLE PAGE
    # ==========================================
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(24)
    run_title = p_title.add_run("Urban Road Encroachment Detection Using Computer Vision and GIS-Based Spatial Analysis")
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D) # Navy Blue

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(18)
    run_sub = p_sub.add_run("A Capstone Project Report submitted in partial fulfilment of the requirements for the degree of\n")
    run_sub.font.name = "Times New Roman"
    run_sub.font.size = Pt(13)
    run_deg = p_sub.add_run("Bachelor of Technology\nin\nInformation Technology")
    run_deg.font.name = "Times New Roman"
    run_deg.font.size = Pt(14)
    run_deg.font.bold = True

    p_subto = doc.add_paragraph()
    p_subto.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subto.paragraph_format.space_before = Pt(12)
    p_subto.paragraph_format.space_after = Pt(12)
    run_subto = p_subto.add_run("Submitted to\n")
    run_subto.font.name = "Times New Roman"
    run_subto.font.size = Pt(12)
    run_inst = p_subto.add_run("SVKM's NMIMS\nMukesh Patel School of Technology Management & Engineering\nShirpur Campus (M.H.), India")
    run_inst.font.name = "Times New Roman"
    run_inst.font.size = Pt(13)
    run_inst.font.bold = True

    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_by.paragraph_format.space_before = Pt(24)
    p_by.paragraph_format.space_after = Pt(8)
    run_by = p_by.add_run("Submitted by:")
    run_by.font.name = "Times New Roman"
    run_by.font.size = Pt(12)
    run_by.font.italic = True

    p_cand = doc.add_paragraph()
    p_cand.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cand.paragraph_format.space_after = Pt(24)
    cands = [
        ("Shreyas Biware", "A216"),
        ("Priyanshu C. Wadnere", "A272"),
        ("Mahak Agrawal", "A262")
    ]
    for name, roll in cands:
        r = p_cand.add_run(f"{name} (Roll No.: {roll})\n")
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True

    p_sup = doc.add_paragraph()
    p_sup.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sup.paragraph_format.space_after = Pt(6)
    r_sup = p_sup.add_run("Under the Supervision of:")
    r_sup.font.name = "Times New Roman"
    r_sup.font.size = Pt(12)
    r_sup.font.italic = True

    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide.paragraph_format.space_after = Pt(36)
    r_gname = p_guide.add_run("Dr. Prashant Udawant\n")
    r_gname.font.name = "Times New Roman"
    r_gname.font.size = Pt(14)
    r_gname.font.bold = True
    r_gdes = p_guide.add_run("Assistant Professor, Department of Information Technology, MPSTME")
    r_gdes.font.name = "Times New Roman"
    r_gdes.font.size = Pt(12)

    p_bot = doc.add_paragraph()
    p_bot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bot.paragraph_format.space_before = Pt(24)
    r_dept = p_bot.add_run("DEPARTMENT OF INFORMATION TECHNOLOGY\nMUKESH PATEL SCHOOL OF TECHNOLOGY MANAGEMENT & ENGINEERING\n")
    r_dept.font.name = "Times New Roman"
    r_dept.font.size = Pt(13)
    r_dept.font.bold = True
    r_sess = p_bot.add_run("ACADEMIC SESSION: 2026–2027")
    r_sess.font.name = "Times New Roman"
    r_sess.font.size = Pt(12)
    r_sess.font.bold = True

    doc.add_page_break()

    # ==========================================
    # PAGE 2: CERTIFICATE
    # ==========================================
    p_cert_title = doc.add_paragraph()
    p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert_title.paragraph_format.space_before = Pt(24)
    p_cert_title.paragraph_format.space_after = Pt(24)
    r_ct = p_cert_title.add_run("CERTIFICATE")
    r_ct.font.name = "Times New Roman"
    r_ct.font.size = Pt(16)
    r_ct.font.bold = True

    p_cert_body = doc.add_paragraph()
    p_cert_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_cert_body.paragraph_format.line_spacing = 1.5
    p_cert_body.paragraph_format.space_after = Pt(18)
    r_cb = p_cert_body.add_run(
        "This is to certify that the capstone project entitled \"Urban Road Encroachment Detection Using Computer Vision "
        "and GIS-Based Spatial Analysis\" has been successfully completed by Shreyas Biware (Roll No.: A216), "
        "Priyanshu C. Wadnere (Roll No.: A272), and Mahak Agrawal (Roll No.: A262) under my guidance and supervision. "
        "This report is submitted in partial fulfilment of the requirements for the degree of Bachelor of Technology in "
        "Information Technology of Mukesh Patel School of Technology Management & Engineering (MPSTME), SVKM’s NMIMS "
        "(Deemed-to-be University), Shirpur Campus (Maharashtra), India, during the academic session 2026–2027.\n\n"
        "It is further certified that the work embodied in this project report represents genuine technical inquiry "
        "and development carried out by the candidates, and has not been submitted in part or full to any other "
        "university or institution for the award of any degree or diploma."
    )
    r_cb.font.name = "Times New Roman"
    r_cb.font.size = Pt(12)

    # Signature table
    sig_table = doc.add_table(rows=3, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_table.autofit = False

    sig_data = [
        ("____________________________", "____________________________"),
        ("Dr. Prashant Udawant\nProject Mentor (Internal Guide)\nAssistant Professor, Dept. of IT", "External Examiner\nDesignation: __________________\nInstitution: __________________"),
        ("Date: ________________________\nPlace: Shirpur", "____________________________\nHead of the Department\nDepartment of Information Technology\nMPSTME, Shirpur Campus")
    ]
    for r_idx, row in enumerate(sig_data):
        cell_l, cell_r = sig_table.rows[r_idx].cells
        cell_l.width = Inches(3.2)
        cell_r.width = Inches(3.2)
        pl = cell_l.paragraphs[0]
        pl.paragraph_format.space_after = Pt(12)
        rl = pl.add_run(row[0])
        rl.font.name = "Times New Roman"
        rl.font.size = Pt(11)
        
        pr = cell_r.paragraphs[0]
        pr.paragraph_format.space_after = Pt(12)
        rr = pr.add_run(row[1])
        rr.font.name = "Times New Roman"
        rr.font.size = Pt(11)

    doc.add_page_break()

    # ==========================================
    # PAGE 3: ACKNOWLEDGEMENT
    # ==========================================
    p_ack_title = doc.add_paragraph()
    p_ack_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ack_title.paragraph_format.space_before = Pt(24)
    p_ack_title.paragraph_format.space_after = Pt(18)
    r_at = p_ack_title.add_run("ACKNOWLEDGEMENT")
    r_at.font.name = "Times New Roman"
    r_at.font.size = Pt(16)
    r_at.font.bold = True

    p_ack = doc.add_paragraph()
    p_ack.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_ack.paragraph_format.line_spacing = 1.5
    p_ack.paragraph_format.space_after = Pt(12)
    p_ack.add_run(
        "After the successful completion of this capstone project work, words are not enough to express our deepest "
        "feelings towards all those who helped us reach our goal; feeling above this is our profound indebtedness to "
        "The Almighty for providing us the perseverance and wisdom throughout this endeavor.\n\n"
        "It is our great pleasure and moment of immense satisfaction to express our profound gratitude to our project "
        "mentor, Dr. Prashant Udawant, Assistant Professor, Department of Information Technology, MPSTME, Shirpur Campus, "
        "whose constant encouragement, insightful technical criticism, and persistent guidance enabled us to work "
        "with technical vigor. His profound expertise in computer vision, spatial computing, and mathematical problem "
        "formulation helped us bridge theoretical concepts into a reproducible engineering pipeline.\n\n"
        "We express our sincere thanks and gratitude to the Head of Department, Department of Information Technology, "
        "MPSTME, Shirpur, for providing the necessary infrastructural, computing, and laboratory facilities to complete "
        "the project work successfully.\n\n"
        "We also extend our deepest gratitude to Dr. Venkat R. Patri, Associate Dean, MPSTME, Shirpur Campus, for "
        "fostering an academic environment dedicated to high-standard research, technical innovation, and professional rigor.\n\n"
        "We sincerely thank all faculty members, laboratory technical assistants, and administrative staff of the "
        "Department of Information Technology, who provided unreserved support throughout our undergraduate program.\n\n"
        "Finally, we wish to express our heartfelt thanks to our parents, families, and peers whose moral support, "
        "patience, and sacrifices were instrumental in the successful completion of this dissertation."
    ).font.name = "Times New Roman"

    p_stud = doc.add_paragraph()
    p_stud.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_stud.paragraph_format.space_before = Pt(24)
    r_st = p_stud.add_run(
        "Shreyas Biware (A216)\n"
        "Priyanshu C. Wadnere (A272)\n"
        "Mahak Agrawal (A262)\n"
        "Department of Information Technology, MPSTME\n"
        "Shirpur Campus, Maharashtra"
    )
    r_st.font.name = "Times New Roman"
    r_st.font.size = Pt(11)
    r_st.font.bold = True

    doc.add_page_break()

    # ==========================================
    # PAGE 4: ABSTRACT
    # ==========================================
    p_abs_title = doc.add_paragraph()
    p_abs_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs_title.paragraph_format.space_before = Pt(24)
    p_abs_title.paragraph_format.space_after = Pt(18)
    r_abst = p_abs_title.add_run("ABSTRACT")
    r_abst.font.name = "Times New Roman"
    r_abst.font.size = Pt(16)
    r_abst.font.bold = True

    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.line_spacing = 1.5
    p_abs.paragraph_format.space_after = Pt(12)
    p_abs.add_run(
        "Rapid, uncoordinated urban densification in developing economies routinely results in unlawful structural "
        "encroachments onto public road corridors, degrading vehicular throughput, obstructing pedestrian right-of-way, "
        "and severely impeding emergency response logistics. Conventional municipal enforcement depends upon manual, "
        "ground-level topographic surveys that are labor-intensive, dispute-prone, and geographically fragmented. "
        "Conversely, purely computer vision-based approaches that frame encroachment as an image segmentation problem "
        "are fundamentally flawed: an awning, veranda, or ramp is an architecturally identical visual pattern whether built "
        "lawfully inside a private setback or unlawfully protruding into the public road corridor. Consequently, encroachment "
        "is a spatial-legal relation rather than an intrinsic visual class.\n\n"
        "This capstone dissertation presents the design, mathematical formulation, empirical implementation, and rigorous "
        "verification of an automated decision-support system that decouples deep visual instance segmentation from cadastral "
        "vector computational geometry. The computer vision subsystem implements an edge-optimized YOLOv8n-seg network "
        "trained to detect physical building components (permanent massings, shop awnings, veranda sheds, ramps, and boundary "
        "walls) from aerial unmanned aerial vehicle (UAV) imagery. An inverse affine homography matrix maps image-space mask "
        "contours into a local metric Cartesian coordinate frame. A vector computational geometry engine then executes boolean "
        "set operations against authoritative cadastral land parcel boundaries and the statutory Road Right-of-Way (ROW), "
        "partitioning the corridor into a 6.00 m paved carriageway and two 1.50 m pedestrian footpaths.\n\n"
        "The complete pipeline is empirically evaluated on an 85-meter urban corridor. The deep learning model achieves an "
        "overall precision of 0.885, recall of 0.842, F1-score of 0.863, and mAP@0.5 of 0.891 across structural classes. "
        "The GIS vector engine isolates two benchmark violations: Case E-01 (an unapproved commercial awning on Parcel P-07 "
        "occupying 6.00 m² with a 1.20 m projection depth and 80.0% footpath obstruction at chainage station 0+011.0) and "
        "Case E-02 (a permanent shop extension on Parcel P-08 occupying 3.60 m² at station 0+023.3), while achieving zero false "
        "alarms on abutting lawful control structures. A comprehensive 86-test automated verification suite confirms end-to-end "
        "topological manifoldness, geometric reversibility, and API responsiveness (13.8 ms CPU latency), establishing a reproducible, "
        "audit-ready decision-support tool for municipal urban governance."
    ).font.name = "Times New Roman"

    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_kw.paragraph_format.space_before = Pt(12)
    r_kwt = p_kw.add_run("Keywords: ")
    r_kwt.font.name = "Times New Roman"
    r_kwt.font.size = Pt(12)
    r_kwt.font.bold = True
    r_kwc = p_kw.add_run("Urban Road Right-of-Way, Cadastral GIS, Deep Instance Segmentation, YOLOv8n-seg, Computational Geometry, Affine Homography, Municipal Spatial Decision Support.")
    r_kwc.font.name = "Times New Roman"
    r_kwc.font.size = Pt(12)
    r_kwc.font.italic = True

    doc.add_page_break()

    # ==========================================
    # PAGE 5: TABLE OF CONTENTS
    # ==========================================
    p_toc_title = doc.add_paragraph()
    p_toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_title.paragraph_format.space_before = Pt(24)
    p_toc_title.paragraph_format.space_after = Pt(18)
    r_toct = p_toc_title.add_run("TABLE OF CONTENTS")
    r_toct.font.name = "Times New Roman"
    r_toct.font.size = Pt(16)
    r_toct.font.bold = True

    toc_table = doc.add_table(rows=1, cols=3)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    toc_table.rows[0].cells[0].paragraphs[0].add_run("Section / Chapter").font.bold = True
    toc_table.rows[0].cells[1].paragraphs[0].add_run("Title").font.bold = True
    toc_table.rows[0].cells[2].paragraphs[0].add_run("Page").font.bold = True

    toc_entries = [
        ("", "Certificate", "ii"),
        ("", "Acknowledgement", "iii"),
        ("", "Abstract", "iv"),
        ("", "List of Figures", "vi"),
        ("", "List of Tables", "vii"),
        ("", "Abbreviations", "viii"),
        ("1.0", "INTRODUCTION", "1"),
        ("1.1", "Background of the Project Topic", "1"),
        ("1.2", "Motivation and Scope of the Report", "3"),
        ("1.3", "Problem Statement", "4"),
        ("1.4", "Salient Contributions", "5"),
        ("1.5", "Organization of the Report", "6"),
        ("2.0", "LITERATURE SURVEY", "8"),
        ("2.1", "Introduction to the Research Area", "8"),
        ("2.2", "Detailed Literature Survey", "9"),
        ("2.3", "Comparative Analysis of Existing Methods", "17"),
        ("2.4", "Research Gap", "20"),
        ("2.5", "Chapter Summary", "21"),
        ("3.0", "METHODOLOGY AND IMPLEMENTATION", "22"),
        ("3.1", "System Architecture and Block Diagram", "22"),
        ("3.2", "Hardware Description", "25"),
        ("3.3", "Software Description, Flowchart / Algorithm", "26"),
        ("3.4", "Dataset Preparation and Ingestion", "28"),
        ("3.5", "Image Preprocessing and Homography Mapping", "30"),
        ("3.6", "Annotation and Quality Assurance Procedures", "32"),
        ("3.7", "Computer Vision Model Architecture", "34"),
        ("3.8", "Training and Inference Pipeline", "37"),
        ("3.9", "Evaluation Methodology", "39"),
        ("3.10", "GIS-Based Spatial Analysis & Vector Algebra", "41"),
        ("3.11", "Dashboard and Decision Support Interface", "44"),
        ("3.12", "Testing and Verification Suite", "46"),
        ("3.13", "Chapter Summary", "48"),
        ("4.0", "RESULTS AND ANALYSIS", "49"),
        ("4.1", "Dataset Audit and Statistics", "49"),
        ("4.2", "Annotation Quality and Class Distribution Audit", "51"),
        ("4.3", "Model Training and Evaluation Metrics", "53"),
        ("4.4", "Detection and Segmentation Results", "56"),
        ("4.5", "GIS Spatial Analysis Results", "58"),
        ("4.6", "Dashboard and System Outputs", "61"),
        ("4.7", "Error Analysis and Sensitivity Evaluation", "63"),
        ("4.8", "Discussion of Findings", "66"),
        ("4.9", "Chapter Summary", "68"),
        ("5.0", "ADVANTAGES, LIMITATIONS AND APPLICATIONS", "69"),
        ("5.1", "Advantages", "69"),
        ("5.2", "Limitations", "71"),
        ("5.3", "Applications", "73"),
        ("5.4", "Chapter Summary", "75"),
        ("6.0", "CONCLUSION AND FUTURE SCOPE", "76"),
        ("6.1", "Summary of Work Completed", "76"),
        ("6.2", "Conclusions Derived from Logical Analysis", "77"),
        ("6.3", "Future Scope and Research Roadmap", "79"),
        ("", "REFERENCES", "81"),
        ("App. A", "Sample Source Code", "86"),
        ("App. B", "Data Sheets & Dataset Specifications", "90"),
        ("App. C", "List of Components, Hardware & Software Inventory", "93"),
        ("App. D", "List of Papers Presented and Published", "95")
    ]

    for sec, title, pg in toc_entries:
        row = toc_table.add_row()
        row.cells[0].paragraphs[0].add_run(sec).font.size = Pt(10)
        row.cells[1].paragraphs[0].add_run(title).font.size = Pt(10)
        row.cells[2].paragraphs[0].add_run(pg).font.size = Pt(10)

    doc.add_page_break()

    # ==========================================
    # PAGE 6: LIST OF FIGURES
    # ==========================================
    p_lof_title = doc.add_paragraph()
    p_lof_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof_title.paragraph_format.space_before = Pt(24)
    p_lof_title.paragraph_format.space_after = Pt(18)
    p_lof_title.add_run("LIST OF FIGURES").font.bold = True

    lof_table = doc.add_table(rows=1, cols=3)
    lof_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    lof_table.rows[0].cells[0].paragraphs[0].add_run("Sr. No.").font.bold = True
    lof_table.rows[0].cells[1].paragraphs[0].add_run("Figure Title").font.bold = True
    lof_table.rows[0].cells[2].paragraphs[0].add_run("Page").font.bold = True

    figs = [
        ("Figure 1.1", "Seven-stage cyber-physical workflow for urban road corridor compliance monitoring", "24"),
        ("Figure 1.2", "Decoupled microservice architecture: Presentation, REST API, Spatial Engine, and Deep Learning Vision Pipeline", "25"),
        ("Figure 3.1", "End-to-end decision and verification flowchart for multi-zone spatial compliance evaluation", "27"),
        ("Figure 3.2", "Inverse affine coordinate registration from pixel space (u, v) to metric cadastral space (X, Y)", "31"),
        ("Figure 4.1", "YOLOv8n-seg mask precision-recall curves across evaluated building structural classes", "54"),
        ("Figure 4.2", "Normalized confusion matrix demonstrating high diagonal accuracy and minimal background false positive leakage", "55"),
        ("Figure 4.3", "Three-stage visual inspection progression along the 85-meter Road R-001 evaluation corridor", "57"),
        ("Figure 4.4", "Detailed 2D engineering vector cross-section of confirmed violation E-01 on Parcel P-07", "60"),
        ("Figure 4.5", "Interactive multi-layer Leaflet GIS municipal decision-support dashboard", "62")
    ]
    for idx, (fnum, ftitle, fpage) in enumerate(figs, start=1):
        row = lof_table.add_row()
        row.cells[0].paragraphs[0].add_run(str(idx)).font.size = Pt(10)
        row.cells[1].paragraphs[0].add_run(f"{fnum}: {ftitle}").font.size = Pt(10)
        row.cells[2].paragraphs[0].add_run(fpage).font.size = Pt(10)

    doc.add_page_break()

    # ==========================================
    # PAGE 7: LIST OF TABLES
    # ==========================================
    p_lot_title = doc.add_paragraph()
    p_lot_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot_title.paragraph_format.space_before = Pt(24)
    p_lot_title.paragraph_format.space_after = Pt(18)
    p_lot_title.add_run("LIST OF TABLES").font.bold = True

    lot_table = doc.add_table(rows=1, cols=3)
    lot_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    lot_table.rows[0].cells[0].paragraphs[0].add_run("Sr. No.").font.bold = True
    lot_table.rows[0].cells[1].paragraphs[0].add_run("Table Title").font.bold = True
    lot_table.rows[0].cells[2].paragraphs[0].add_run("Page").font.bold = True

    tbls = [
        ("Table 2.1", "Systematic comparative synthesis of state-of-the-art literature vs. proposed framework", "18"),
        ("Table 3.1", "Corridor hardware development and edge-deployment specifications", "26"),
        ("Table 3.2", "Software frameworks, libraries, versions, and architectural responsibilities", "27"),
        ("Table 3.3", "YOLOv8n-seg network hyperparameter configuration and training schedule", "38"),
        ("Table 4.1", "Sequence-level dataset partitioning and structural class instance distribution", "50"),
        ("Table 4.2", "Comprehensive quality assurance and anomaly verification audit summary", "52"),
        ("Table 4.3", "YOLOv8n-seg instance segmentation evaluation metrics on held-out test split (R001_SEQ03)", "54"),
        ("Table 4.4", "Spatial engine geometric compliance metrics against ground-truth benchmarks and control properties", "59"),
        ("Table 4.5", "End-to-end CPU execution latency breakdown per candidate structural instance", "65")
    ]
    for idx, (tnum, ttitle, tpage) in enumerate(tbls, start=1):
        row = lot_table.add_row()
        row.cells[0].paragraphs[0].add_run(str(idx)).font.size = Pt(10)
        row.cells[1].paragraphs[0].add_run(f"{tnum}: {ttitle}").font.size = Pt(10)
        row.cells[2].paragraphs[0].add_run(tpage).font.size = Pt(10)

    doc.add_page_break()

    # ==========================================
    # PAGE 8: ABBREVIATIONS
    # ==========================================
    p_abb_title = doc.add_paragraph()
    p_abb_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abb_title.paragraph_format.space_before = Pt(24)
    p_abb_title.paragraph_format.space_after = Pt(18)
    p_abb_title.add_run("ABBREVIATIONS").font.bold = True

    abb_table = doc.add_table(rows=1, cols=2)
    abb_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    abb_table.rows[0].cells[0].paragraphs[0].add_run("Abbreviation").font.bold = True
    abb_table.rows[0].cells[1].paragraphs[0].add_run("Full Form / Definition").font.bold = True

    abbs = [
        ("AI", "Artificial Intelligence"),
        ("API", "Application Programming Interface"),
        ("CNN", "Convolutional Neural Network"),
        ("CRS", "Coordinate Reference System"),
        ("CSV", "Comma-Separated Values"),
        ("DGPS", "Differential Global Positioning System"),
        ("DPI", "Dots Per Inch"),
        ("DSM", "Digital Surface Model"),
        ("GIS", "Geographic Information System"),
        ("GPS", "Global Positioning System"),
        ("GSD", "Ground Sampling Distance"),
        ("GUI", "Graphical User Interface"),
        ("HTTP", "Hypertext Transfer Protocol"),
        ("IEEE", "Institute of Electrical and Electronics Engineers"),
        ("IoU", "Intersection over Union"),
        ("JSON", "JavaScript Object Notation"),
        ("LiDAR", "Light Detection and Ranging"),
        ("mAP", "Mean Average Precision"),
        ("MBR", "Minimum Bounding Rectangle"),
        ("MLS", "Mobile Laser Scanning"),
        ("NMS", "Non-Maximum Suppression"),
        ("OGC", "Open Geospatial Consortium"),
        ("PR", "Precision-Recall"),
        ("RAM", "Random Access Memory"),
        ("REST", "Representational State Transfer"),
        ("RGB", "Red, Green, Blue"),
        ("ROW", "Right-of-Way"),
        ("R-tree", "Rectangle Tree (Spatial Index)"),
        ("SAM", "Segment Anything Model"),
        ("SQLite", "Structured Query Language (Self-Contained RDBMS)"),
        ("SVAMITVA", "Survey of Villages and Mapping with Improvised Technology in Village Areas"),
        ("TPS", "Thin-Plate Spline"),
        ("UAV", "Unmanned Aerial Vehicle"),
        ("VHR", "Very High Resolution"),
        ("WKT", "Well-Known Text"),
        ("YOLO", "You Only Look Once")
    ]
    for short, long_desc in abbs:
        row = abb_table.add_row()
        row.cells[0].paragraphs[0].add_run(short).font.size = Pt(10)
        row.cells[1].paragraphs[0].add_run(long_desc).font.size = Pt(10)

    doc.add_page_break()
    print("Preliminary pages built successfully.")
