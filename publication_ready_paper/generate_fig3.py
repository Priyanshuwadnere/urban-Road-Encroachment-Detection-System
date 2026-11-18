import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

out_dir = r"E:/Urban Road Encroachment Detection System/publication_ready_paper/figures"
os.makedirs(out_dir, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# 11 inches wide by 7.8 inches high - comprehensive civil engineering cross-section
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.6), dpi=300, gridspec_kw={'height_ratios': [1.0, 1.35], 'hspace': 0.38})

# ==========================================
# (a) Longitudinal Corridor Plan View (85m)
# ==========================================
ax1.set_xlim(-2, 87)
ax1.set_ylim(-7.5, 7.5)

# Paved Carriageway (6.0m: -3.0 to +3.0)
ax1.fill_between([-2, 87], [-3, -3], [3, 3], color='#E2E8F0', alpha=0.9, zorder=1)

# Pedestrian Sidewalks (1.5m: 3.0 to 4.5 and -4.5 to -3.0)
ax1.fill_between([-2, 87], [3, 3], [4.5, 4.5], color='#FEF3C7', alpha=0.9, zorder=1)
ax1.fill_between([-2, 87], [-4.5, -4.5], [-3, -3], color='#FEF3C7', alpha=0.9, zorder=1)

# Road Centerline
line_cl, = ax1.plot([-2, 87], [0, 0], color='#D97706', ls='--', lw=1.8, zorder=3, label=r'Road Centerline $\mathcal{L}_{\mathrm{center}}$')

# Kerb Lines (Curb edge separating carriageway from sidewalk at y = +/- 3.0)
line_kerb, = ax1.plot([-2, 87], [3.0, 3.0], color='#0D9488', ls='-.', lw=1.5, zorder=3, label=r'Kerb Line / Footpath Inner Edge ($y = \pm 3.0\,\mathrm{m}$)')
ax1.plot([-2, 87], [-3.0, -3.0], color='#0D9488', ls='-.', lw=1.5, zorder=3)

# Statutory ROW Limits / Cadastral baseline (Red lines at y = +/- 4.5)
line_row, = ax1.plot([-2, 87], [4.5, 4.5], color='#DC2626', lw=2.2, zorder=4, label=r'Statutory ROW Boundary ($9.00\,\mathrm{m}$ width, $y = \pm 4.5\,\mathrm{m}$)')
ax1.plot([-2, 87], [-4.5, -4.5], color='#DC2626', lw=2.2, zorder=4)

