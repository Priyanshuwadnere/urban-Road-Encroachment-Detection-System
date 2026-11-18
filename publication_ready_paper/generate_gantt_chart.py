import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

out_dir = Path(r"e:\Urban Road Encroachment Detection System\publication_ready_paper\figures")
out_dir.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

def generate_gantt_chart():
    fig, ax = plt.subplots(figsize=(12, 6.8), dpi=300)
    ax.set_xlim(0, 16.5)
    ax.set_ylim(0, 9.8)
    ax.axis('off')

    # Background canvas
    canvas = patches.Rectangle((0, 0), 16.5, 9.8, facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=1.5)
    ax.add_patch(canvas)

    # Header Banner (NMIMS Maroon / Red)
    hdr_banner = patches.Rectangle((0.2, 8.8), 16.1, 0.8, facecolor='#B91C1C', edgecolor='none')
    ax.add_patch(hdr_banner)
    ax.text(8.25, 9.2, "MUKESH PATEL SCHOOL OF TECHNOLOGY MANAGEMENT & ENGINEERING, SHIRPUR",
            ha='center', va='center', fontsize=11, fontweight='bold', color='#FFFFFF')

    # Slide Title
    ax.text(8.25, 8.35, "Project Development Timeline (Gantt Chart)",
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1E293B')

    # Table Header Box
    tbl_hdr = patches.Rectangle((0.4, 7.2), 15.7, 0.75, facecolor='#1E40AF', edgecolor='#1E3A8A', lw=1.2)
    ax.add_patch(tbl_hdr)

    # Columns
    ax.text(1.7, 7.57, "Task / Activity", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#FFFFFF')
    ax.text(3.7, 7.57, "Duration\n(Start – End)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#FFFFFF')

    weeks = [
        ("W1", "13–19\nJul"),
        ("W2", "20–26\nJul"),
        ("W3", "27 Jul–\n2 Aug"),
        ("W4", "3–9\nAug"),
        ("W5", "10–16\nAug"),
        ("W6", "17–23\nAug"),
        ("W7", "24–30\nAug"),
        ("W8", "31 Aug–\n6 Sep"),
        ("W9", "7–13\nSep"),
        ("W10", "14–20\nSep"),
        ("W11", "21–27\nSep"),
        ("W12", "28 Sep–\n4 Oct"),
        ("W13", "5–11\nOct"),
        ("W14", "12–18\nOct"),
        ("W15", "19–25\nOct"),
        ("W16", "26–30\nOct"),
    ]

    x_start = 4.6
    w_step = 0.718

    # Vertical gridlines & Week labels in Header
    for idx, (w_lbl, d_lbl) in enumerate(weeks):
        cx = x_start + idx * w_step
        # Header text
        ax.text(cx + w_step/2, 7.68, w_lbl, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#FFFFFF')
        ax.text(cx + w_step/2, 7.38, d_lbl, ha='center', va='center', fontsize=6.2, color='#E2E8F0')

        # Vertical divider line inside table
        ax.plot([cx, cx], [0.6, 7.95], color='#E2E8F0', lw=0.8, zorder=1)
    ax.plot([x_start + 16*w_step, x_start + 16*w_step], [0.6, 7.95], color='#E2E8F0', lw=0.8, zorder=1)

    # Tasks configuration matching the presentation slide
    tasks = [
        {
            "id": 1,
            "name": "1. Problem Statement",
            "duration": "13 Jul – 20 Jul\n(1 Week)",
            "start_w": 0, "span_w": 1.0,
            "color": "#3B82F6", "badge_color": "#2563EB"
        },
        {
            "id": 2,
            "name": "2. Literature Review",
            "duration": "15 Jul – 30 Jul\n(2 Weeks)",
            "start_w": 0.3, "span_w": 2.4,
            "color": "#06B6D4", "badge_color": "#0891B2"
        },
        {
            "id": 3,
            "name": "3. Review Paper",
            "duration": "25 Jul – 6 Aug\n(2 Weeks)",
            "start_w": 1.7, "span_w": 2.0,
            "color": "#22C55E", "badge_color": "#16A34A"
        },
        {
            "id": 4,
            "name": "4. Dataset Preparation",
            "duration": "30 Jul – 6 Aug\n(1 Week)",
            "start_w": 2.4, "span_w": 1.3,
            "color": "#14B8A6", "badge_color": "#0D9488"
        },
        {
            "id": 5,
            "name": "5. ML Model Development",
            "duration": "6 Aug – 25 Sep\n(7 Weeks)",
            "start_w": 3.7, "span_w": 7.3,
            "color": "#F59E0B", "badge_color": "#D97706"
        },
        {
            "id": 6,
            "name": "6. Comparative Analysis",
            "duration": "25 Sep – 2 Oct\n(1 Week)",
            "start_w": 11.0, "span_w": 1.0,
            "color": "#EF4444", "badge_color": "#DC2626"
        },
        {
            "id": 7,
            "name": "7. Research Paper",
            "duration": "2 Oct – 20 Oct\n(3 Weeks)",
            "start_w": 12.0, "span_w": 2.6,
            "color": "#8B5CF6", "badge_color": "#7C3AED"
        },
        {
            "id": 8,
            "name": "8. Final Presentation",
            "duration": "20 Oct – 30 Oct\n(2 Weeks)",
            "start_w": 14.6, "span_w": 1.4,
            "color": "#EC4899", "badge_color": "#DB2777"
        },
    ]

    row_y = 6.55
    y_step = 0.72

    for t in tasks:
        y_pos = row_y - (t["id"] - 1) * y_step

        # Alternating row background
        bg_col = "#F8FAFC" if t["id"] % 2 == 1 else "#FFFFFF"
        row_rect = patches.Rectangle((0.4, y_pos - 0.32), 15.7, 0.68, facecolor=bg_col, edgecolor='#E2E8F0', lw=0.6, zorder=0)
        ax.add_patch(row_rect)

        # Task Name with icon badge
        badge = patches.Circle((0.75, y_pos), 0.18, facecolor=t["badge_color"], edgecolor='none', zorder=2)
        ax.add_patch(badge)
        ax.text(0.75, y_pos, str(t["id"]), ha='center', va='center', fontsize=7.5, fontweight='bold', color='#FFFFFF', zorder=3)

        ax.text(1.05, y_pos, t["name"].split(". ")[1], ha='left', va='center', fontsize=8.5, fontweight='bold', color='#1E293B', zorder=3)

        # Duration Text
        ax.text(3.7, y_pos, t["duration"].replace("\n", " "), ha='center', va='center', fontsize=7.5, color='#475569', zorder=3)

        # Gantt Bar
        bar_x = x_start + t["start_w"] * w_step
        bar_w = t["span_w"] * w_step
        g_bar = patches.FancyBboxPatch((bar_x, y_pos - 0.16), bar_w, 0.32,
                                       boxstyle="round,pad=0.03,rounding_size=0.12",
                                       facecolor=t["color"], edgecolor=t["badge_color"], lw=1.2, zorder=4)
        ax.add_patch(g_bar)

    # Slide Footer Info
    ax.text(15.9, 0.35, "16", ha='right', va='center', fontsize=8.5, color='#94A3B8')
    ax.text(0.6, 0.35, "Department of Information Technology, MPSTME Shirpur Campus | Academic Session: 2026–2027",
            ha='left', va='center', fontsize=7.5, color='#64748B')

    plt.tight_layout()
    out_file = out_dir / "fig_gantt_chart.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated Gantt Chart image: {out_file}")

if __name__ == "__main__":
    generate_gantt_chart()
