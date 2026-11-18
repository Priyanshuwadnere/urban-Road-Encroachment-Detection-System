# Urban Road Encroachment Detection Using Computer Vision and GIS-Based Spatial Analysis
## Final-Year B.Tech Information Technology Capstone Presentation & Complete Defense Guide
### SVKM's NMIMS University | MPSTME Shirpur Campus | Academic Session 2026–2027

---

### Project & Author Metadata
* **Title:** Urban Road Encroachment Detection Using Computer Vision and GIS-Based Spatial Analysis
* **Degree:** Bachelor of Technology in Information Technology
* **Institution:** SVKM's NMIMS, Mukesh Patel School of Technology Management & Engineering (MPSTME), Shirpur Campus, Maharashtra, India
* **Department:** Department of Information Technology
* **Academic Session:** 2026–2027
* **Project Team Members:**
  * **Shreyas Biware** — Roll No.: A216
  * **Priyanshu C. Wadnere** — Roll No.: A272
  * **Mahak Agrawal** — Roll No.: A262
* **Project Supervisor:** **Dr. Prashant Udawant**, Assistant Professor, Department of Information Technology, MPSTME
* **Generated Presentation File:** [`Urban_Road_Encroachment_Detection_Capstone_Presentation.pptx`](file:///e:/Urban%20Road%20Encroachment%20Detection%20System/Urban_Road_Encroachment_Detection_Capstone_Presentation.pptx) (22 Slides, 16:9 Widescreen)

---

## Complete Slide-by-Slide Index & Defense Guide

### Slide 1: Title Slide (Opening Defense)
* **Visual Elements:** NMIMS Crimson header banner, SVKM's NMIMS University & MPSTME Shirpur institutional branding, Navy Blue main title, project subtitle, student team table with roll numbers, supervisor designation.
* **What it explains:** Formal opening slide establishing the institution, department, project title, student team, faculty guide, and academic session.
* **45–60 Second Speaking Script:**
  > "Good morning respected evaluators, external examiners, and faculty members. Today, our team—Shreyas Biware, Priyanshu Wadnere, and Mahak Agrawal—under the mentorship of Dr. Prashant Udawant, presents our final-year B.Tech Information Technology capstone project: *'Urban Road Encroachment Detection Using Computer Vision and GIS-Based Spatial Analysis'*. In this project, we address a persistent municipal governance challenge across Indian urban local bodies—unauthorized structural encroachments into public road corridors. We propose a decoupled, test-driven spatial decision-support system that bridges deep instance segmentation with legal cadastral geometry."
* **Key Technical Concepts:** Interdisciplinary synthesis of deep learning (YOLOv8n-seg), UAV aerial remote sensing, and GIS cadastral vector analysis.
* **Likely Viva Question & Answer:**
  * **Q:** *Why is pure computer vision alone inadequate for municipal road encroachment detection?*
  * **A:** *Computer vision models detect only physical optical boundaries. They possess zero intrinsic awareness of statutory property boundaries or legal road rights-of-way. A structure detected outside a private parcel can only be confirmed as an encroachment through computational geometry against gazetted cadastral vectors.*

---

### Slide 2: Presentation Index & Chapter Flow
* **Visual Elements:** Structured two-column card layout displaying the 14 sections mapped across all 22 slides.
* **What it explains:** Structural agenda dividing the defense into 14 distinct sections, ensuring comprehensive alignment with university evaluation standards.
* **45–60 Second Speaking Script:**
  > "This presentation is systematically organized into 14 core sections. We begin with the municipal problem statement, literature survey, and identified research gaps. We then delineate our two major engineering objectives: Objective 1 focuses on deep learning instance segmentation using YOLOv8n-seg, while Objective 2 formalizes GIS coordinate homography and vector set algebra. We conclude with empirical evaluations on ground-truth benchmark corridors, our decision dashboard, our submitted IEEE conference paper, and an open technical defense."
* **Key Technical Concepts:** Linear, transparent dissertation progression from problem definition to mathematical formulation, empirical verification, and peer review.
* **Likely Viva Question & Answer:**
  * **Q:** *How is the project work divided among the team members?*
  * **A:** *The project was executed collaboratively across three specialized modules: Shreyas Biware led the computer vision annotation pipeline and YOLOv8n-seg training; Priyanshu Wadnere engineered the GIS spatial set algebra, affine homography, and database backend; and Mahak Agrawal directed dataset quality auditing, frontend Leaflet visualization, and the 86-test automated verification suite.*

---

### Slide 3: 1. Introduction | Urban Infrastructure & Civic Governance Challenge
* **Visual Elements:** Dual card layout: (Left) The Municipal Corridor Reality; (Right) The Operational & Technological Crisis.
* **What it explains:** Urban road corridor management, the nature of structural encroachments, current enforcement bottlenecks, and the role of UAV photogrammetry.
* **45–60 Second Speaking Script:**
  > "Urban roadways are statutory public easements critical for civic economy and safety. In rapidly expanding Indian municipalities, public road corridors suffer from chronic structural encroachments—commercial establishments and residents build awnings, ramps, and veranda sheds into gazetted road rights-of-way. Conventional enforcement relies on manual physical inspections by municipal junior engineers with measuring tapes. These surveys are slow, dispute-prone, and lack immutable georeferenced evidence. When eviction notices are issued, property owners routinely stay them in civil court. Our project leverages drone photogrammetry and cadastral GIS to generate an objective, mathematically verifiable evidence base."
* **Key Technical Concepts:** Road Right-of-Way (ROW), functional zoning (carriageway vs. sidewalk), manual survey limitations, UAV photogrammetry benefits.
* **Likely Viva Question & Answer:**
  * **Q:** *What is the legal definition of a Road Right-of-Way (ROW)?*
  * **A:** *Under the Indian Roads Congress (IRC:86-1983) and Municipal Corporation Acts, the Road Right-of-Way (ROW) is the entire statutory width of land legally acquired and gazetted for public transit, encompassing the paved carriageway, shoulders, curbs, pedestrian footpaths, and utility margins. Any private structure projecting beyond the property boundary into this corridor constitutes a statutory encroachment.*

---

### Slide 4: 2. Problem Statement | The Gap Between Visual Detection & Legal Compliance
* **Visual Elements:** Prominent problem statement banner followed by three technical dilemma cards (Semantic-Legal Disconnect, Sub-Meter Precision, Evidence Admissibility).
* **What it explains:** The core problem statement broken down into the semantic-legal disconnect, sub-meter spatial precision requirements, and judicial evidence admissibility.
* **45–60 Second Speaking Script:**
  > "Our problem statement addresses the fundamental disconnect between visual computer vision and statutory municipal law. State-of-the-art computer vision models like YOLO or Mask R-CNN can segment a building or an awning with high accuracy, but they operate blind to property lines. A shed built within private property is completely legal, but an identical shed extending onto a public sidewalk is an illegal encroachment. Computer vision alone cannot determine legality. Furthermore, because encroachments are sub-meter projections, coarse bounding boxes fail completely. Finally, municipal authorities cannot issue demolition notices without verifiable cadastral parcel attribution and linear road chainage."
* **Key Technical Concepts:** Semantic-legal disconnect, sub-meter spatial precision requirements, evidence admissibility under municipal law.
* **Likely Viva Question & Answer:**
  * **Q:** *Can bounding box object detection (like YOLOv8-det) be used instead of instance segmentation?*
  * **A:** *No. Bounding boxes are rectangular approximations that inherently encompass empty sidewalk space, road surface, and adjacent parcels. Applying GIS intersection to a rectangular box produces massive false-positive encroachments. Only pixel-accurate instance segmentation masks isolate true physical boundaries.*

---

### Slide 5: 3. Literature Review | Systematic State-of-the-Art Comparison Matrix
* **Visual Elements:** Comprehensive 7-row academic comparison table covering Yurtseven (2019), He et al. (2017), Chen et al. (2024), Zhang et al. (2024), Verma et al. (2024), Fleischmann (2024), and our Proposed Framework.
* **What it explains:** Comparative synthesis evaluating state-of-the-art literature across data modalities, networks, objectives, and cadastral boundary awareness.
* **45–60 Second Speaking Script:**
  > "To situate our contribution within the scientific literature, we conducted a systematic review across three domains. As shown in our comparison matrix, classical UAV photogrammetry studies like Yurtseven relied on manual digitization. Deep learning studies like Mask R-CNN by He et al. and RSPrompter by Chen et al. made tremendous strides in visual segmentation, but completely lack cadastral vector awareness. Zhang's FFCA-YOLO is restricted to bounding boxes, which cannot model narrow overhangs. Verma used mobile LiDAR, but vehicular sensors are blocked by parked cars and lack land ownership layers. Fleischmann combined GNNs with cadastre, but only at macro parcel scales. Our proposed framework is the first to couple sub-meter YOLOv8n-seg masks with closed-form cadastral set algebra."
* **Key Technical Concepts:** Comparative literature synthesis, state-of-the-art limitations, lack of legal cadastral coupling in vision models.
* **Likely Viva Question & Answer:**
  * **Q:** *How does your work differ from recent Foundation Models like SAM (Segment Anything Model) in remote sensing?*
  * **A:** *While SAM and RSPrompter produce high-quality zero-shot masks, they are computationally heavy (hundreds of millions of parameters) and require visual prompting. More importantly, they output uncalibrated pixel masks without real-world metric scaling, coordinate homography, or cadastral boundary awareness. Our system is edge-deployable (3.2M params) and performs automated legal spatial attribution.*

---

### Slide 6: 3. Literature Review | Thematic Synthesis across 3 Technological Pillars
* **Visual Elements:** Three thematic vertical cards detailing: (1) Aerial Remote Sensing & Drone Photogrammetry, (2) Deep Learning Instance Segmentation, and (3) Cadastral GIS & Computational Geometry.
* **What it explains:** The three foundational technological pillars and how their convergence addresses past remote sensing bottlenecks.
* **45–60 Second Speaking Script:**
  > "Our methodology synthesizes three distinct technological pillars. The first pillar is UAV photogrammetry, which provides the sub-5 cm ground sampling distance necessary to detect narrow shop extensions, overcoming the resolution limits of satellite imaging. The second pillar is real-time instance segmentation. We adopt YOLOv8n-seg because its single-stage Protonet architecture predicts polygonal masks in under 10 milliseconds, which is vital for edge deployment. The third pillar is cadastral computational geometry. Thanks to digital land records under schemes like SVAMITVA, statutory property and road boundaries are accessible as vector layers. By uniting these three pillars, our framework transforms raw drone pixels into legally actionable GIS evidence."
* **Key Technical Concepts:** UAV photogrammetry GSD, YOLOv8n-seg Protonet branch, OGC-compliant vector set algebra, SVAMITVA digital land records.
* **Likely Viva Question & Answer:**
  * **Q:** *What is Ground Sampling Distance (GSD) and why is it critical here?*
  * **A:** *Ground Sampling Distance (GSD) is the real-world distance between the centers of two consecutive image pixels. In satellite imagery, GSD is typically 30 to 50 cm, meaning a 60 cm awning occupies barely two pixels and cannot be delineated. In our UAV survey, GSD is approximately 5.45 cm per pixel, allowing precise sub-meter contour extraction.*

---

### Slide 7: 4. Research Gap | Critical Deficiencies in Current Methodologies
* **Visual Elements:** Dual deep-dive cards: Gap 1 (The Semantic-Legal Disconnect) and Gap 2 (Lack of Sub-Meter Municipal Attribution & Functional Zoning).
* **What it explains:** The precise, defensible research gaps motivating the capstone project.
* **45–60 Second Speaking Script:**
  > "Our investigation identifies two critical research gaps. First, the Semantic-Legal Disconnect: existing computer vision research focuses entirely on improving detection benchmarks on datasets like VisDrone or SpaceNet. However, these models operate in complete isolation from property boundaries. A vision model cannot know if a shed is legal or illegal. Naive buffering causes severe false positives against lawful properties. Second, the lack of Sub-Meter Municipal Attribution: current systems treat roads as generic collision polygons without attributing encroachments to specific tax parcels or functional zones like sidewalks. In municipal governance, an eviction notice requires exact parcel identification, chainage stationing, and projection depth. Our project directly bridges these two gaps."
* **Key Technical Concepts:** Decoupled spatial set algebra, municipal property attribution, linear road chainage stations, functional zoning.
* **Likely Viva Question & Answer:**
  * **Q:** *What do you mean by 'Decoupled Spatial Architecture'?*
  * **A:** *It means strictly separating the perception layer from the legal evaluation layer. The deep learning model is responsible solely for delineating physical pixels without attempting to predict legality. The GIS computational geometry layer takes those physical polygons and evaluates them against statutory cadastral boundaries. This guarantees mathematical transparency and prevents model hallucinations from creating unlawful penalties.*

---

### Slide 8: 5. Objectives | Primary Engineering & Research Goals
* **Visual Elements:** Central project aim card, followed by two structured columns detailing Objective 1 (CV Instance Segmentation) and Objective 2 (GIS Spatial Set Algebra & Decision-Support).
* **What it explains:** Clear, measurable engineering objectives aligned with both phases of project execution.
* **45–60 Second Speaking Script:**
  > "Our project is structured around two clear, complementary engineering objectives. Objective 1 addresses the computer vision pipeline: curating an audited 90-frame aerial dataset across an 8-class taxonomy, and training an edge-optimized YOLOv8n-seg model to accurately delineate physical structures from nadir drone viewpoints. Objective 2 addresses the geospatial and civic compliance pipeline: formulating an affine coordinate homography to bridge camera pixels to ground meters, executing closed-form vector set algebra to isolate encroachments into the road right-of-way, computing engineering chainage stations, and deploying a responsive municipal web dashboard verified by an automated 86-test suite."
* **Key Technical Concepts:** Two-stage objective structure, YOLOv8n-seg physical contouring, affine homography, vector set algebra, civil engineering chainage.
* **Likely Viva Question & Answer:**
  * **Q:** *Why did you choose YOLOv8n-seg instead of Mask R-CNN or Faster R-CNN?*
  * **A:** *Mask R-CNN is a two-stage proposal-based network with over 44 million parameters and high inference latency (~120 ms on CPU), making real-time drone or edge video processing unfeasible. YOLOv8n-seg has only 3.2 million parameters and executes inference in 8.2 ms on standard CPU hardware, while retaining high mask accuracy through its PANet and Protonet prototype mask heads.*

---

### Slide 9: 6. Project Timeline | 16-Week Capstone Engineering Roadmap
* **Visual Elements:** High-resolution Gantt chart graphic (`fig_gantt_chart.png`) paired with a 16-week milestone summary table.
* **What it explains:** The 16-week project lifecycle from problem definition (July 13, 2026) to final dissertation defense (October 30, 2026).
* **45–60 Second Speaking Script:**
  > "This slide presents our project development timeline spanning 16 academic weeks from July 13 to October 30, 2026. The project progressed through four distinct phases: Weeks 1 to 4 established problem formulation, exhaustive literature review, and dataset curation of 90 drone frames. Weeks 4 to 11 were dedicated to deep learning model development, polygon annotation auditing, and YOLOv8n-seg training. Weeks 11 to 14 focused on coordinate transformation, spatial engine algebra, full-stack dashboard integration, and authoring our IEEE conference paper. The final two weeks were devoted to comprehensive test-driven verification, black book documentation, and final presentation design."
* **Key Technical Concepts:** Gantt chart scheduling, sequential multi-stage delivery, milestone tracking, deadline adherence.
* **Likely Viva Question & Answer:**
  * **Q:** *What was the most challenging phase of the project timeline?*
  * **A:** *The most critical phase was Weeks 4 to 11, specifically resolving the class imbalance during annotation auditing and calibrating the affine coordinate transformation matrix to ensure that pixel segmentation errors did not propagate into false GIS boundary violations.*

---

### Slide 10: 7. Objective 1: Methodology | System Architecture & Dataset Pipeline
* **Visual Elements:** High-resolution End-to-End System Architecture workflow diagram (`fig1_workflow.jpg`) paired with dataset specifications and quality audit details.
* **What it explains:** Dataset sequence partitioning, Ground Sampling Distance (5.45 cm/px), the 8-class architectural taxonomy, and the comprehensive 551-instance audit ledger.
* **45–60 Second Speaking Script:**
  > "Here we outline our Computer Vision methodology. As shown in the workflow diagram, the pipeline ingests raw UAV survey frames, applies preprocessing, and feeds them into our instance segmentation model. Our dataset comprises 90 aerial frames divided into three strict 30-frame sequence splits—Train, Validation, and Test—to avoid storyboard data leakage. We defined an 8-class architectural taxonomy covering structures relevant to road corridors: buildings, compound walls, entrance ramps, shop extensions, awnings, and sheds. An exhaustive quality control audit verified 551 polygon instances across the dataset, ensuring exact vertex coordinates and label syntax."
* **Key Technical Concepts:** Sequence-level split to prevent data leakage, 8-class physical taxonomy, GSD calibration (5.45 cm/px), dataset audit ledger.
* **Likely Viva Question & Answer:**
  * **Q:** *Why did you split the dataset by sequence rather than random frame shuffling?*
  * **A:** *In video or continuous drone flights, consecutive frames are highly correlated (separated by only 2 meters in our sequence). If we shuffled frames randomly into train and test splits, the model would be tested on near-identical frames it had already seen during training, causing severe data leakage and artificially inflated accuracy. Strict sequence-level splitting ensures true generalization.*

---

### Slide 11: 7. Objective 1: Methodology | YOLOv8n-seg Deep Architecture & Training
* **Visual Elements:** High-resolution dual-pipeline architecture diagram (`fig2_architecture_workflow.png`) alongside network component specifications and multi-task loss formulation.
* **What it explains:** Internal neural architecture of YOLOv8n-seg, its C2f backbone, PANet multi-scale feature neck, anchor-free decoupled heads, Protonet mask branch, and multi-task loss functions.
* **45–60 Second Speaking Script:**
  > "Now let us look at the internal deep learning architecture. We deployed YOLOv8n-seg, the nano instance segmentation network containing just 3.2 million parameters. Its backbone utilizes C2f modules, which combine high-level semantics with low-level spatial detail while maintaining computational efficiency. The neck uses a Path Aggregation Network to fuse features across three spatial scales: P3 for small objects like ramps and awnings, and P5 for large building complexes. The segment head is anchor-free: instead of rigid bounding boxes, it predicts 32 prototype mask coefficients that are linearly combined with Protonet mask tensors. The network is trained with a multi-task loss combining Complete IoU, Distribution Focal Loss, and Binary Cross-Entropy mask loss."
* **Key Technical Concepts:** YOLOv8n-seg C2f blocks, PANet feature pyramid, Protonet prototype masks, anchor-free detection, multi-task loss.
* **Likely Viva Question & Answer:**
  * **Q:** *How does YOLOv8n-seg generate segmentation masks compared to Mask R-CNN?*
  * **A:** *Mask R-CNN uses a two-stage approach: it first generates Region Proposals (RPN) and then runs a small FCN (Fully Convolutional Network) on each RoI to predict a 28x28 mask. This is computationally expensive. YOLOv8n-seg uses a single-stage Protonet: it predicts 32 full-resolution prototype masks for the entire image in parallel, and the detection head simply outputs 32 linear scalar coefficients per instance. Multiplying these coefficients by the prototype masks yields the final polygon instantly.*

---

### Slide 12: 8. Objective 1: Results | Quantitative Metrics & Convergence Analysis
* **Visual Elements:** High-resolution Mask Precision-Recall Curve (`fig4_mask_pr_curve.png`) and comprehensive quantitative evaluation table (Table 4.3).
* **What it explains:** Quantitative metrics on the held-out test split (R001_SEQ03), showing Precision (0.885), Recall (0.842), F1-score (0.863), mAP@0.5 (0.891), and training loss convergence.
* **45–60 Second Speaking Script:**
  > "Turning to our experimental results for Objective 1, the model was evaluated on the held-out test sequence R001_SEQ03 comprising 185 annotated instances. The model achieved an overall micro-average Precision of 88.5%, Recall of 84.2%, and an mAP@0.5 of 0.891. For the dominant building class, Precision reached 91.2% with mAP of 0.915. For infrastructure classes like compound walls and ramps, mAP exceeded 0.84. As seen in the Precision-Recall curve on the left, the area under the curve is consistent across confidence thresholds. Training loss curves confirmed smooth monotonic convergence without overfitting or gradient instability."
* **Key Technical Concepts:** Precision, Recall, F1-score, mAP@0.5, loss curve convergence, generalization on held-out test split.
* **Likely Viva Question & Answer:**
  * **Q:** *What is the difference between mAP@0.5 and mAP@0.5:0.95?*
  * **A:** *mAP@0.5 measures mean Average Precision at a single IoU (Intersection-over-Union) threshold of 0.50, reflecting whether an object is correctly detected. mAP@0.5:0.95 averages precision across 10 IoU thresholds from 0.50 to 0.95 in steps of 0.05. It is a much stricter metric evaluating the exact millimeter boundary alignment of the segmentation mask.*

---

### Slide 13: 8. Objective 1: Results | Visual Qualitative Predictions & Failure Modes
* **Visual Elements:** Visual model predictions batch (`val_batch0_pred.jpg`) showcasing predicted masks against ground truth, accompanied by boundary fidelity analysis and honest failure mode breakdown.
* **What it explains:** Visual segmentation fidelity, followed by an honest analysis of remote sensing constraints: low-resolution boundary smoothing, relief displacement, and class imbalance.
* **45–60 Second Speaking Script:**
  > "Looking at the qualitative prediction batch on the left, the model successfully produces sharp, watertight polygons around rooftops and structural interfaces, avoiding the rectangular background leakage typical of bounding boxes. In academic honesty, we must also examine our failure modes. First, at low tile resolutions, thin features like awning poles exhibit minor boundary dilation. Second, oblique drone angles produce relief displacement, where taller building roofs appear shifted relative to their foundations. Third, class imbalance: buildings comprise over 65% of annotations, which naturally yielded higher precision than rare classes like verandas. Recognizing these limitations is precisely why our GIS stage is designed to filter noise."
* **Key Technical Concepts:** Visual mask fidelity, relief displacement in aerial imagery, low-resolution blurring, class imbalance impact.
* **Likely Viva Question & Answer:**
  * **Q:** *What is relief displacement and how does it affect encroachment detection?*
  * **A:** *Relief displacement is an optical geometric distortion in aerial photography where the tops of tall objects are displaced radially outward from the nadir point relative to their base. If a building is 10 meters tall and photographed obliquely, its roofline appears shifted by several decimeters into the street. We mitigate this by using orthorectified nadir viewpoints and enforcing a 0.50 m² area threshold.*

---

### Slide 14: 9. Objective 2: Methodology | 2D Affine Homography & Coordinate Transformation
* **Visual Elements:** Cadastral survey baseline visual (`fig3a_cadastral_baseline.jpg`) paired with mathematical matrix formulation and ground sampling calibration parameters.
* **What it explains:** Mathematical coordinate transformation bridging raw camera pixel space $(u, v)$ to statutory metric ground space $(X, Y)$ via a calibrated 2D affine homography matrix.
* **45–60 Second Speaking Script:**
  > "Moving to Objective 2, our first challenge is translating detected pixel masks into real-world statutory coordinates. An aerial camera records in discrete pixel space (u, v), while municipal GIS records exist in statutory metric coordinates (X, Y). We formulate a 2D affine transformation matrix that incorporates scaling, translation, and axis orientation. Our Ground Sampling Distance is calibrated at 0.0545 meters per pixel, with the road centerline datum established at u equals 475 pixels corresponding to X equals 24.5 meters. Because the determinant of the affine matrix is strictly non-zero, the transformation is perfectly invertible. This allows two-way projection between the drone video and the cadastral database with sub-millimeter precision."
* **Key Technical Concepts:** 2D Affine Homography, camera pixel coordinates vs. metric ground coordinates, GSD scaling, matrix invertibility.
* **Likely Viva Question & Answer:**
  * **Q:** *Why use an affine transformation instead of a full 8-parameter projective homography?*
  * **A:** *Projective homography is required when the camera viewpoint is heavily tilted with severe perspective convergence. In our nadir aerial survey, the camera optical axis is orthogonal to the ground plane (pitch = 90°), and the terrain across the 180 m study corridor is planar. Under these photogrammetric conditions, the 6-parameter affine transformation preserves parallel lines and collinearity while avoiding projective singularities and parameter overfitting.*

---

### Slide 15: 9. Objective 2: Methodology | GIS Spatial Set Algebra & Encroachment Logic
* **Visual Elements:** High-resolution spatial set algebra diagram (`fig3_encroachment_attribution.png`) illustrating Rule 1 ($O = S \setminus P^*$) and Rule 2 ($E = O \cap R_{\text{ROW}}$), alongside linear chainage and severity criteria.
* **What it explains:** The two-stage GIS spatial set algebra rules (Difference and Intersection), extraction of civil engineering metrics, and severity tier classification.
* **45–60 Second Speaking Script:**
  > "Once physical polygons are mapped to metric space, our spatial engine applies two-stage topological set algebra. In Stage 1, we compute the set difference between the detected structure S and the legal property boundary P-star. If the result O is empty, the structure sits 100% within private bounds and is marked permissible. If O is non-empty, Stage 2 intersects this protruding polygon with the gazetted Road Right-of-Way. If the intersection area exceeds a noise threshold of 0.50 square meters, it is flagged as a potential encroachment. The engine then extracts key municipal metrics: linear road chainage along the centerline, frontage width, max projection depth, and assigns a severity tier—Critical, High, or Moderate—based on sidewalk obstruction."
* **Key Technical Concepts:** Planar topological set algebra (difference and intersection), linear chainage calculation, projection depth, severity classification.
* **Likely Viva Question & Answer:**
  * **Q:** *Why do you apply an area threshold of 0.50 m² before flagging an encroachment?*
  * **A:** *In aerial remote sensing, minor edge noise, optical blooming, and GPS registration tolerance create minute boundary fluctuations of 1 to 2 pixels (5 to 10 cm). Without an area threshold, minor roof gutters or sensor noise would trigger hundreds of false municipal alarms. A 0.50 m² threshold cleanly filters noise while catching real architectural encroachments like 0.80 m sheds and 1.20 m awnings.*

---

### Slide 16: 10. Objective 2: Results | Benchmark Encroachment Attribution Metrics
* **Visual Elements:** High-resolution Encroachment Attribution overlay (`fig3c_encroachment_attribution.jpg`) alongside Table 4.4 reporting verified geometric compliance metrics against ground-truth benchmarks.
* **What it explains:** Empirical validation of the GIS spatial engine against ground-truth benchmarks and control properties (Table 4.4).
* **45–60 Second Speaking Script:**
  > "Slide 16 presents the empirical validation of our spatial engine against ground-truth benchmarks. The engine correctly isolated two active structural encroachments: Case E-01 on Parcel P-07, an awning projecting 1.20 meters into the sidewalk with a computed area of exactly 6.00 square meters; and Case E-02 on Parcel P-08, a veranda shed projecting 0.80 meters with a computed area of exactly 3.60 square meters. The error against benchmark geometry is 0.00 square meters. Equally important, for control properties like P-01, P-02, and P-06 that have lawful building setbacks, the engine returned exactly 0.00 square meters. This proves zero false positives against compliant properties."
* **Key Technical Concepts:** Benchmark geometric compliance, area accuracy, projection depth measurement, zero false positive rate on setbacks.
* **Likely Viva Question & Answer:**
  * **Q:** *Why did E-01 and E-02 achieve exactly 0.00 m² error?*
  * **A:** *Because E-01 and E-02 are synthetic ground-truth reference benchmark cases defined by calibrated survey geometry. Evaluating them verified the mathematical correctness of our Shapely computational geometry engine and affine homography formulas, proving that the geometric engine introduces zero numerical distortion.*

---

### Slide 17: 10. Objective 2: Results | Decision-Support Dashboard & Verification Flow
* **Visual Elements:** GIS Dashboard map render (`gis_map_render.png`) alongside full-stack architecture specifications (FastAPI, SQLite, Leaflet.js), latency breakdown (13.8 ms), and municipal verification workflow.
* **What it explains:** The full-stack web decision-support system, end-to-end execution latency (13.8 ms), and the 5-step municipal enforcement workflow.
* **45–60 Second Speaking Script:**
  > "To make our research actionable for municipal governance, we implemented an interactive web decision-support dashboard. The backend is built with FastAPI and SQLite, providing RESTful endpoints for spatial layers, property records, and summary reports. The frontend features Leaflet.js with two viewing modes: a Survey Alignment View overlaying orthophotos, and a Vector Cadastral View displaying parcels 1 through 10 with permanent house numbers and red violation tags. Crucially, as documented in Table 4.5, our entire pipeline executes in just 13.8 milliseconds per instance on standard CPU hardware, with YOLO inference taking 8.2 ms and vector operations taking 4.2 ms. This proves the system can run directly on edge devices in municipal patrol vans."
* **Key Technical Concepts:** FastAPI REST architecture, Leaflet.js dual view modes, CPU execution latency (13.8 ms), municipal field verification workflow.
* **Likely Viva Question & Answer:**
  * **Q:** *How does this system fit into the actual legal procedure of an Indian municipal corporation?*
  * **A:** *The system functions strictly as a decision-support tool, not an automated demolition trigger. When a potential encroachment is flagged, the system generates a standardized Inspection Sheet containing parcel ID, owner name, chainage, frontage, and projection depth. A municipal junior engineer visits the site for ground truthing. If verified, the immutable digital record serves as unshakeable technical evidence in court under the Municipal Corporation Act.*

---

### Slide 18: 11. Conclusion | Research Summary, Honest Limitations & Future Scope
* **Visual Elements:** Structured three-card synthesis: Key Research Contributions, Honest Limitations, and Future Development Roadmap.
* **What it explains:** Core research conclusions, honest technical limitations, and a prioritized roadmap for future municipal scaling.
* **45–60 Second Speaking Script:**
  > "In conclusion, our capstone project successfully demonstrates that uniting deep instance segmentation with cadastral computational geometry provides an objective, automated, and mathematically verifiable solution for urban road encroachment detection. Our decoupled spatial architecture achieves 89.1% mAP while guaranteeing zero false penalization against lawful property setbacks, executing in just 13.8 milliseconds. In terms of limitations, our prototype was evaluated on calibrated synthetic drone corridors, and oblique angles introduce relief displacement. In our future scope, we plan to incorporate UAV LiDAR point clouds to measure vertical headroom clearance and integrate directly with national SVAMITVA digital land registry APIs."
* **Key Technical Concepts:** Research synthesis, decoupled architecture benefits, honest limitations disclosure, LiDAR fusion roadmap.
* **Likely Viva Question & Answer:**
  * **Q:** *If you had 6 more months to work on this project, what single improvement would you prioritize?*
  * **A:** *I would prioritize integrating 3D UAV LiDAR point clouds. While 2D drone photogrammetry is cost-effective, LiDAR penetrates vegetation shadows and provides true 3D point coordinates (X, Y, Z). This would completely eliminate relief displacement and allow the system to calculate vertical headroom clearance under awnings, verifying whether an overhang violates the minimum 2.5-meter vertical clearance mandated by Indian road standards.*

---

### Slide 19: 12. Research Paper | Peer-Reviewed Scholarly Publication
* **Visual Elements:** Research publication metadata card, complete manuscript title, full author listing, institutional affiliation, and submission status.
* **What it explains:** Details of the research paper resulting from this capstone project: title, authorship, IEEE conference format, verified submission status, and core contributions.
* **45–60 Second Speaking Script:**
  > "A tangible outcome of our capstone research is a complete scientific research paper titled *'Automated Urban Road and Government Land Encroachment Detection System for Municipal Governance: Design, Implementation, and Empirical Validation'*. Co-authored with our mentor, Dr. Prashant Udawant, the paper is prepared in IEEE double-column format using IEEEtran LaTeX. In strict academic honesty, the paper has been finalized and submitted for presentation and publication in an IEEE-sponsored international conference on geospatial artificial intelligence and smart cities. The paper details our decoupled spatial set algebra, empirical YOLOv8n-seg metrics, and GSD sensitivity analyses."
* **Key Technical Concepts:** IEEE conference paper publication, IEEEtran format, verified submission status, open-science reproducibility.
* **Likely Viva Question & Answer:**
  * **Q:** *What is the core novel scientific contribution highlighted in your research paper?*
  * **A:** *The primary scientific contribution is the mathematical formalization of Decoupled Spatial Set Algebra ($S \setminus P^* \cap R_{\text{ROW}}$). While prior literature treated aerial road monitoring as either a pure computer vision problem or a manual GIS digitizing task, our paper is the first to prove mathematically and empirically that decoupling visual instance segmentation from statutory cadastral vector algebra is necessary to eliminate false legal attribution while retaining sub-meter precision.*

---

### Slide 20: 13. References | Key Scholarly Literature (Part 1)
* **Visual Elements:** Full bibliographic citations [1] through [7] formatted cleanly in academic IEEE reference style.
* **What it explains:** Citations of peer-reviewed journal and conference publications covering Mask R-CNN, Segment Anything, remote sensing YOLO variants, UAV photogrammetry, and spatial computing.
* **45–60 Second Speaking Script:**
  > "Slides 20 and 21 compile our academic and statutory references. Part 1 lists foundational scholarly publications: He et al.'s seminal Mask R-CNN paper; Kirillov et al.'s Segment Anything model; Chen et al.'s 2024 RSPrompter for remote sensing; Zhang's FFCA-YOLO for small aerial objects; Yurtseven's UAV roadside photogrammetry; Verma's roadside obstacle detection; and Fleischmann's 2024 spatial GNN modeling of urban cadastral forms. Every citation has been consulted and integrated into our dissertation."
* **Key Technical Concepts:** Peer-reviewed scholarly citations, remote sensing literature, foundational deep learning papers.
* **Likely Viva Question & Answer:**
  * **Q:** *Which of these citations is the primary baseline for your instance segmentation architecture?*
  * **A:** *Ultralytics YOLOv8-seg builds upon the single-stage prototype segmentation paradigm originally proposed in YOLACT (Bolya et al., 2019) and the feature pyramid formulations of Lin and He et al., combined with C2f cross-stage partial modules.*

---

### Slide 21: 13. References | Geospatial Standards, Codes & Frameworks (Part 2)
* **Visual Elements:** Full statutory citations [8] through [13] covering IRC codes, MoHUA guidelines, SVAMITVA protocols, OGC standards, Ultralytics, and Shapely.
* **What it explains:** Statutory engineering guidelines, municipal standards, Indian Road Congress codes, and open-source geospatial frameworks.
* **45–60 Second Speaking Script:**
  > "Part 2 of our references lists the governing statutory and civil engineering standards. We adhere to Indian Roads Congress code IRC:86-1983 for statutory road right-of-way widths, MoHUA's National Urban Transport Policy for pedestrian sidewalk protection, and Survey of India's SVAMITVA drone survey guidelines. On the software side, our planar topological set algebra strictly complies with Open Geospatial Consortium (OGC) Simple Feature Access standards implemented via Shapely and GEOS, and our computer vision model builds on the official Ultralytics YOLOv8 framework."
* **Key Technical Concepts:** IRC:86-1983, MoHUA NUTP, SVAMITVA drone survey protocols, OGC Simple Features, Shapely/GEOS standards.
* **Likely Viva Question & Answer:**
  * **Q:** *Why is IRC:86-1983 relevant to your spatial analysis?*
  * **A:** *IRC:86-1983 defines the statutory geometric standards for urban road rights-of-way in India. It mandates standard corridor widths—such as 9 meters, 12 meters, or 18 meters—and specifies minimum pedestrian footpath widths of 1.5 to 2.5 meters. Our GIS engine uses these IRC statutory widths to generate the gazetted road ROW layer against which potential encroachments are measured.*

---

### Slide 22: 14. Questions & Discussion | Capstone Project Defense
* **Visual Elements:** Project identity summary card (students, mentor, institution) paired with Core Viva Defense Takeaways and formal Q&A prompt.
* **What it explains:** Concludes the presentation, summarizing the four core technical takeaways and inviting technical questions and discussion from the examination panel.
* **45–60 Second Speaking Script:**
  > "That concludes our presentation. To summarize our defense: we have proven that combining deep instance segmentation with cadastral computational geometry bridges the gap between raw drone survey imagery and statutory municipal governance. Our decoupled spatial set algebra eliminates false legal attribution, isolates sub-meter corridor encroachments with zero false positives on lawful setbacks, and runs in under 14 milliseconds on standard CPU hardware. We would like to express our deepest gratitude to our project guide, Dr. Prashant Udawant, and the faculty of MPSTME. We are now open for technical questions and discussion from the evaluation panel."
* **Key Technical Concepts:** Capstone project defense, core scientific contributions, open floor for examination panel.
* **Likely Viva Question & Answer:**
  * **Q:** *If a municipal corporation wants to deploy this system tomorrow, what are the primary prerequisite data layers they must provide?*
  * **A:** *They must supply two foundational datasets: first, a georeferenced cadastral property boundary shapefile or GeoJSON with unique parcel identifiers; and second, the gazetted Road Master Right-of-Way alignment defining the statutory corridor width. With those two vector layers in place, our pipeline can ingest drone imagery, execute automated transformation, and output legally actionable encroachment inspection sheets.*

---
*Document prepared for B.Tech Information Technology Capstone Project Evaluation at SVKM's NMIMS MPSTME, Shirpur Campus.*
