import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

out_dir = r'e:\Urban Road Encroachment Detection System\publication_ready_paper\figures'
os.makedirs(out_dir, exist_ok=True)

# -------------------------------------------------------------
# Figure 2: End-to-End System Architecture and Operational Dataflow
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.0), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 50)
ax.axis('off')

def draw_box(ax, x, y, w, h, title, subtext, color_fill, color_edge, text_color='#1a252f'):
    box = patches.FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.6',
                                facecolor=color_fill, edgecolor=color_edge, lw=1.6)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2 + 1.2, title, ha='center', va='center',
            fontsize=8.5, fontweight='bold', color=text_color)
    ax.text(x + w/2, y + h/2 - 2.0, subtext, ha='center', va='center',
            fontsize=7.2, color='#34495e', multialignment='center')

def draw_arrow(ax, x1, y1, x2, y2, label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=1.6, color='#2c3e50', shrinkA=2, shrinkB=2))
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 1.2, label, ha='center', va='bottom', fontsize=7, color='#2c3e50', fontweight='bold')

# Top Row - Vision & Georeferencing
draw_box(ax, 2, 34, 18, 12, '1. Aerial Drone Survey', 'Nadir RGB Imagery\n1024 x 723 (GSD ~ 5 cm/px)', '#ebf5fb', '#2980b9')
draw_arrow(ax, 20, 40, 26, 40)

draw_box(ax, 26, 34, 20, 12, '2. YOLOv8n-seg Core', 'Physical Instance Masks\n(Roofs, Awnings, Ramps)\nPrecision 0.885, mAP 0.891', '#e8f8f5', '#16a085')
draw_arrow(ax, 46, 40, 52, 40, 'Masks (u, v)')

draw_box(ax, 52, 34, 20, 12, '3. Inverse Affine T', 'Projective Coordinate Map\nx_metric = A * x_pixel\nNon-Singular (det A != 0)', '#fef9e7', '#f39c12')
draw_arrow(ax, 72, 40, 78, 40, 'Polygons (X, Y)')

draw_box(ax, 78, 34, 20, 12, '4. Cadastral Layer GIS', 'Authoritative Cadastre\nStatutory ROW Corridor\nCarriageway & Footpaths', '#f4ecf7', '#8e44ad')

# Connecting Downward
draw_arrow(ax, 88, 34, 88, 22)

# Bottom Row - Spatial Set Engine & Attribution
draw_box(ax, 76, 8, 22, 13, '5. Vector Set Algebra', 'Weiler-Atherton Clipping\nOutside: O = S \\ P*\nROW Intrusion: E = O n R_ROW', '#fadbd8', '#c0392b')
draw_arrow(ax, 76, 14.5, 68, 14.5, 'Violations E')

draw_box(ax, 46, 8, 22, 13, '6. Engineering Attribution', 'Footpath vs. Carriageway\nArea A_enc, Depth d_proj, Frontage\nChainage Projection: 0+011.0 m', '#fdedec', '#e74c3c')
draw_arrow(ax, 46, 14.5, 38, 14.5, 'Attributes')

draw_box(ax, 16, 8, 22, 13, '7. Municipal Decision API', 'Rule Severity: CRITICAL/HIGH...\nAudit Notice & GeoJSON\nFastAPI + SQLite + Leaflet', '#eaf2f8', '#3498db')
draw_arrow(ax, 16, 14.5, 9, 14.5)

draw_box(ax, 1, 8, 8, 13, 'Evidentiary\nAudit Cards', 'Sub-Meter\nLegal Trail', '#d5f5e3', '#27ae60')

plt.tight_layout()
p2 = os.path.join(out_dir, 'fig2_architecture_workflow.png')
plt.savefig(p2, bbox_inches='tight')
plt.close()
print('Created:', p2)

# -------------------------------------------------------------
# Figure 3: Visual Inspection & Verification of Multi-Zone Encroachments
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)

# ax1: Aerial Drone Ortho with Cadastral Boundaries & Violations
ax1.set_xlim(0, 85)
ax1.set_ylim(-6, 6)
ax1.set_aspect('equal')
ax1.set_title('(a) Drone Orthophoto with Cadastral ROW & Detections', fontsize=9, fontweight='bold')
ax1.set_xlabel('Corridor Chainage Length (meters)', fontsize=8)
ax1.set_ylabel('Transverse Width (meters)', fontsize=8)

# Carriageway (-3.0 to +3.0)
ax1.fill_between([0, 85], [-3, -3], [3, 3], color='#34495e', alpha=0.3, label='Carriageway (6.0m)')
# Footpaths
ax1.fill_between([0, 85], [3, 3], [4.5, 4.5], color='#f39c12', alpha=0.25, label='East Footpath (1.5m)')
ax1.fill_between([0, 85], [-4.5, -4.5], [-3, -3], color='#f39c12', alpha=0.25, label='West Footpath (1.5m)')

# Centerline
ax1.plot([0, 85], [0, 0], color='#e67e22', ls='--', lw=1.5, label='Centerline')

