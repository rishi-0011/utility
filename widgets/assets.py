import os
import base64
import io
from PIL import Image, ImageTk

# Base directory for the Utility project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load Base64 Strings
def _load_b64(filename):
    for candidate in [
        os.path.join(BASE_DIR, "assets", "icons", filename),
        os.path.join(BASE_DIR, "assets", "images", filename),
        os.path.join(BASE_DIR, "assets", filename),
        os.path.join(BASE_DIR, filename),
    ]:
        if os.path.exists(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                pass
    return ""

CARONA_LOGO_B64 = _load_b64("carona_logo_b64.txt")
PILL_STEPPER_B64 = _load_b64("pill_stepper_b64.txt")
INFO_BUBBLE_B64 = _load_b64("info_bubble_b64.txt")

# Image Caches
CARONA_LOGO_CACHE = {}
PILL_STEPPER_CACHE = {}
INFO_BUBBLE_CACHE = {}

def get_asset_file(*rel_paths):
    """Searches for an asset file in project root, assets/images, assets/icons, or assets."""
    for rel in rel_paths:
        candidates = [
            os.path.join(BASE_DIR, rel),
            os.path.join(BASE_DIR, "assets", "images", rel),
            os.path.join(BASE_DIR, "assets", "icons", rel),
            os.path.join(BASE_DIR, "assets", rel),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
    return None

def get_carona_logo_image(height=28):
    """Returns a PhotoImage of the Carona Power logo scaled to the requested height."""
    if height in CARONA_LOGO_CACHE:
        return CARONA_LOGO_CACHE[height]

    file_path = get_asset_file("carona_logo_ui.png", "carona_logo_transparent.png", "carona_logo.png")
    if file_path:
        try:
            raw = Image.open(file_path)
            w = int(raw.width * (height / raw.height))
            img = ImageTk.PhotoImage(raw.resize((w, height), Image.Resampling.LANCZOS))
            CARONA_LOGO_CACHE[height] = img
            return img
        except Exception:
            pass

    if CARONA_LOGO_B64:
        try:
            raw_data = base64.b64decode(CARONA_LOGO_B64)
            raw = Image.open(io.BytesIO(raw_data))
            w = int(raw.width * (height / raw.height))
            img = ImageTk.PhotoImage(raw.resize((w, height), Image.Resampling.LANCZOS))
            CARONA_LOGO_CACHE[height] = img
            return img
        except Exception:
            pass

    return None

get_carona_logo = get_carona_logo_image

def get_pill_stepper_image(width=18, height=26):
    """Returns a PhotoImage of the authentic LabVIEW pill stepper."""
    key = (width, height)
    if key in PILL_STEPPER_CACHE:
        return PILL_STEPPER_CACHE[key]

    file_path = get_asset_file("pill_stepper_ui.png", "pill_stepper.png")
    if file_path:
        try:
            raw = Image.open(file_path).resize((width, height), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(raw)
            PILL_STEPPER_CACHE[key] = img
            return img
        except Exception:
            pass

    if PILL_STEPPER_B64:
        try:
            raw_data = base64.b64decode(PILL_STEPPER_B64)
            raw = Image.open(io.BytesIO(raw_data)).resize((width, height), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(raw)
            PILL_STEPPER_CACHE[key] = img
            return img
        except Exception:
            pass

    return None

def get_info_bubble_image(size=62):
    """Returns a PhotoImage of the information bubble icon."""
    if size in INFO_BUBBLE_CACHE:
        return INFO_BUBBLE_CACHE[size]

    file_path = get_asset_file("info_bubble_ui.png", "info_bubble.png")
    if file_path:
        try:
            raw = Image.open(file_path).resize((size, size), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(raw)
            INFO_BUBBLE_CACHE[size] = img
            return img
        except Exception:
            pass

    if INFO_BUBBLE_B64:
        try:
            raw_data = base64.b64decode(INFO_BUBBLE_B64)
            raw = Image.open(io.BytesIO(raw_data)).resize((size, size), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(raw)
            INFO_BUBBLE_CACHE[size] = img
            return img
        except Exception:
            pass

    return None

ARROW_BUTTON_CACHE = {}

def get_arrow_button_image(direction="increase", width=64, height=20, fg="#000000"):
    """Returns a PhotoImage of authentic LabVIEW increase (< -  - >) or decrease (- >  < -) arrows with centered hyphens."""
    key = (direction, width, height, fg)
    if key in ARROW_BUTTON_CACHE:
        return ARROW_BUTTON_CACHE[key]

    file_path = get_asset_file(f"arrow_{direction}.png")
    if file_path and os.path.exists(file_path):
        try:
            raw = Image.open(file_path).resize((width, height), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(raw)
            ARROW_BUTTON_CACHE[key] = img
            return img
        except Exception:
            pass

    # Dynamic vector rendering fallback ensuring exact horizontal centerline alignment
    from PIL import ImageDraw
    img_pil = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img_pil)
    cy = height // 2
    cx = width // 2
    lw = 2
    cw = 6
    ch = 5
    hl = 9
    gap = 10

    if direction == "increase":
        # < -    - >
        x_l = cx - gap // 2 - hl - cw
        draw.line([(x_l + cw, cy - ch), (x_l, cy)], fill=fg, width=lw)
        draw.line([(x_l + cw, cy + ch), (x_l, cy)], fill=fg, width=lw)
        x_h1 = x_l + cw + 3
        draw.line([(x_h1, cy), (x_h1 + hl, cy)], fill=fg, width=lw)

        x_h2 = cx + gap // 2
        draw.line([(x_h2, cy), (x_h2 + hl, cy)], fill=fg, width=lw)
        x_r = x_h2 + hl + 3
        draw.line([(x_r, cy - ch), (x_r + cw, cy)], fill=fg, width=lw)
        draw.line([(x_r, cy + ch), (x_r + cw, cy)], fill=fg, width=lw)
    else:
        # - >    < -
        x_h1 = cx - gap // 2 - cw - hl - 3
        draw.line([(x_h1, cy), (x_h1 + hl, cy)], fill=fg, width=lw)
        x_r = x_h1 + hl + 3
        draw.line([(x_r, cy - ch), (x_r + cw, cy)], fill=fg, width=lw)
        draw.line([(x_r, cy + ch), (x_r + cw, cy)], fill=fg, width=lw)

        x_l = cx + gap // 2
        draw.line([(x_l + cw, cy - ch), (x_l, cy)], fill=fg, width=lw)
        draw.line([(x_l + cw, cy + ch), (x_l, cy)], fill=fg, width=lw)
        x_h2 = x_l + cw + 3
        draw.line([(x_h2, cy), (x_h2 + hl, cy)], fill=fg, width=lw)

    img = ImageTk.PhotoImage(img_pil)
    ARROW_BUTTON_CACHE[key] = img
    return img

def get_increase_arrow_image(width=64, height=20, fg="#000000"):
    return get_arrow_button_image("increase", width, height, fg)

def get_decrease_arrow_image(width=64, height=20, fg="#000000"):
    return get_arrow_button_image("decrease", width, height, fg)
