#!/usr/bin/env python3
"""
Process attack sheet v3 with bold, luminous cyan-white ink sword FX (16:9 wide).
"""
from pathlib import Path
from PIL import Image
import numpy as np

SOURCE     = Path(r"C:\Users\luyus\.gemini\antigravity\brain\d81eb2c1-d0d1-4391-ab33-851bd360ff28\qingfeng_attack_fx_v3_1790164744609.jpg")
OUT_DIR    = Path(r"C:\Users\luyus\Desktop\刀影江湖\New Tuanjie Project\Assets\Sprites\Player\Attack")
DESIGN_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列")
OUT_DIR.mkdir(parents=True, exist_ok=True)
DESIGN_DIR.mkdir(parents=True, exist_ok=True)

import shutil
shutil.copyfile(SOURCE, DESIGN_DIR / "attack-fx-source.png")

COLS, ROWS   = 4, 3
CANVAS_W     = 680
CANVAS_H     = 480
TARGET_H     = 328
FOOT_Y       = 437
CENTER_X     = 340

src = Image.open(SOURCE).convert("RGBA")
W, H = src.size
rh = H // 3

# Adaptive boundary cuts per row: preserves full extended thrusts and shockwaves
cuts_per_row = [
    [0, 340, 710, 1075, W],   # Row 0: F1 starburst, F2 spiral cone, F3 piercing spearhead, F4 aura
    [0, 344, 688, 1032, W],   # Row 1: F5 edge, F6 slash arc, F7 wide crescent, F8 aura
    [0, 350, 695, 1100, W]    # Row 2: F9 lightning aura, F10 cleave, F11 shockwave, F12 recovery
]

def clean_magenta(cell, thresh=35, feather=40):
    arr = np.array(cell, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    dist = np.sqrt((r - 255.0)**2 + g**2 + (b - 255.0)**2)
    spill = np.maximum(0, np.minimum(r - g, b - g))
    r_clean = np.clip(r - 0.95 * spill, 0, 255)
    b_clean = np.clip(b - 0.95 * spill, 0, 255)
    alpha = np.clip((dist - thresh) / feather, 0, 1) * 255
    out = np.dstack([r_clean, g, b_clean, alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")

def tight_crop(rgba_img):
    arr = np.array(rgba_img)
    alpha = arr[..., 3]
    rows = np.where(alpha.max(axis=1) > 25)[0]
    cols = np.where(alpha.max(axis=0) > 25)[0]
    if len(rows) == 0 or len(cols) == 0:
        return rgba_img
    return rgba_img.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))

UNIFORM_SCALE = TARGET_H / 181.0
print(f"Uniform scale = {UNIFORM_SCALE:.4f}")

processed = []
for r in range(3):
    y0 = r * rh
    y1 = min((r + 1) * rh, H - 2 if r == 2 else (r + 1) * rh)
    cuts = cuts_per_row[r]
    for c in range(4):
        idx = r * 4 + c + 1
        x0 = cuts[c]
        x1 = min(cuts[c + 1], W - 2 if c == 3 else cuts[c + 1])
        cell = src.crop((x0, y0, x1, y1))
        clean = clean_magenta(cell)
        crop = tight_crop(clean)
        
        nw = int(round(crop.size[0] * UNIFORM_SCALE))
        nh = int(round(crop.size[1] * UNIFORM_SCALE))
        scaled = crop.resize((nw, nh), Image.LANCZOS)
        
        s_arr = np.array(scaled)
        s_alpha = s_arr[..., 3].astype(float)
        bot = s_alpha[max(0, nh - 25):nh, :]
        fx = float((bot * np.arange(nw)).sum() / bot.sum()) if bot.sum() > 1 else nw / 2.0
        
        px = int(round(CENTER_X - fx))
        py = int(round(FOOT_Y - nh))
        
        if px + nw > CANVAS_W - 5:
            px = CANVAS_W - 5 - nw
        if px < 5:
            px = 5
        if py < 5:
            py = 5
            
        canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        canvas.paste(scaled, (px, py), scaled)
        processed.append(canvas)
        print(f"Frame {idx:2d}: crop {crop.size[0]}x{crop.size[1]} -> scaled {nw}x{nh}, px={px}, right={px+nw}, py={py}, bottom={py+nh} [OK]")

for i, frame in enumerate(processed):
    frame.save(OUT_DIR / f"attack-{i+1}.png", "PNG")
print(f"\nSaved 12 individual PNGs -> {OUT_DIR}")

sheet = Image.new("RGBA", (CANVAS_W * COLS, CANVAS_H * ROWS), (0, 0, 0, 0))
for i, frame in enumerate(processed):
    r, c = divmod(i, COLS)
    sheet.paste(frame, (c * CANVAS_W, r * CANVAS_H), frame)
sheet.save(OUT_DIR / "sheet-transparent.png", "PNG")

strip = Image.new("RGBA", (CANVAS_W * 12, CANVAS_H), (0, 0, 0, 0))
for i, frame in enumerate(processed):
    strip.paste(frame, (i * CANVAS_W, 0), frame)
strip.save(DESIGN_DIR / "attack-sequence.png", "PNG")
print("Saved sheet-transparent.png & attack-sequence.png")

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
print("All finished successfully!")