# Cadastral ROW lines (Red)
ax1.plot([0, 85], [4.5, 4.5], color='#c0392b', lw=2.0, label='Statutory ROW Boundary')
ax1.plot([0, 85], [-4.5, -4.5], color='#c0392b', lw=2.0)

# Draw private buildings on East side (lawful)
for x_start, w in [(2, 12), (18, 10), (32, 14), (50, 12), (66, 15)]:
    bld = patches.Rectangle((x_start, 4.8), w, 4.0, facecolor='#2980b9', alpha=0.4, edgecolor='#1b4f72', lw=1.2)
    ax1.add_patch(bld)

# Draw Encroachment E-01 (Awning at chainage 11m, x=8.5 to 13.5, y=3.3 to 4.5 => area 5.0m x 1.2m = 6.0 sqm)
enc1 = patches.Rectangle((8.5, 3.3), 5.0, 1.2, facecolor='#e74c3c', alpha=0.85, edgecolor='#922b21', lw=1.8)
ax1.add_patch(enc1)
ax1.plot([11.0, 11.0], [3.9, 0], color='#e74c3c', ls=':', lw=1.2)
ax1.plot(11.0, 0, marker='o', color='#e74c3c', markersize=4)
ax1.text(11.0, 1.8, 'E-01 (6.00 m$^2$)\nStation 0+011.0', ha='center', va='center', fontsize=7.5,
         fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', facecolor='#fadbd8', edgecolor='#c0392b', lw=1))

# Draw Encroachment E-02 (Ramp/Shed at chainage 54.5m, x=53 to 56, y=3.7 to 4.5 => area 3.0m x 1.2m = 3.6 sqm)
enc2 = patches.Rectangle((53.0, 3.3), 3.0, 1.2, facecolor='#e74c3c', alpha=0.85, edgecolor='#922b21', lw=1.8)
ax1.add_patch(enc2)
ax1.plot([54.5, 54.5], [3.9, 0], color='#e74c3c', ls=':', lw=1.2)
ax1.plot(54.5, 0, marker='o', color='#e74c3c', markersize=4)
ax1.text(54.5, 1.8, 'E-02 (3.60 m$^2$)\nStation 0+054.5', ha='center', va='center', fontsize=7.5,
         fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', facecolor='#fadbd8', edgecolor='#c0392b', lw=1))

ax1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.45), ncol=3, fontsize=6.8)

# ax2: Zoomed Encroachment Attribution Diagram
ax2.set_xlim(6, 16)
ax2.set_ylim(2, 7)
ax2.set_aspect('equal')
ax2.set_title('(b) Detailed Vector Attribution of Violation E-01', fontsize=9, fontweight='bold')
ax2.set_xlabel('Local X (meters)', fontsize=8)
ax2.set_ylabel('Local Y (meters)', fontsize=8)

# Building Base
bld_zoom = patches.Rectangle((8.5, 4.5), 5.0, 2.2, facecolor='#3498db', alpha=0.35, edgecolor='#2980b9', lw=1.5)
ax2.add_patch(bld_zoom)
ax2.text(11.0, 5.5, 'Parcel P-07\n(Private Ground)', ha='center', va='center', fontsize=8, fontweight='bold', color='#1b4f72')

# Statutory Line (y = 4.5)
ax2.axhline(4.5, color='#c0392b', lw=2.2, ls='-', label='Property Line / ROW')

# Encroaching Awning (y = 3.3 to 4.5)
enc_zoom = patches.Rectangle((8.5, 3.3), 5.0, 1.2, facecolor='#e74c3c', alpha=0.75, edgecolor='#922b21', lw=2.0)
ax2.add_patch(enc_zoom)
ax2.text(11.0, 3.9, 'ENCROACHMENT $\\mathcal{E}_1$\nArea = 6.00 m$^2$\n(Footpath Intrusion)', ha='center', va='center', fontsize=8, fontweight='bold', color='#ffffff')

# Dimension annotations
# Depth = 1.2m
ax2.annotate('', xy=(14.0, 3.3), xytext=(14.0, 4.5),
            arrowprops=dict(arrowstyle='<->', lw=1.4, color='#2c3e50'))
ax2.text(14.2, 3.9, '$d_{proj} = 1.20$ m\n(80% Footpath)', va='center', fontsize=7.5, fontweight='bold', color='#2c3e50')

# Frontage = 5.0m
ax2.annotate('', xy=(8.5, 2.9), xytext=(13.5, 2.9),
            arrowprops=dict(arrowstyle='<->', lw=1.4, color='#2c3e50'))
ax2.text(11.0, 2.65, 'Frontage Width $w_{front} = 5.00$ m', ha='center', va='top', fontsize=7.5, fontweight='bold', color='#2c3e50')

ax2.legend(loc='lower center', bbox_to_anchor=(0.5, -0.45), fontsize=7.2)

plt.tight_layout()
p3 = os.path.join(out_dir, 'fig3_encroachment_attribution.png')
plt.savefig(p3, bbox_inches='tight')
plt.close()
print('Created:', p3)
