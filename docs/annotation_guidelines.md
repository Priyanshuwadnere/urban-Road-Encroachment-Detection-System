# Phase 3A Annotation Guidelines: YOLO Instance Segmentation

> [!IMPORTANT]
> **ACADEMIC DATA PROVENANCE DISCLAIMER**:
> This dataset consists of a **SYNTHETIC ACADEMIC DATASET** extracted from AI-generated storyboard montages.
> All legal boundaries, property lines, and annotations are for academic computer-vision and GIS pipeline development ONLY.
> `SYNTHETIC / ACADEMIC PROTOTYPE — NOT AN OFFICIAL MUNICIPAL RECORD`

---

## 1. Core Principles

1. **Physical Structures Only**: The YOLO model detects **physical structural shapes** in 2D space.
2. **NO Encroachment Class**: There is **NO** `encroachment` YOLO class. Encroachment is evaluated downstream using GIS vector set algebra.
3. **Conservative Annotation Rule**: If an object cannot be reliably identified from the aerial perspective, do **NOT** invent a label. Leave it unannotated or flag for manual review.

---

## 2. Physical Structure Class Taxonomy (0 to 7)

| Class ID | Class Name | Description | What to Annotate | What NOT to Annotate |
| :--- | :--- | :--- | :--- | :--- |
| `0` | **building** | Main residential/commercial building structure | Visible building footprint & outer wall boundary | Rooftop equipment, solar panels, shadows, trees |
| `1` | **staircase** | Exterior steps & stair structures | Identifiable concrete/metal exterior staircases | Interior stairs, ground level flat footpaths |
| `2` | **shop_extension** | Shopfront commercial extensions | Physical shop-side stalls, display frames, covered extensions | Main building body, parked delivery vehicles, street displays |
| `3` | **veranda** | Covered or elevated porch/veranda | Covered elevated porches visually distinct from main roof | Interior rooms, open roofs without railings |
| `4` | **shed** | Standalone or attached shed roofs | Corrugated tin/metal sheds, utility sheds | Canvas umbrellas, temporary tarps |
| `5` | **ramp** | Vehicle/pedestrian access ramp | Physical concrete/metal ramps extending from property line | Flat asphalt road, standard sidewalks |
| `6` | **awning** | Roof/sunshade projections | Fixed metal/fabric awning overhangs extending from facade | Soft window curtains, open doors |
| `7` | **compound_wall** | Property perimeter boundary wall | Visible masonry/metal boundary compound walls | Temporary wooden fences, painted lines on road |

---

## 3. General Annotation Rules

### A. Occlusion & Tree Canopy
- **Light Occlusion (< 30%)**: Trace the estimated structural contour smoothly through minor foliage.
- **Heavy Occlusion (> 30%)**: Split into separate visible polygon fragments rather than annotating unseen ground underneath dense tree canopy.

### B. Overlapping Structures
- When an awning (`6`) or shed (`4`) overlaps a staircase (`1`) or veranda (`3`), annotate each distinct physical structure with its own tight polygon. Overlapping polygon coordinates are allowed and expected in YOLO instance segmentation.

### C. Boundary Precision
- Draw tight polygon vertices along the physical edge of the structure.
- Minimum polygon size: Object area must exceed at least **100 pixels²** ($0.01\%$ of total frame area).
- Coordinates must be normalized floats in $[0.0, 1.0]$.

### D. Ambiguous Cases
- If an object cannot be differentiated between a shed (`4`) and a shop extension (`2`) due to image blur or shadow, mark it for secondary human inspection. Do **NOT** guess.