# Private Cadastral Parcels on North (P-07 to P-11)
parcels_n = [(0, 15, 'P-07'), (15, 28, 'P-08'), (28, 45, 'P-09'), (45, 62, 'P-10'), (62, 85, 'P-11')]
for x1_p, x2_p, pid in parcels_n:
    w = x2_p - x1_p
    p_box = patches.Rectangle((x1_p, 4.5), w, 2.6, facecolor='#EFF6FF', edgecolor='#3B82F6', lw=1.2, ls='--', zorder=2)
    ax1.add_patch(p_box)
    ax1.text(x1_p + w/2, 5.8, f'Parcel {pid}', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1E40AF')

# Private Cadastral Parcels on South (P-01 to P-04)
parcels_s = [(0, 20, 'P-01'), (20, 42, 'P-02'), (42, 65, 'P-03'), (65, 85, 'P-04')]
for x1_p, x2_p, pid in parcels_s:
    w = x2_p - x1_p
    p_box = patches.Rectangle((x1_p, -7.1), w, 2.6, facecolor='#F8FAFC', edgecolor='#64748B', lw=1.0, ls='--', zorder=2)
    ax1.add_patch(p_box)
    ax1.text(x1_p + w/2, -5.8, f'Parcel {pid}', ha='center', va='center', fontsize=8, color='#475569')

# Violations in plan view
# E-01: Station 11.0m
enc1 = patches.Rectangle((8.5, 3.3), 5.0, 1.2, facecolor='#EF4444', edgecolor='#B91C1C', lw=2.0, zorder=5)
ax1.add_patch(enc1)
ax1.plot([11.0, 11.0], [3.3, 0], color='#B91C1C', ls=':', lw=1.5, zorder=6)
ax1.plot(11.0, 0, marker='o', markersize=5, color='#B91C1C', zorder=6)
ax1.annotate('Violation E-01 (6.00 m$^2$)\nStation 0+011.0 (Awning)', xy=(11.0, 3.9), xytext=(11.0, 1.2),
             ha='center', va='center', fontsize=8, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEE2E2', edgecolor='#DC2626', lw=1.2),
             arrowprops=dict(arrowstyle='->', lw=1.2, color='#DC2626'))

# E-02: Station 23.3m
enc2 = patches.Rectangle((21.05, 3.7), 4.5, 0.8, facecolor='#F97316', edgecolor='#C2410C', lw=2.0, zorder=5)
ax1.add_patch(enc2)
ax1.plot([23.3, 23.3], [3.7, 0], color='#C2410C', ls=':', lw=1.5, zorder=6)
ax1.plot(23.3, 0, marker='o', markersize=5, color='#C2410C', zorder=6)
ax1.annotate('Violation E-02 (3.60 m$^2$)\nStation 0+023.3 (Shop Ext.)', xy=(23.3, 4.1), xytext=(28.0, 1.2),
             ha='center', va='center', fontsize=8, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFEDD5', edgecolor='#EA580C', lw=1.2),
             arrowprops=dict(arrowstyle='->', lw=1.2, color='#EA580C'))

# Centerline chainage station ticks
for ch in range(0, 85, 10):
    ax1.plot([ch, ch], [-0.3, 0.3], color='#D97706', lw=1.2, zorder=4)
    ax1.text(ch, -0.9, f'0+{ch:03d}', ha='center', va='top', fontsize=6.8, color='#92400E', fontweight='semibold')

# Zone Callout text in Plan View
ax1.text(78, 3.75, 'Pedestrian Footpath (1.50 m)', ha='center', va='center', fontsize=7.2, fontweight='bold', color='#92400E')
ax1.text(78, 0.0, 'Carriageway (6.00 m)', ha='center', va='center', fontsize=7.5, fontweight='bold', color='#475569')

ax1.set_xlabel('Corridor Chainage Length (meters)', fontsize=9.5, fontweight='bold', labelpad=4)
ax1.set_ylabel('Transverse Width (m)', fontsize=9.5, fontweight='bold', labelpad=4)
ax1.tick_params(axis='both', labelsize=8.5)
ax1.grid(True, linestyle=':', alpha=0.4, color='#94A3B8')

# Custom clean legend
patch_cw = patches.Patch(facecolor='#E2E8F0', edgecolor='#94A3B8', label='Vehicular Carriageway (6.00 m)')
patch_fp = patches.Patch(facecolor='#FEF3C7', edgecolor='#D97706', label='Pedestrian Footpaths (1.50 m each)')
ax1.legend(handles=[line_cl, line_kerb, line_row, patch_cw, patch_fp],
           loc='upper right', ncol=5, fontsize=7.2, framealpha=0.95, edgecolor='#CBD5E1')

# =========================================================================
# (b) Detailed Transverse Vector Engineering Cross-Section at Parcel P-07
# =========================================================================
ax2.set_xlim(5.5, 17.5)
ax2.set_ylim(-0.4, 7.4)

# 1. Vehicular Carriageway Zone (-0.4 to 3.0 m)
ax2.fill_between([5.5, 17.5], [-0.4, -0.4], [3.0, 3.0], color='#F1F5F9', alpha=0.9, zorder=1)
ax2.text(6.0, 1.5, 'VEHICULAR CARRIAGEWAY\n(Paved Asphalt Corridor, Total Width = 6.00 m)',
         ha='left', va='center', fontsize=8.5, fontweight='bold', color='#64748B')

# 2. Road Centerline (y = 0.00 m)
ax2.axhline(0.0, color='#D97706', ls='--', lw=2.0, zorder=3)
ax2.text(17.3, 0.15, r'Road Centerline $\mathcal{L}_{\mathrm{center}}$ ($y = 0.00\,\mathrm{m}$)',
         ha='right', va='bottom', fontsize=8.5, fontweight='bold', color='#D97706')

# Directional arrows in carriageway lane
ax2.annotate('', xy=(10.0, 1.5), xytext=(8.0, 1.5),
             arrowprops=dict(arrowstyle='->', lw=1.8, color='#94A3B8'))
ax2.text(9.0, 1.8, 'Lane Travel Direction', ha='center', va='bottom', fontsize=7.5, color='#64748B')

# 3. Footpath Zone (y = 3.00 to 4.50 m, Width = 1.50 m)
ax2.fill_between([5.5, 17.5], [3.0, 3.0], [4.5, 4.5], color='#FEF3C7', alpha=0.85, zorder=1)

# 4. Kerb Line / Sidewalk Inner Edge (y = 3.00 m)
ax2.axhline(3.0, color='#0D9488', ls='-.', lw=2.2, zorder=4)
ax2.text(17.3, 3.12, r'KERB LINE / Footpath Edge ($y = 3.00\,\mathrm{m}$)',
         ha='right', va='bottom', fontsize=8.5, fontweight='bold', color='#0F766E')

# 5. Statutory ROW Boundary / Cadastral Property Deed Baseline (y = 4.50 m)
ax2.axhline(4.5, color='#DC2626', ls='-', lw=2.5, zorder=4)
ax2.text(17.3, 4.62, r'STATUTORY ROW LIMIT / PROPERTY DEED LINE ($y = 4.50\,\mathrm{m}$)',
         ha='right', va='bottom', fontsize=8.5, fontweight='bold', color='#B91C1C')

# 6. Private Deeded Property (Parcel P-07, y >= 4.50 m)
bld_plot = patches.Rectangle((8.5, 4.5), 5.0, 2.4, facecolor='#EFF6FF', edgecolor='#3B82F6', lw=1.8, zorder=2)
ax2.add_patch(bld_plot)
ax2.text(11.0, 5.7, 'Parcel P-07\n(Authoritative Deeded Private Property)', ha='center', va='center',
         fontsize=9.5, fontweight='bold', color='#1E40AF')

# Building Setback line inside private property
ax2.plot([8.5, 13.5], [5.2, 5.2], color='#3B82F6', ls=':', lw=1.5, zorder=3)
ax2.text(11.0, 5.0, 'Approved Building Plinth Line (Compliant Setback)', ha='center', va='top', fontsize=7.5, color='#2563EB')

# 7. Corridor Encroachment Area E_1 (y = 3.30 to 4.50 m, x = 8.5 to 13.5 m)
enc_zoom = patches.Rectangle((8.5, 3.3), 5.0, 1.2, facecolor='#EF4444', edgecolor='#B91C1C', lw=2.2, zorder=5)
ax2.add_patch(enc_zoom)
ax2.text(11.0, 3.9, r'UNLAWFUL CORRIDOR ENCROACHMENT $\mathcal{E}_1$' + '\n' +
         r'Area = 6.00 m$^2$ (Cantilevered Commercial Awning)',
         ha='center', va='center', fontsize=9.0, fontweight='bold', color='#FFFFFF', zorder=6)

# 8. Remaining Clear Pedestrian Width (y = 3.00 to 3.30 m, width = 0.30 m)
rect_res = patches.Rectangle((8.5, 3.0), 5.0, 0.3, facecolor='#FCA5A5', edgecolor='#DC2626', lw=1.0, hatch='//', alpha=0.7, zorder=4)
ax2.add_patch(rect_res)

# Perpendicular Chainage Projection Line to Centerline
ax2.plot([11.0, 11.0], [3.3, 0.0], color='#B91C1C', ls=':', lw=1.8, zorder=7)
ax2.plot(11.0, 0.0, marker='D', markersize=6, color='#D97706', zorder=8)
ax2.text(11.0, -0.25, 'Linear Chainage Station 0+011.0 (Centroid Project)',
         ha='center', va='top', fontsize=8.0, fontweight='bold', color='#92400E')

# DIMENSION ARROWS & ANNOTATIONS

# A. Projection Depth d_proj = 1.20 m
ax2.annotate('', xy=(14.2, 3.3), xytext=(14.2, 4.5),
             arrowprops=dict(arrowstyle='<->', lw=1.8, color='#0F172A'))
ax2.text(14.4, 3.9, 'Projection Depth\n$d_{\\mathrm{proj}} = 1.20\\,\\mathrm{m}$\n(80.0% Footpath Blockage)',
         va='center', fontsize=8.2, fontweight='bold', color='#991B1B')

# B. Residual Sidewalk Clearance = 0.30 m (Critical Safety Hazard)
ax2.annotate('', xy=(14.2, 3.0), xytext=(14.2, 3.3),
             arrowprops=dict(arrowstyle='<->', lw=1.5, color='#DC2626'))
ax2.text(14.4, 3.15, 'Residual Sidewalk = 0.30 m\n[CRITICAL HAZARD: 30 cm clearance\nforces pedestrians into active carriageway]',
         va='center', fontsize=7.2, fontweight='bold', color='#DC2626')

# C. Frontage Width w_front = 5.00 m
ax2.annotate('', xy=(8.5, 2.5), xytext=(13.5, 2.5),
             arrowprops=dict(arrowstyle='<->', lw=1.8, color='#0F172A'))
ax2.text(11.0, 2.3, r'Continuous Frontage Width $w_{\mathrm{front}} = 5.00\,\mathrm{m}$',
         ha='center', va='top', fontsize=8.5, fontweight='bold', color='#0F172A')

# D. Transverse Corridor Dimension Stack on Left
# Total Sidewalk width = 1.50 m
ax2.annotate('', xy=(5.8, 3.0), xytext=(5.8, 4.5),
             arrowprops=dict(arrowstyle='<->', lw=1.5, color='#0F766E'))
ax2.text(5.6, 3.75, 'Pedestrian\nSidewalk\n$W = 1.50\\,\\mathrm{m}$',
         ha='right', va='center', fontsize=7.5, fontweight='bold', color='#0F766E')

# Carriageway Half-Width = 3.00 m
ax2.annotate('', xy=(5.8, 0.0), xytext=(5.8, 3.0),
             arrowprops=dict(arrowstyle='<->', lw=1.5, color='#475569'))
ax2.text(5.6, 1.5, 'Carriageway\nHalf-Width\n$W/2 = 3.00\\,\\mathrm{m}$',
         ha='right', va='center', fontsize=7.5, fontweight='bold', color='#475569')

ax2.set_xlabel('Local Corridor Longitudinal X (meters)', fontsize=9.5, fontweight='bold', labelpad=4)
ax2.set_ylabel('Transverse Coordinate Y (m)', fontsize=9.5, fontweight='bold', labelpad=4)
ax2.tick_params(axis='both', labelsize=8.5)
ax2.grid(True, linestyle=':', alpha=0.4, color='#94A3B8')

plt.tight_layout()
plt.savefig(out_dir + "/fig3_encroachment_attribution.png", dpi=300, bbox_inches='tight')
plt.close()
print("Successfully generated upgraded fig3_encroachment_attribution.png with all corridor lines and civil dimensions!")
