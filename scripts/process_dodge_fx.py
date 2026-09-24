#!/usr/bin/env python3
"""
Process Qingfeng Swordsman Redesigned Dodge Animation Frames (8 frames)
Features:
- High-speed phantom dash (极速残影瞬步) with cyan-white energy trails and ink afterimages.
- Precise magenta chroma-key (#FF00FF) with despill and alpha feathering.
- Uniform proportional scaling (standing height = 328px, matching Idle/Run/Attack).
- Foot baseline locked to Y=437 on 680x480 canvas (Pivot 0.5, 0.09, PPU 214).
- Seamless hot reload in Unity (maintaining existing .meta files and GUIDs).
- Exports individual PNGs, preview GIF, transparent sprite sheet, and design sequence.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import shutil

P1_SOURCE = Path(r"C:\Users\luyus\.gemini\antigravity\brain\d81eb2c1-d0d1-4391-ab33-851bd360ff28\qingfeng_dodge_p1_2x2_1790224770570.jpg")
P2_SOURCE = Path(r"C:\Users\luyus\.gemini\antigravity\brain\d81eb2c1-d0d1-4391-ab33-851bd360ff28\qingfeng_dodge_p2_2x2_1790224821301.jpg")

OUT_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\New Tuanjie Project\Assets\Sprites\Player\Dodge")
DESIGN_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列")
OUT_DIR.mkdir(parents=True, exist_ok=True)
DESIGN_DIR.mkdir(parents=True, exist_ok=True)

# Copy source sheets to design directory for archiving
shutil.copyfile(P1_SOURCE, DESIGN_DIR / "dodge-p1-source.png")
shutil.copyfile(P2_SOURCE, DESIGN_DIR / "dodge-p2-source.png")

CANVAS_W = 680
CANVAS_H = 480
TARGET_STAND_H = 328
RAW_STAND_H = 322.0
UNIFORM_SCALE = TARGET_STAND_H / RAW_STAND_H
FOOT_Y = 437
CENTER_X = 340

print(f"Uniform Scale Ratio: {UNIFORM_SCALE:.5f} (target {TARGET_STAND_H}px / raw {RAW_STAND_H}px)")

def clean_magenta(cell, thresh=45, feather=35):
    """Clean solid magenta (#FF00FF) background with despill to protect cyan-white and ink effects."""
    arr = np.array(cell, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    dist = np.sqrt((r - 255.0)**2 + g**2 + (b - 255.0)**2)
    
    # Magenta hue detector: both r and b high, g very low
    mag_tint = (r > 90) & (b > 90) & (g < 60) & (abs(r - b) < 60)
    
    # Despill: suppress magenta fringe reflected onto sprite edges
    spill = np.maximum(0, np.minimum(r - g, b - g))
    r_clean = np.clip(r - 0.95 * spill, 0, 255)
    b_clean = np.clip(b - 0.95 * spill, 0, 255)
    
    alpha = np.clip((dist - thresh) / feather, 0, 1) * 255
    # Completely zero out alpha on magenta background artifacts
    alpha[mag_tint & (dist < 120)] = 0
    out = np.dstack([r_clean, g, b_clean, alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")

def tight_crop(rgba_img):
    """Crop strictly around non-transparent content."""
    arr = np.array(rgba_img)
    alpha = arr[..., 3]
    rows = np.where(alpha.max(axis=1) > 20)[0]
    cols = np.where(alpha.max(axis=0) > 20)[0]
    if len(rows) == 0 or len(cols) == 0:
        return rgba_img, (0, 0, rgba_img.width, rgba_img.height)
    return rgba_img.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1)), (int(cols[0]), int(rows[0]), int(cols[-1] + 1), int(rows[-1] + 1))

img1 = Image.open(P1_SOURCE)
img2 = Image.open(P2_SOURCE)

# Quadrant boundaries tailored to fully preserve scabbards, air wakes, sparks, and afterimages
# (source_img, row, col, x0, y0, x1, y1, desc)
cut_configs = [
    (img1, 0, 0, 0, 0, 650, 384, "F1: 起式下潜蓄势 (Startup crouch)"),
    (img1, 0, 1, 650, 0, 1376, 384, "F2: 破空暴冲弹射 (Dash launch)"),
    (img1, 1, 0, 0, 384, 688, 768, "F3: 极速残影瞬步 (Phantom dash peak)"),
    (img1, 1, 1, 688, 384, 1376, 768, "F4: 疾速穿梭延伸 (Gliding stretch)"),
    (img2, 0, 0, 0, 0, 688, 384, "F5: 触地低姿滑行 (Ground slide)"),
    (img2, 0, 1, 688, 0, 1376, 384, "F6: 侧身急刹减速 (Braking skid)"),
    (img2, 1, 0, 0, 384, 688, 768, "F7: 顺势起身回升 (Recovery rise)"),
    (img2, 1, 1, 688, 384, 1376, 768, "F8: 凝神回正收招 (Ready stance)"),
]

processed_frames = []

for idx, (img, r, c, x0, y0, x1, y1, desc) in enumerate(cut_configs):
    cell = img.crop((x0, y0, x1, y1))
    cleaned = clean_magenta(cell)
    cropped, (cx0, cy0, cx1, cy1) = tight_crop(cleaned)
    
    # Scale uniformly
    nw = int(round(cropped.width * UNIFORM_SCALE))
    nh = int(round(cropped.height * UNIFORM_SCALE))
    scaled = cropped.resize((nw, nh), Image.LANCZOS)
    
    # Calculate vertical ground position relative to cell
    ground_in_cell = 353 if y0 == 0 else (353 + 384)
    local_ground_y = (ground_in_cell - y0) - cy0
    scaled_ground_y = int(round(local_ground_y * UNIFORM_SCALE))
    py = FOOT_Y - scaled_ground_y
    
    # Calculate horizontal placement (torso center of mass aligned to center X)
    s_arr = np.array(scaled)
    s_alpha = s_arr[..., 3].astype(float)
    mid_h = nh // 2
    torso_slice = s_alpha[max(0, mid_h - 40):min(nh, mid_h + 40), :]
    if torso_slice.sum() > 10:
        torso_x = float((torso_slice * np.arange(nw)).sum() / torso_slice.sum())
    else:
        torso_x = nw / 2.0
    px = int(round(CENTER_X - torso_x))
    
    # Safety clamp to guarantee no canvas boundary truncation
    if px + nw > CANVAS_W - 5:
        px = CANVAS_W - 5 - nw
    if px < 5:
        px = 5
    if py + nh > CANVAS_H - 2:
        py = CANVAS_H - 2 - nh
    if py < 5:
        py = 5
        
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.paste(scaled, (px, py), scaled)
    processed_frames.append(canvas)
    
    print(f"[{idx+1}/8] {desc} -> scaled {nw}x{nh}, pos=({px}, {py}), right={px+nw}, bot={py+nh} [OK]")

# 1. Save individual frame PNGs to Unity Dodge directory
for i, frame in enumerate(processed_frames):
    out_path = OUT_DIR / f"dodge-{i+1}.png"
    frame.save(out_path, "PNG")
print(f"\nSaved 8 individual frames to {OUT_DIR}")

# 2. Save preview animation GIF to Unity and Design directories (75ms/frame = 13.33fps)
gif_path_unity = OUT_DIR / "animation.gif"
gif_path_design = DESIGN_DIR / "dodge-animation.gif"
processed_frames[0].save(
    gif_path_unity,
    save_all=True,
    append_images=processed_frames[1:],
    duration=75,
    loop=0,
    disposal=2
)
shutil.copyfile(gif_path_unity, gif_path_design)
print(f"Saved dodge GIF -> {gif_path_unity}")

# 3. Save 4x2 transparent sprite sheet (2720x960) to Unity directory
sheet_w = CANVAS_W * 4
sheet_h = CANVAS_H * 2
sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
for i, frame in enumerate(processed_frames):
    sr = i // 4
    sc = i % 4
    sheet.paste(frame, (sc * CANVAS_W, sr * CANVAS_H), frame)
sheet_path = OUT_DIR / "sheet-transparent.png"
sheet.save(sheet_path, "PNG")
print(f"Saved transparent sheet -> {sheet_path}")

# 4. Save horizontal sequence filmstrip (8x1, 5440x480) to Design directory
seq_w = CANVAS_W * 8
seq_h = CANVAS_H
seq = Image.new("RGBA", (seq_w, seq_h), (0, 0, 0, 0))
for i, frame in enumerate(processed_frames):
    seq.paste(frame, (i * CANVAS_W, 0), frame)
seq_path = DESIGN_DIR / "dodge-sequence.png"
seq.save(seq_path, "PNG")
print(f"Saved horizontal sequence filmstrip -> {seq_path}")

print("\nAll dodge assets successfully processed and updated!")
