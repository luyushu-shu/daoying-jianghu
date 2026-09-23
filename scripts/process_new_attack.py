#!/usr/bin/env python3
"""
Process the new attack sprite sheet (white background, 4×3 grid, 12 frames).
Pipeline:
  1. Split into 12 raw frames
  2. Remove white/near-white background → RGBA transparent
  3. Crop tight bounding box per frame
  4. Scale character to ~328 px height
  5. Paste onto 680×480 canvas with foot baseline at Y=437
  6. Save individual PNGs, transparent sheet (4×3), horizontal strip, GIFs
"""

import os, sys
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np

# ─── Paths ───────────────────────────────────────────────────────────────────
SOURCE  = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列\attack-new-source.png")
OUT_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\New Tuanjie Project\Assets\Sprites\Player\Attack")
DESIGN_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列")
OUT_DIR.mkdir(parents=True, exist_ok=True)
DESIGN_DIR.mkdir(parents=True, exist_ok=True)

# ─── Constants ────────────────────────────────────────────────────────────────
COLS, ROWS   = 4, 3
CANVAS_W, CANVAS_H = 680, 480
TARGET_H     = 328   # idle character height
FOOT_Y       = 437   # baseline (0.09 pivot × 480)
CENTER_X     = 340   # canvas center

# ─── Step 1: Load & Split ────────────────────────────────────────────────────
src = Image.open(SOURCE).convert("RGBA")
W, H = src.size
fw = W // COLS
fh = H // ROWS
print(f"Source: {W}×{H}, cell: {fw}×{fh}")

raw_frames = []
for r in range(ROWS):
    for c in range(COLS):
        box = (c*fw, r*fh, (c+1)*fw, (r+1)*fh)
        raw_frames.append(src.crop(box))
print(f"Extracted {len(raw_frames)} frames")

# ─── Step 2: Remove White Background ────────────────────────────────────────
def remove_white_bg(img: Image.Image, threshold=230, feather=15) -> Image.Image:
    arr = np.array(img, dtype=np.float32)   # H×W×4
    r, g, b, a_in = arr[...,0], arr[...,1], arr[...,2], arr[...,3]
    brightness = (r + g + b) / 3.0
    # "whiteness": all channels must be high AND close together
    max_ch = np.maximum(np.maximum(r, g), b)
    min_ch = np.minimum(np.minimum(r, g), b)
    spread = max_ch - min_ch  # low spread = grey/white
    # alpha: 0 where white, 1 where coloured
    dist_from_white = 255.0 - brightness          # 0 → pure white
    colour_score    = spread                      # 0 → grey/white
    raw_alpha = np.minimum(dist_from_white, colour_score * 3)
    raw_alpha = np.clip(raw_alpha, 0, feather) / feather  # 0..1
    new_a = (raw_alpha * 255).astype(np.uint8)
    out = arr.astype(np.uint8).copy()
    out[..., 3] = new_a
    return Image.fromarray(out, "RGBA")

# ─── Step 3 & 4: Crop tight, measure character height, scale ─────────────────
def tight_crop(img: Image.Image):
    arr = np.array(img)
    alpha = arr[..., 3]
    rows = np.where(alpha.max(axis=1) > 20)[0]
    cols = np.where(alpha.max(axis=0) > 20)[0]
    if len(rows) == 0 or len(cols) == 0:
        return img
    return img.crop((cols[0], rows[0], cols[-1]+1, rows[-1]+1))

def foot_centroid_x(img: Image.Image, foot_rows=15) -> float:
    """Horizontal alpha centroid of bottom N rows (foot position)."""
    arr = np.array(img)
    h = arr.shape[0]
    bottom = arr[max(0, h-foot_rows):h]
    alpha  = bottom[..., 3].astype(np.float32)
    total  = alpha.sum()
    if total < 1:
        return img.size[0] / 2.0
    xs = np.arange(img.size[0], dtype=np.float32)
    return float((alpha * xs).sum() / total)

processed = []
for i, raw in enumerate(raw_frames):
    clean = remove_white_bg(raw)
    crop  = tight_crop(clean)
    cw, ch = crop.size
    if ch == 0:
        print(f"Frame {i+1}: empty after crop!")
        processed.append(Image.new("RGBA", (CANVAS_W, CANVAS_H), (0,0,0,0)))
        continue
    # Scale so character height == TARGET_H
    scale  = TARGET_H / ch
    new_w  = int(cw * scale)
    new_h  = int(ch * scale)
    scaled = crop.resize((new_w, new_h), Image.LANCZOS)
    # Foot alignment
    fx = foot_centroid_x(scaled)
    px = int(CENTER_X - fx)
    py = FOOT_Y - new_h
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.paste(scaled, (px, py), scaled)
    processed.append(canvas)
    print(f"Frame {i+1:2d}: cell {cw}×{ch} → scaled {new_w}×{new_h} "
          f"paste @({px},{py}) foot_x={fx:.1f}")

# ─── Step 5: Save individual PNGs ────────────────────────────────────────────
for i, frame in enumerate(processed):
    path = OUT_DIR / f"attack-{i+1}.png"
    frame.save(path, "PNG")
print(f"Saved {len(processed)} PNGs to {OUT_DIR}")

# ─── Step 6: Transparent 4×3 sheet ───────────────────────────────────────────
sheet = Image.new("RGBA", (CANVAS_W*COLS, CANVAS_H*ROWS), (0, 0, 0, 0))
for i, frame in enumerate(processed):
    r, c = divmod(i, COLS)
    sheet.paste(frame, (c*CANVAS_W, r*CANVAS_H), frame)
sheet_path = OUT_DIR / "sheet-transparent.png"
sheet.save(sheet_path, "PNG")
print(f"Saved sheet: {sheet_path}")

# ─── Step 7: Horizontal strip for README ─────────────────────────────────────
strip = Image.new("RGBA", (CANVAS_W*12, CANVAS_H), (0, 0, 0, 0))
for i, frame in enumerate(processed):
    strip.paste(frame, (i*CANVAS_W, 0), frame)
strip_path = DESIGN_DIR / "attack-sequence.png"
strip.save(strip_path, "PNG")
print(f"Saved strip: {strip_path}")

# ─── Step 8: GIF animations ──────────────────────────────────────────────────
def make_gif(frames, path, duration=85):
    # Convert RGBA → RGB with white BG for GIF compatibility
    rgb = []
    for f in frames:
        bg = Image.new("RGB", f.size, (255, 255, 255))
        bg.paste(f, mask=f.split()[3])
        rgb.append(bg)
    rgb[0].save(path, save_all=True, append_images=rgb[1:],
                loop=0, duration=duration, optimize=False)

make_gif(processed,       OUT_DIR / "animation.gif")
make_gif(processed[0:4],  OUT_DIR / "attack-hit1.gif")
make_gif(processed[4:8],  OUT_DIR / "attack-hit2.gif")
make_gif(processed[8:12], OUT_DIR / "attack-hit3.gif")
print("Saved GIFs")

# ─── Measure final bounds for QC ─────────────────────────────────────────────
print("\n=== QC ===")
for i, frame in enumerate(processed):
    arr   = np.array(frame)
    alpha = arr[..., 3]
    rows  = np.where(alpha.max(axis=1) > 20)[0]
    if len(rows) == 0:
        print(f"Frame {i+1}: EMPTY")
        continue
    h = rows[-1] - rows[0] + 1
    bottom = rows[-1]
    print(f"Frame {i+1:2d}: char_h={h}, bottom_row={bottom}")

print("\nDone!")
