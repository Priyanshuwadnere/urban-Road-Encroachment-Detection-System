"""
GIS Map Visualizer for Phase 5 Encroachment Analysis.
Renders high-resolution vector map visualizations displaying cadastral parcels,
road ROW corridors, paved carriageways, road centerlines, chainage markers,
physical structure detections, and highlighted potential encroachment zones.
"""

import os
from typing import List, Optional, Any
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, Point

from src.config import ACADEMIC_DISCLAIMER
from src.gis.gis_models import PropertyMasterRecord, RoadMasterRecord, Phase5EncroachmentResult


class GISMapVisualizer:
    """Renders GIS Map Visualizations of Road ROW Encroachment Analysis."""

    @staticmethod
    def _plot_polygon(
        ax,
        geom: Any,
        facecolor: str = "none",
        edgecolor: str = "black",
        linestyle: str = "-",
        linewidth: float = 1.0,
        alpha: float = 0.5,
        hatch: Optional[str] = None,
        label: Optional[str] = None,
    ):
        """Helper to plot Shapely Polygon or MultiPolygon onto matplotlib Axes."""
        if geom is None or geom.is_empty:
            return

        if isinstance(geom, Polygon):
            polys = [geom]
        elif isinstance(geom, MultiPolygon):
            polys = list(geom.geoms)
        else:
            return

        for idx, poly in enumerate(polys):
            exterior = poly.exterior.coords
            path = Path(exterior)
            patch = mpatches.PathPatch(
                path,
                facecolor=facecolor,
                edgecolor=edgecolor,
                linestyle=linestyle,
                linewidth=linewidth,
                alpha=alpha,
                hatch=hatch,
                label=label if idx == 0 else None,
            )
            ax.add_patch(patch)

    @classmethod
    def render_map(
        cls,
        parcels: List[PropertyMasterRecord],
        road_row: RoadMasterRecord,
        results: List[Phase5EncroachmentResult],
        output_path: str = "dataset/gis_outputs/gis_map_render.png",
    ) -> str:
        """
        Render comprehensive GIS map visualization and save image file.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig, ax = plt.subplots(figsize=(11, 8.5), dpi=300)

        ax.set_facecolor("#f8f9fa")

        # 1. Plot Legal Cadastral Property Parcels
        for p in parcels:
            try:
                g = shape(p.geometry_geojson)
                cls._plot_polygon(
                    ax, g, facecolor="#e1f5fe", edgecolor="#0288d1", linestyle="-", linewidth=1.2, alpha=0.6
                )
                cent = g.centroid
                ax.text(
                    cent.x,
                    cent.y,
                    p.parcel_id,
                    fontsize=8.5,
                    fontweight="bold",
                    color="#01579b",
                    ha="center",
                    va="center",
                )
            except Exception:
                pass

        # 2. Plot Legal Road ROW Boundary
        try:
            row_g = shape(road_row.geometry_geojson)
            cls._plot_polygon(
                ax, row_g, facecolor="#ffebee", edgecolor="#d32f2f", linestyle="--", linewidth=1.8, alpha=0.4
            )
        except Exception:
            pass

        # 3. Plot Existing Paved Carriageway
        if road_row.carriageway_geojson:
            try:
                cw_g = shape(road_row.carriageway_geojson)
                cls._plot_polygon(
                    ax, cw_g, facecolor="#cfd8dc", edgecolor="#455a64", linestyle="-", linewidth=1.0, alpha=0.7
                )
            except Exception:
                pass

        # 4. Plot Road Centerline
        if road_row.centerline_geojson:
            try:
                cl_g = shape(road_row.centerline_geojson)
                if isinstance(cl_g, LineString):
                    xs, ys = cl_g.xy
                    ax.plot(xs, ys, color="#fbc02d", linestyle="--", linewidth=2.0, label="Road Centerline")
            except Exception:
                pass

        # 5. Plot Chainage Markers within the corridor study area (0+000 to 0+030)
        chainages = [0.0, 10.0, 20.0, 30.0]
        if road_row.centerline_geojson:
            try:
                cl_g = shape(road_row.centerline_geojson)
                if isinstance(cl_g, LineString):
                    for ch in chainages:
                        if ch <= cl_g.length:
                            pt = cl_g.interpolate(ch)
                            ax.plot(pt.x, pt.y, "o", color="#333333", markersize=5)
                            ax.text(
                                pt.x - 1.2,
                                pt.y,
                                f"CH 0+{ch:03.0f}",
                                fontsize=7.5,
                                color="#212121",
                                fontweight="bold",
                                ha="right",
                                va="center",
                            )
            except Exception:
                pass

        # 6. Plot Potential Encroachments & Detections
        for r in results:
            if r.status == "POTENTIAL ROAD ROW ENCROACHMENT" and r.encroachment_polygon_geojson:
                try:
                    enc_g = shape(r.encroachment_polygon_geojson)
                    cls._plot_polygon(
                        ax,
                        enc_g,
                        facecolor="#d50000",
                        edgecolor="#b71c1c",
                        linestyle="-",
                        linewidth=2.0,
                        alpha=0.90,
                        hatch="//",
                    )
                    cent = enc_g.centroid
                    is_e01 = (r.parcel_id == "P-07" or "E01" in str(r.detection_id) or "4A8C" in str(r.case_id))
                    enc_name = "E-01" if is_e01 else "E-02"
                    concept_str = r.structure_concept or r.class_name
                    tag = "[REF]" if r.data_provenance == "SYNTHETIC_GIS_REFERENCE_BENCHMARK" else "[ML]"
                    area_val = r.metrics.area_sqm if r.metrics else (r.area_sqm if hasattr(r, "area_sqm") else 0.0)
                    label_str = f"{tag} {enc_name} on {r.parcel_id}\n{concept_str}\n{area_val:.2f} m²"
                    ax.text(
                        cent.x - 3.2,
                        cent.y,
                        label_str,
                        fontsize=7.5,
                        fontweight="bold",
                        color="#b71c1c",
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#b71c1c", alpha=0.95),
                        ha="right",
                        va="center",
                    )
                except Exception:
                    pass

        # Setup Axis bounds & Grid
        ax.set_xlim(-4.0, 53.0)
        ax.set_ylim(-3.0, 35.0)
        ax.set_aspect("equal")
        ax.grid(True, linestyle=":", alpha=0.5, color="#9e9e9e")

        ax.set_title(
            "URBAN ROAD ENCROACHMENT DETECTION SYSTEM\nPhase 5 GIS Spatial Analysis & Encroachment Map (Synthetic Reference Benchmarks)",
            fontsize=12,
            fontweight="bold",
            pad=12,
        )
        ax.set_xlabel("Easting / X Coordinate (meters)", fontsize=10)
        ax.set_ylabel("Northing / Y Coordinate (meters)", fontsize=10)

        # Legend handles
        parcel_patch = mpatches.Patch(facecolor="#e1f5fe", edgecolor="#0288d1", label="Legal Cadastral Parcel")
        row_patch = mpatches.Patch(facecolor="#ffebee", edgecolor="#d32f2f", linestyle="--", label="Legal Road ROW (9.0m)")
        cw_patch = mpatches.Patch(facecolor="#cfd8dc", edgecolor="#455a64", label="Paved Carriageway (6.0m)")
        enc_patch = mpatches.Patch(facecolor="#d50000", edgecolor="#b71c1c", hatch="//", label="Synthetic GIS Reference Benchmark Encroachment")

        ax.legend(handles=[parcel_patch, row_patch, cw_patch, enc_patch], loc="upper right", fontsize=8, framealpha=0.95)

        # North Arrow
        ax.annotate(
            "N",
            xy=(0.04, 0.94),
            xytext=(0.04, 0.86),
            xycoords="axes fraction",
            arrowprops=dict(facecolor="black", width=2, headwidth=7),
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

        # Academic Disclaimer Footer
        fig.text(
            0.5,
            0.015,
            ACADEMIC_DISCLAIMER,
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
            color="#c62828",
            bbox=dict(boxstyle="square,pad=0.3", facecolor="#ffebee", edgecolor="#c62828", alpha=0.9),
        )

        plt.tight_layout(rect=[0, 0.04, 1, 0.96])
        plt.savefig(output_path, bbox_inches="tight", dpi=300)
        plt.close(fig)

        return output_path
