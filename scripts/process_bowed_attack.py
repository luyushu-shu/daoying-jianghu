#!/usr/bin/env python3
"""
Process the bowed-attack sprite sheet (magenta background, 4×3 grid, 12 frames).
Pipeline:
  1. Split into 12 raw cells
  2. Chroma-key remove magenta (#FF00FF) → RGBA transparent
  3. Crop tight bounding box per frame
  4. Scale character to ~328 px height (same as idle)
  5. Paste onto 680×480 canvas, foot baseline at Y=437, center X=340
  6. Save individual PNGs, 4×3 sheet, horizontal strip, GIFs
"""
import os
from pathlib import Path
from PIL import Image
import numpy as np

# ─── Paths ────────────────────────────────────────────────────────────────────
SOURCE    = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列\attack-bowed-source.png")
OUT_DIR   = Path(r"C:\Users\luyus\Desktop\刀影江湖\New Tuanjie Project\Assets\Sprites\Player\Attack")
DESIGN_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Constants ─────────────────────────────────────────────────────────────────
COLS, ROWS   = 4, 3
CANVAS_W     = 680
CANVAS_H     = 480
TARGET_H     = 328    # match idle character height
FOOT_Y       = 437    # 0.09 × 480 = 43.2 → baseline
CENTER_X     = 340

# ─── Step 1: Load & split ──────────────────────────────────────────────────────
src = Image.open(SOURCE).convert("RGBA")
W, H = src.size
fw, fh = W // COLS, H // ROWS
print(f"Source {W}×{H}, cell {fw}×{fh}")

raw_frames = []
for r in range(ROWS):
    for c in range(COLS):
        box = (c*fw, r*fh, (c+1)*fw, (r+1)*fh)
        raw_frames.append(src.crop(box))

# ─── Step 2: Remove magenta background ────────────────────────────────────────
def remove_magenta(img: Image.Image, threshold=40, feather=40) -> Image.Image:
    arr = np.array(img, dtype=np.float32)
    r, g, b = arr[...,0], arr[...,1], arr[...,2]
    # Distance from pure magenta (255, 0, 255)
    dist = np.sqrt((r - 255)**2 + g**2 + (b - 255)**2)
    # Despill: remove magenta tint from near-edge pixels
    spill = np.maximum(0, np.minimum(r - g, b - g))
    arr[...,0] = np.clip(r - 0.9 * spill, 0, 255)
    arr[...,2] = np.clip(b - 0.9 * spill, 0, 255)
    # Alpha: 0 where magenta, 255 where clearly foreground
    raw_a = np.clip((dist - threshold) / feather, 0, 1) * 255
    out = arr.astype(np.uint8)
    out[...,3] = raw_a.astype(np.uint8)
    return Image.fromarray(out, "RGBA")

# ─── Step 3: Tight crop ────────────────────────────────────────────────────────
def tight_crop(img):
    arr = np.array(img)
    alpha = arr[...,3]
    rows = np.where(alpha.max(axis=1) > 20)[0]
    cols = np.where(alpha.max(axis=0) > 20)[0]
    if len(rows)==0 or len(cols)==0:
        return img
    return img.crop((cols[0], rows[0], cols[-1]+1, rows[-1]+1))

# ─── Step 4: Foot centroid ─────────────────────────────────────────────────────
def foot_centroid_x(img, foot_rows=15):
    arr = np.array(img)
    h = arr.shape[0]
    bottom = arr[max(0, h-foot_rows):h]
    alpha = bottom[...,3].astype(np.float32)
    total = alpha.sum()
    if total < 1:
        return img.size[0] / 2.0
    xs = np.arange(img.size[0], dtype=np.float32)
    return float((alpha * xs[np.newaxis,:]).sum() / total)

# ─── Process all frames ────────────────────────────────────────────────────────
processed = []
for i, raw in enumerate(raw_frames):
    clean = remove_magenta(raw)
    crop  = tight_crop(clean)
    cw, ch = crop.size
    if ch == 0:
        print(f"Frame {i+1}: empty!")
        processed.append(Image.new("RGBA", (CANVAS_W, CANVAS_H)))
        continue
    scale  = TARGET_H / ch
    new_w  = max(1, int(cw * scale))
    new_h  = int(ch * scale)
    scaled = crop.resize((new_w, new_h), Image.LANCZOS)
    fx     = foot_centroid_x(scaled)
    px     = int(CENTER_X - fx)
    py     = FOOT_Y - new_h
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0,0,0,0))
    canvas.paste(scaled, (px, py), scaled)
    processed.append(canvas)
    print(f"Frame {i+1:2d}: crop {cw}×{ch} → scale={scale:.3f} new={new_w}×{new_h} paste@({px},{py}) fx={fx:.1f}")

# ─── Save PNGs ─────────────────────────────────────────────────────────────────
for i, frame in enumerate(processed):
    frame.save(OUT_DIR / f"attack-{i+1}.png", "PNG")
print(f"Saved 12 PNGs to {OUT_DIR}")

# ─── Transparent 4×3 sheet ─────────────────────────────────────────────────────
sheet = Image.new("RGBA", (CANVAS_W*COLS, CANVAS_H*ROWS), (0,0,0,0))
for i, frame in enumerate(processed):
    r, c = divmod(i, COLS)
    sheet.paste(frame, (c*CANVAS_W, r*CANVAS_H), frame)
sheet.save(OUT_DIR / "sheet-transparent.png", "PNG")

# ─── Horizontal strip for README ──────────────────────────────────────────────
strip = Image.new("RGBA", (CANVAS_W*12, CANVAS_H), (0,0,0,0))
for i, frame in enumerate(processed):
    strip.paste(frame, (i*CANVAS_W, 0), frame)
strip.save(DESIGN_DIR / "attack-sequence.png", "PNG")
print("Saved sheet + strip")

# ─── GIFs ─────────────────────────────────────────────────────────────────────
def make_gif(frames, path, duration=85):
    rgb = []
    for f in frames:
        bg = Image.new("RGB", f.size, (255,255,255))
        bg.paste(f, mask=f.split()[3])
        rgb.append(bg)
    rgb[0].save(path, save_all=True, append_images=rgb[1:], loop=0, duration=duration)

make_gif(processed,       OUT_DIR / "animation.gif")
make_gif(processed[0:4],  OUT_DIR / "attack-hit1.gif")
make_gif(processed[4:8],  OUT_DIR / "attack-hit2.gif")
make_gif(processed[8:12], OUT_DIR / "attack-hit3.gif")
print("Saved GIFs")

# ─── QC ───────────────────────────────────────────────────────────────────────
print("\n=== QC ===")
for i, frame in enumerate(processed):
    arr   = np.array(frame)
    alpha = arr[...,3]
    rows  = np.where(alpha.max(axis=1) > 20)[0]
    if len(rows)==0:
        print(f"Frame {i+1}: EMPTY"); continue
    h = rows[-1]-rows[0]+1
    bottom = rows[-1]
    # check edge touch
    edge_l = alpha[:,0].max() > 20
    edge_r = alpha[:,CANVAS_W-1].max() > 20
    edge_t = alpha[0,:].max() > 20
    edge_b = alpha[CANVAS_H-1,:].max() > 20
    flags = []
    if edge_l: flags.append("EDGE_LEFT")
    if edge_r: flags.append("EDGE_RIGHT")
    if edge_t: flags.append("EDGE_TOP")
    if edge_b: flags.append("EDGE_BOTTOM")
    warn = " ⚠ " + " ".join(flags) if flags else ""
    print(f"Frame {i+1:2d}: char_h={h}, bottom={bottom}{warn}")

print("\nDone!")
