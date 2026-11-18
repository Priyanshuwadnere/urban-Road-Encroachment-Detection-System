"""
YOLO Instance Segmentation Polygon Visualizer.
Overlays physical structure polygon annotations (Classes 0-7) onto drone images
using distinct color coding per class.
"""

import os
import sys
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.abspath("."))
from src.config import PHYSICAL_CLASSES, ACADEMIC_DISCLAIMER
from src.ml.annotation_validator import AnnotationValidator

# Color mapping for physical classes (RGB tuples)
CLASS_COLORS = {
    0: (0, 150, 255),    # building: Blue
    1: (255, 100, 0),    # staircase: Orange
    2: (255, 0, 100),    # shop_extension: Pink/Magenta
    3: (150, 0, 255),    # veranda: Purple
    4: (255, 200, 0),    # shed: Yellow
    5: (0, 200, 100),    # ramp: Green
    6: (0, 255, 255),    # awning: Cyan
    7: (128, 128, 128),  # compound_wall: Grey
}


def draw_yolo_polygons_on_image(
    image_path: str,
    label_path: str,
    output_path: Optional[str] = None,
    alpha: int = 80,
) -> Image.Image:
    """
    Overlay YOLO polygon annotations from label_path onto image_path.
    Saves output to output_path if provided, and returns PIL Image.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = Image.open(image_path).convert("RGBA")
    img_w, img_h = img.size

    # Create transparent overlay layer for filled polygons
    overlay = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    draw_img = ImageDraw.Draw(img)

    is_valid, errors, polys = AnnotationValidator.validate_label_file(label_path, image_path)

    if is_valid and polys:
        for poly_data in polys:
            cid = poly_data["class_id"]
            cname = poly_data["class_name"]
            norm_pts = poly_data["vertices"]

            # Denormalize coordinates [0, 1] -> pixel coordinates (x, y)
            pixel_pts = [(int(x * img_w), int(y * img_h)) for x, y in norm_pts]

            color_rgb = CLASS_COLORS.get(cid, (255, 255, 255))
            color_fill = color_rgb + (alpha,)
            color_stroke = color_rgb + (255,)

            # Draw filled semi-transparent polygon & outline
            draw_overlay.polygon(pixel_pts, fill=color_fill, outline=color_stroke)
            draw_img.polygon(pixel_pts, outline=color_stroke, width=2)

            # Draw class label tag at first vertex
            if pixel_pts:
                label_text = f"{cid}: {cname}"
                tx, ty = pixel_pts[0]
                draw_img.rectangle([tx, ty - 14, tx + len(label_text) * 7, ty], fill=(0, 0, 0, 180))
                draw_img.text((tx + 2, ty - 12), label_text, fill=(255, 255, 255, 255))

    # Composite overlay onto base image
    composite = Image.alpha_composite(img, overlay).convert("RGB")

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        composite.save(output_path, quality=95)

    return composite
