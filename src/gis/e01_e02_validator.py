"""
Synthetic Reference Validation Engine for Benchmark Cases E-01 and E-02.
Verifies spatial set algebra, metric calculation, chainage calculations,
and total area summation against synthetic ground-truth reference benchmarks.

CRITICAL DISCLOSURE:
Cases E-01 and E-02 are PURELY SYNTHETIC GIS REFERENCE BENCHMARK GEOMETRIES.
They are NOT YOLO model predictions.
Original structure concepts:
  E-01: staircase / shop-side extension (Parcel P-07)
  E-02: veranda / shop-extension (Parcel P-09)
"""

from typing import List, Tuple, Dict, Any
from src.gis.gis_models import PropertyMasterRecord, RoadMasterRecord, DetectedObjectGISRecord, Phase5EncroachmentResult
from src.gis.phase5_engine import Phase5GISEngine
from src.config import STATUS_POTENTIAL_ENCROACHMENT, ACTION_FIELD_VERIFICATION


class SyntheticReferenceValidator:
    """Validator for synthetic reference benchmark cases E-01 and E-02."""

    @staticmethod
    def get_test_case_e01_detection() -> DetectedObjectGISRecord:
        """
        Synthetic Reference Benchmark Case E-01 (Top Red Outline in Drone View):
        Structure concept: awning / shop-side canopy extension (Green tarpaulin awning/stall)
        Property = Parcel P-07 (Shanti Heights)
        Projection = 1.20 m into ROW, Frontage = 5.00 m -> Area = 6.00 m²
        Data Provenance = SYNTHETIC_GIS_REFERENCE_BENCHMARK (Ground-truth drone survey reference)
        """
        # Map polygon extending from X=27.8 (in ROW) to X=33.0 (inside P-07)
        # Y from 20.75 to 25.75 (frontage 5.0m)
        coords = [
            (27.8, 20.75),
            (33.0, 20.75),
            (33.0, 25.75),
            (27.8, 25.75),
            (27.8, 20.75),
        ]
        # Exact image pixel coordinates of the marked red outline
        pixels = [
            (545.0, 117.0),
            (552.0, 193.0),
            (572.0, 215.0),
            (602.0, 225.0),
            (615.0, 179.0),
            (609.0, 110.0),
            (545.0, 117.0),
        ]
        return DetectedObjectGISRecord(
            detection_id="REF-BENCHMARK-E01",
            frame_id="DRONE_SURVEY_R001_CORRIDOR.jpg",
            sequence_id="SYNTHETIC_SEQ01",
            class_id=6,  # 6 represents awning in physical class taxonomy
            class_name="awning / shop-side canopy extension",
            structure_concept="awning / shop-side canopy extension",
            data_provenance="SYNTHETIC_GIS_REFERENCE_BENCHMARK",
            confidence=1.00,  # Benchmark ground-truth reference
            pixel_polygon=pixels,
            map_polygon=coords,
        )

    @staticmethod
    def get_test_case_e02_detection() -> DetectedObjectGISRecord:
        """
        Synthetic Reference Benchmark Case E-02 (Bottom Red Outline in Drone View):
        Structure concept: shop_extension / veranda shed (Corrugated tin sheet shed/veranda)
        Property = Parcel P-08 (Surya Electricals & Workshop)
        Projection = 0.80 m into ROW, Frontage = 4.50 m -> Area = 3.60 m²
        Data Provenance = SYNTHETIC_GIS_REFERENCE_BENCHMARK (Ground-truth drone survey reference)
        """
        # Map polygon extending from X=28.2 (in ROW) to X=32.5 (inside P-08)
        # Y from 15.0 to 19.5 (frontage 4.5m)
        coords = [
            (28.2, 15.0),
            (32.5, 15.0),
            (32.5, 19.5),
            (28.2, 19.5),
            (28.2, 15.0),
        ]
        # Exact image pixel coordinates of the marked red outline
        pixels = [
            (629.0, 262.0),
            (562.0, 292.0),
            (564.0, 394.0),
            (576.0, 408.0),
            (611.0, 411.0),
            (649.0, 395.0),
            (629.0, 262.0),
        ]
        return DetectedObjectGISRecord(
            detection_id="REF-BENCHMARK-E02",
            frame_id="DRONE_SURVEY_R001_CORRIDOR.jpg",
            sequence_id="SYNTHETIC_SEQ01",
            class_id=2,  # 2 represents shop_extension in physical class taxonomy
            class_name="shop_extension / veranda shed",
            structure_concept="shop_extension / veranda shed",
            data_provenance="SYNTHETIC_GIS_REFERENCE_BENCHMARK",
            confidence=1.00,  # Benchmark ground-truth reference
            pixel_polygon=pixels,
            map_polygon=coords,
        )

    @classmethod
    def validate_e01_e02(
        cls,
        engine: Phase5GISEngine
    ) -> Tuple[Phase5EncroachmentResult, Phase5EncroachmentResult, float]:
        """
        Execute analysis on E-01 and E-02 and validate results against reference benchmarks.
        Returns (res_e01, res_e02, total_encroached_area).
        """
        det_e01 = cls.get_test_case_e01_detection()
        det_e02 = cls.get_test_case_e02_detection()

        res_e01 = engine.analyze_detection(det_e01)
        res_e02 = engine.analyze_detection(det_e02)

        # Assertions for E-01
        assert res_e01.status == STATUS_POTENTIAL_ENCROACHMENT, f"E-01 status expected {STATUS_POTENTIAL_ENCROACHMENT}, got {res_e01.status}"
        assert res_e01.parcel_id == "P-07", f"E-01 expected parcel P-07, got {res_e01.parcel_id}"
        assert res_e01.data_provenance == "SYNTHETIC_GIS_REFERENCE_BENCHMARK"
        assert res_e01.structure_concept == "awning / shop-side canopy extension"
        assert res_e01.metrics is not None
        assert abs(res_e01.metrics.area_sqm - 6.00) < 0.01, f"E-01 area expected 6.00, got {res_e01.metrics.area_sqm}"
        assert abs(res_e01.metrics.max_projection_m - 1.20) < 0.01, f"E-01 depth expected 1.20, got {res_e01.metrics.max_projection_m}"
        assert abs(res_e01.metrics.frontage_m - 5.00) < 0.01, f"E-01 frontage expected 5.00, got {res_e01.metrics.frontage_m}"

        # Assertions for E-02
        assert res_e02.status == STATUS_POTENTIAL_ENCROACHMENT, f"E-02 status expected {STATUS_POTENTIAL_ENCROACHMENT}, got {res_e02.status}"
        assert res_e02.parcel_id in ["P-08", "P-09"], f"E-02 expected parcel P-08, got {res_e02.parcel_id}"
        assert res_e02.data_provenance == "SYNTHETIC_GIS_REFERENCE_BENCHMARK"
        assert res_e02.structure_concept == "shop_extension / veranda shed"
        assert res_e02.metrics is not None
        assert abs(res_e02.metrics.area_sqm - 3.60) < 0.01, f"E-02 area expected 3.60, got {res_e02.metrics.area_sqm}"
        assert abs(res_e02.metrics.max_projection_m - 0.80) < 0.01, f"E-02 depth expected 0.80, got {res_e02.metrics.max_projection_m}"
        assert abs(res_e02.metrics.frontage_m - 4.50) < 0.01, f"E-02 frontage expected 4.50, got {res_e02.metrics.frontage_m}"

        # Total Encroached Area assertion
        total_area = round(res_e01.metrics.area_sqm + res_e02.metrics.area_sqm, 2)
        assert abs(total_area - 9.60) < 0.01, f"Total encroached area expected 9.60 m², got {total_area} m²"

        return res_e01, res_e02, total_area
