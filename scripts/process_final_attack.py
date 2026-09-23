#!/usr/bin/env python3
"""Process final bowed attack sheet (magenta bg, 4x3 grid, 12 frames)."""
from pathlib import Path
from PIL import Image
import numpy as np

SOURCE     = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列\attack-final-source.png")
OUT_DIR    = Path(r"C:\Users\luyus\Desktop\刀影江湖\New Tuanjie Project\Assets\Sprites\Player\Attack")
DESIGN_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列")
OUT_DIR.mkdir(parents=True, exist_ok=True)

COLS, ROWS   = 4, 3
CANVAS_W     = 680
CANVAS_H     = 480
TARGET_H     = 328
FOOT_Y       = 437
CENTER_X     = 340

# Split
src = Image.open(SOURCE).convert("RGBA")
W, H = src.size
fw, fh = W // COLS, H // ROWS
print(f"Source {W}x{H}, cell {fw}x{fh}")

raw_frames = [src.crop((c*fw, r*fh, (c+1)*fw, (r+1)*fh))
              for r in range(ROWS) for c in range(COLS)]

# Remove magenta
def remove_magenta(img, threshold=35, feather=45):
    arr = np.array(img, dtype=np.float32)
    r, g, b = arr[...,0], arr[...,1], arr[...,2]
    dist = np.sqrt((r-255)**2 + g**2 + (b-255)**2)
    # Despill
    spill = np.maximum(0, np.minimum(r-g, b-g))
    arr[...,0] = np.clip(r - 0.9*spill, 0, 255)
    arr[...,2] = np.clip(b - 0.9*spill, 0, 255)
    raw_a = np.clip((dist - threshold) / feather, 0, 1) * 255
    out = arr.astype(np.uint8)
    out[...,3] = raw_a.astype(np.uint8)
    return Image.fromarray(out, "RGBA")

def tight_crop(img):
    arr = np.array(img)
    alpha = arr[...,3]
    rows = np.where(alpha.max(axis=1) > 20)[0]
    cols = np.where(alpha.max(axis=0) > 20)[0]
    if len(rows)==0 or len(cols)==0:
        return img
    return img.crop((cols[0], rows[0], cols[-1]+1, rows[-1]+1))

def foot_centroid_x(img, foot_rows=15):
    arr = np.array(img)
    h = arr.shape[0]
    bottom = arr[max(0,h-foot_rows):h]
    alpha = bottom[...,3].astype(np.float32)
    total = alpha.sum()
    if total < 1:
        return img.size[0]/2.0
    xs = np.arange(img.size[0], dtype=np.float32)
    return float((alpha * xs[np.newaxis,:]).sum() / total)

processed = []
for i, raw in enumerate(raw_frames):
    clean  = remove_magenta(raw)
    crop   = tight_crop(clean)
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

    # QC edge check
    arr = np.array(canvas)
    alpha = arr[...,3]
    flags = []
    if alpha[:,0].max()>20:          flags.append("EDGE_L")
    if alpha[:,CANVAS_W-1].max()>20: flags.append("EDGE_R")
    if alpha[0,:].max()>20:          flags.append("EDGE_T")
    if alpha[CANVAS_H-1,:].max()>20: flags.append("EDGE_B")
    rows_nz = np.where(alpha.max(axis=1)>20)[0]
    char_h  = rows_nz[-1]-rows_nz[0]+1 if len(rows_nz) else 0
    warn = " ⚠ "+" ".join(flags) if flags else ""
    print(f"Frame {i+1:2d}: crop={cw}x{ch} scale={scale:.3f} → char_h={char_h} bottom={rows_nz[-1] if len(rows_nz) else '?'}{warn}")

# Save PNGs
for i, frame in enumerate(processed):
    frame.save(OUT_DIR / f"attack-{i+1}.png", "PNG")
print(f"\nSaved 12 PNGs → {OUT_DIR}")

# Sheet 4x3
sheet = Image.new("RGBA", (CANVAS_W*COLS, CANVAS_H*ROWS), (0,0,0,0))
for i, frame in enumerate(processed):
    r, c = divmod(i, COLS)
    sheet.paste(frame, (c*CANVAS_W, r*CANVAS_H), frame)
sheet.save(OUT_DIR / "sheet-transparent.png", "PNG")

# Horizontal strip for README
strip = Image.new("RGBA", (CANVAS_W*12, CANVAS_H), (0,0,0,0))
for i, frame in enumerate(processed):
    strip.paste(frame, (i*CANVAS_W, 0), frame)
strip.save(DESIGN_DIR / "attack-sequence.png", "PNG")
print("Saved sheet + strip")

# GIFs
def make_gif(frames, path, duration=85):
    rgb = []
    for f in frames:
        bg = Image.new("RGB", f.size, (255,255,255))
        bg.paste(f, mask=f.split()[3])
        rgb.append(bg)
    rgb[0].save(path, save_all=True, append_images=rgb[1:], loop=0, duration=duration)

make_gif(processed,       OUT_DIR/"animation.gif")
make_gif(processed[0:4],  OUT_DIR/"attack-hit1.gif")
make_gif(processed[4:8],  OUT_DIR/"attack-hit2.gif")
make_gif(processed[8:12], OUT_DIR/"attack-hit3.gif")
print("Saved GIFs\nDone!")
