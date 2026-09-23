#!/usr/bin/env python3
"""
Process v13 attack sheet (16:9 aspect ratio, 4x3 grid, 12 frames).
Key improvements:
- Wide 16:9 canvas provides ample horizontal room: zero sword truncation, zero border overlap.
- Uses UNIFORM_SCALE based on neutral standing frame (Frame 1) so bowed/crouching poses
  naturally have lowered torso/head height while anatomical scale is 100% consistent.
- Foot baseline aligned to Y=437 on 680x480 canvas, matching Player Idle/Run/Dodge.
"""
from pathlib import Path
from PIL import Image
import numpy as np

SOURCE     = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列\attack-v13-source.png")
OUT_DIR    = Path(r"C:\Users\luyus\Desktop\刀影江湖\New Tuanjie Project\Assets\Sprites\Player\Attack")
DESIGN_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列")
OUT_DIR.mkdir(parents=True, exist_ok=True)

COLS, ROWS   = 4, 3
CANVAS_W     = 680
CANVAS_H     = 480
TARGET_H     = 328    # Idle character height
FOOT_Y       = 437    # baseline (0.09 pivot * 480)
CENTER_X     = 340

src = Image.open(SOURCE).convert("RGBA")
W, H = src.size
cw, ch = W // COLS, H // ROWS
print(f"Source size {W}x{H}, cell {cw}x{ch}")

# Remove magenta with despill
def remove_magenta_and_clean(img, threshold=35, feather=40):
    arr = np.array(img, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    dist = np.sqrt((r - 255.0)**2 + g**2 + (b - 255.0)**2)
    spill = np.maximum(0, np.minimum(r - g, b - g))
    r_clean = np.clip(r - 0.95 * spill, 0, 255)
    b_clean = np.clip(b - 0.95 * spill, 0, 255)
    raw_a = np.clip((dist - threshold) / feather, 0, 1) * 255
    out = arr.astype(np.uint8)
    out[..., 0] = r_clean.astype(np.uint8)
    out[..., 2] = b_clean.astype(np.uint8)
    out[..., 3] = raw_a.astype(np.uint8)
    return Image.fromarray(out, "RGBA")

def tight_crop(img):
    arr = np.array(img)
    alpha = arr[..., 3]
    rows = np.where(alpha.max(axis=1) > 25)[0]
    cols = np.where(alpha.max(axis=0) > 25)[0]
    if len(rows) == 0 or len(cols) == 0:
        return img
    return img.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))

def foot_centroid_x(img, foot_rows=15):
    arr = np.array(img)
    h = arr.shape[0]
    bottom = arr[max(0, h - foot_rows):h]
    alpha = bottom[..., 3].astype(np.float32)
    total = alpha.sum()
    if total < 1:
        return img.size[0] / 2.0
    xs = np.arange(img.size[0], dtype=np.float32)
    return float((alpha * xs[np.newaxis, :]).sum() / total)

# Step 1: Crop cells
raw_cells = []
for r in range(ROWS):
    for c in range(COLS):
        x0 = c * cw
        y0 = r * ch
        x1 = min((c + 1) * cw, W - 2 if c == COLS - 1 else (c + 1) * cw)
        y1 = min((r + 1) * ch, H - 2 if r == ROWS - 1 else (r + 1) * ch)
        raw_cells.append(src.crop((x0, y0, x1, y1)))

# Step 2: Clean and crop
cleaned_frames = []
for i, cell in enumerate(raw_cells):
    clean = remove_magenta_and_clean(cell)
    crop = tight_crop(clean)
    cleaned_frames.append(crop)

# Step 3: Determine UNIFORM_SCALE from neutral standing pose (Frame 1)
f1_w, f1_h = cleaned_frames[0].size
UNIFORM_SCALE = TARGET_H / float(f1_h)
print(f"Neutral standing height (Frame 1): {f1_h}px -> Uniform scale = {UNIFORM_SCALE:.4f}")

# Step 4: Scale and place onto 680x480 canvas
processed = []
for i, crop in enumerate(cleaned_frames):
    cw_crop, ch_crop = crop.size
    new_w = max(1, int(round(cw_crop * UNIFORM_SCALE)))
    new_h = max(1, int(round(ch_crop * UNIFORM_SCALE)))
    scaled = crop.resize((new_w, new_h), Image.LANCZOS)
    
    fx = foot_centroid_x(scaled)
    px = int(round(CENTER_X - fx))
    py = int(round(FOOT_Y - new_h))
    
    # Safe boundary clamping: keep at least 15px inside canvas
    if px + new_w > CANVAS_W - 15:
        px = CANVAS_W - 15 - new_w
    if px < 15:
        px = 15
    
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.paste(scaled, (px, py), scaled)
    processed.append(canvas)
    
    # QC check
    arr = np.array(canvas)
    alpha = arr[..., 3]
    flags = []
    if alpha[:, 0].max() > 20:          flags.append("EDGE_L")
    if alpha[:, CANVAS_W - 1].max() > 20: flags.append("EDGE_R")
    if alpha[0, :].max() > 20:          flags.append("EDGE_T")
    if alpha[CANVAS_H - 1, :].max() > 20: flags.append("EDGE_B")
    rows_nz = np.where(alpha.max(axis=1) > 20)[0]
    char_h = rows_nz[-1] - rows_nz[0] + 1 if len(rows_nz) else 0
    bottom = rows_nz[-1] if len(rows_nz) else 0
    status = "WARNING: " + " ".join(flags) if flags else "[OK]"
    print(f"Frame {i+1:2d}: crop {cw_crop}x{ch_crop} -> scaled {new_w}x{new_h}, char_h={char_h}, bottom_y={bottom}, paste@({px},{py}) {status}")

# Step 5: Save individual PNGs
for i, frame in enumerate(processed):
    frame.save(OUT_DIR / f"attack-{i+1}.png", "PNG")
print(f"\nSaved 12 individual PNGs to {OUT_DIR}")

# Step 6: 4x3 transparent sheet
sheet = Image.new("RGBA", (CANVAS_W * COLS, CANVAS_H * ROWS), (0, 0, 0, 0))
for i, frame in enumerate(processed):
    r, c = divmod(i, COLS)
    sheet.paste(frame, (c * CANVAS_W, r * CANVAS_H), frame)
sheet.save(OUT_DIR / "sheet-transparent.png", "PNG")

# Step 7: Horizontal strip for README/design
strip = Image.new("RGBA", (CANVAS_W * 12, CANVAS_H), (0, 0, 0, 0))
for i, frame in enumerate(processed):
    strip.paste(frame, (i * CANVAS_W, 0), frame)
strip.save(DESIGN_DIR / "attack-sequence.png", "PNG")
print("Saved sheet-transparent.png & attack-sequence.png")

# Step 8: GIFs
def make_gif(frames, path, duration=85):
    rgb = []
    for f in frames:
        bg = Image.new("RGB", f.size, (255, 255, 255))
        bg.paste(f, mask=f.split()[3])
        rgb.append(bg)
    rgb[0].save(path, save_all=True, append_images=rgb[1:], loop=0, duration=duration)

make_gif(processed,       OUT_DIR / "animation.gif")
make_gif(processed[0:4],  OUT_DIR / "attack-hit1.gif")
make_gif(processed[4:8],  OUT_DIR / "attack-hit2.gif")
make_gif(processed[8:12], OUT_DIR / "attack-hit3.gif")
print("Saved animation.gif & attack-hit1~3.gif")
print("All done successfully!")
