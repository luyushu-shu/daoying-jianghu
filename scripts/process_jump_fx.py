#!/usr/bin/env python3
"""
Process Qingfeng Swordsman Jump Animation Frames (8 frames)
Features:
- Martial arts light-body jump (轻功凌空纵跃) with cyan-white energy trails and ink afterimages.
- Precise magenta chroma-key (#FF00FF) with despill and alpha feathering.
- Uniform proportional scaling (standing height = 328px, matching Idle/Run/Attack/Dodge).
- Foot baseline aligned to Y=437 on 680x480 canvas (Pivot 0.5, 0.09, PPU 214).
- Seamless hot reload in Unity (maintaining existing .meta files and GUIDs).
- Exports individual PNGs, preview GIF, transparent sprite sheet, and design sequence.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import shutil

P1_SOURCE = Path(r"C:\Users\luyus\.gemini\antigravity\brain\000cfc7f-a167-4909-a0fc-768476b36049\qingfeng_jump_p1_1790296368182.jpg")
P2_SOURCE = Path(r"C:\Users\luyus\.gemini\antigravity\brain\000cfc7f-a167-4909-a0fc-768476b36049\qingfeng_jump_p2_1790296409458.jpg")

OUT_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\New Tuanjie Project\Assets\Sprites\Player\Jump")
DESIGN_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列")
OUT_DIR.mkdir(parents=True, exist_ok=True)
DESIGN_DIR.mkdir(parents=True, exist_ok=True)

# Copy source sheets to design directory for archiving
shutil.copyfile(P1_SOURCE, DESIGN_DIR / "jump-p1-source.png")
shutil.copyfile(P2_SOURCE, DESIGN_DIR / "jump-p2-source.png")

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
    # Clear outer 3px edge to avoid JPEG compression border ringing
    alpha[:3, :] = 0; alpha[-3:, :] = 0; alpha[:, :3] = 0; alpha[:, -3:] = 0
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

# Quadrant configurations
# (source_img, x0, y0, x1, y1, desc)
cut_configs = [
    (img1, 0, 0, 688, 384, "F1: 起跳蓄势 (Jump Squat)"),
    (img1, 688, 0, 1376, 384, "F2: 踏空离地 (Takeoff Launch)"),
    (img1, 0, 384, 688, 768, "F3: 穿云拔升 (Airborne Rise)"),
    (img1, 688, 384, 1376, 768, "F4: 滞空极点 (Apex Float)"),
    (img2, 0, 0, 688, 384, "F5: 俯身寻地 (Initial Fall)"),
    (img2, 688, 0, 1376, 384, "F6: 破风急坠 (Fast Fall Plunge)"),
    (img2, 0, 384, 688, 768, "F7: 前掌触地 (Touchdown Contact)"),
    (img2, 688, 384, 1376, 768, "F8: 屈膝收式 (Cushion & Recovery)"),
]

processed_frames = []

for idx, (img, x0, y0, x1, y1, desc) in enumerate(cut_configs):
    cell = img.crop((x0, y0, x1, y1))
    cleaned = clean_magenta(cell)
    cropped, (cx0, cy0, cx1, cy1) = tight_crop(cleaned)
    
    # Scale uniformly
    nw = int(round(cropped.width * UNIFORM_SCALE))
    nh = int(round(cropped.height * UNIFORM_SCALE))
    scaled = cropped.resize((nw, nh), Image.LANCZOS)
    
    # Vertical placement: ground line in cell is at Y=353
    local_ground_y = 353 - cy0
    scaled_ground_y = int(round(local_ground_y * UNIFORM_SCALE))
    py = FOOT_Y - scaled_ground_y
    
    # Horizontal placement: torso center aligned to CENTER_X
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

# 1. Save individual frame PNGs to Unity Jump directory
for i, frame in enumerate(processed_frames):
    out_path = OUT_DIR / f"jump-{i+1}.png"
    frame.save(out_path, "PNG")
print(f"\nSaved 8 individual frames to {OUT_DIR}")

# 2. Save preview animation GIF to Unity and Design directories (90ms/frame)
gif_path_unity = OUT_DIR / "animation.gif"
gif_path_design = DESIGN_DIR / "jump-animation.gif"
processed_frames[0].save(
    gif_path_unity,
    save_all=True,
    append_images=processed_frames[1:],
    duration=90,
    loop=0,
    disposal=2
)
shutil.copyfile(gif_path_unity, gif_path_design)
print(f"Saved jump GIF -> {gif_path_unity}")

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
seq_path = DESIGN_DIR / "jump-sequence.png"
seq.save(seq_path, "PNG")
print(f"Saved horizontal sequence filmstrip -> {seq_path}")

print("\nAll jump assets successfully processed and saved!")
