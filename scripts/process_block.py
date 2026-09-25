#!/usr/bin/env python3
"""
Process Qingfeng Swordsman Block & Parry (招架/格挡) Animation Frames (8 frames)
Features:
- Directly derived from concept art '01-青锋剑客-动作设计.png' §3 招架 (PARRY).
- Clean text label removal from reference sheet P1.
- Precise magenta chroma-key (#FF00FF) with despill and alpha feathering.
- Uniform proportional scaling (standing height = 328px, matching Idle/Run/Attack/Dodge/Jump/HeavyThrust).
- Foot baseline aligned to Y=437 on 680x480 canvas (Pivot 0.5, 0.09, PPU 214).
- Exports individual PNGs, preview GIF, transparent sprite sheet, and design sequence.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import shutil

P1_SOURCE = Path(r"C:\Users\luyus\.gemini\antigravity\brain\000cfc7f-a167-4909-a0fc-768476b36049\qingfeng_block_p1_1790301990761.jpg")
P2_SOURCE = Path(r"C:\Users\luyus\.gemini\antigravity\brain\000cfc7f-a167-4909-a0fc-768476b36049\qingfeng_block_p2_1790302008756.jpg")

OUT_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\New Tuanjie Project\Assets\Sprites\Player\Block")
DESIGN_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列")
OUT_DIR.mkdir(parents=True, exist_ok=True)
DESIGN_DIR.mkdir(parents=True, exist_ok=True)

# Archive source sheets
shutil.copyfile(P1_SOURCE, DESIGN_DIR / "block-p1-source.png")
shutil.copyfile(P2_SOURCE, DESIGN_DIR / "block-p2-source.png")

CANVAS_W = 680
CANVAS_H = 480
TARGET_STAND_H = 328
RAW_STAND_H = 343.0  # Measured from Frame 8 standing height: 361 - 19 + 1 = 343
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

# Text masks for P1 quads to cleanly eliminate text labels
text_masks_p1 = [
    (98, 225),  # Quad 1
    (98, 310),  # Quad 2
    (60, 250),  # Quad 3
    (60, 250),  # Quad 4
]

cut_configs = [
    (img1, 0, 0, 688, 384, text_masks_p1[0], "B1: 沉腰拔势 (Drop & Raise)"),
    (img1, 688, 0, 1376, 384, text_masks_p1[1], "B2: 剑横胸前·弹反窗 (Cross Guard)"),
    (img1, 0, 384, 688, 768, text_masks_p1[2], "B3: 卸力抗震·火花迸发 (Parry Spark)"),
    (img1, 688, 384, 1376, 768, text_masks_p1[3], "B4: 坚实架势 (Solid Guard Stance)"),
    (img2, 0, 0, 688, 384, None, "B5: 凝神屏息 (Guarded Focus)"),
    (img2, 688, 0, 1376, 384, None, "B6: 劲力蓄势 (Defensive Ready)"),
    (img2, 0, 384, 688, 768, None, "B7: 翻腕卸劲 (Disengage & Wrist Turn)"),
    (img2, 688, 384, 1376, 768, None, "B8: 敛剑归正 (Neutral Stance Transition)"),
]

processed_frames = []

for idx, (img, x0, y0, x1, y1, text_mask, desc) in enumerate(cut_configs):
    cell = img.crop((x0, y0, x1, y1))
    
    # Fill text area with pure magenta if mask is specified
    if text_mask is not None:
        my, mx = text_mask
        cell_arr = np.array(cell)
        cell_arr[:my, :mx, :] = [255, 0, 255]
        cell = Image.fromarray(cell_arr)
        
    cleaned = clean_magenta(cell)
    cropped, (cx0, cy0, cx1, cy1) = tight_crop(cleaned)
    
    # Scale uniformly
    nw = int(round(cropped.width * UNIFORM_SCALE))
    nh = int(round(cropped.height * UNIFORM_SCALE))
    scaled = cropped.resize((nw, nh), Image.LANCZOS)
    
    # Measure boot sole in unscaled cropped image to align ground precisely
    c_arr = np.array(cropped)
    # Check rows from bottom up for dark boot pixels
    boot_local_y = cropped.height - 1
    for r in range(cropped.height - 1, max(0, cropped.height - 40), -1):
        row = c_arr[r, :, :]
        # Check alpha > 120 and dark boot color
        alpha_row = row[:, 3]
        dark = (row[:, 0] < 90) & (row[:, 1] < 90) & (row[:, 2] < 90) & (alpha_row > 120)
        if dark.sum() > 4:
            boot_local_y = r
            break
            
    scaled_boot_y = int(round(boot_local_y * UNIFORM_SCALE))
    py = FOOT_Y - scaled_boot_y
    
    # Horizontal placement: align center of character feet to CENTER_X
    cell_np = np.array(cell)
    sub_raw = cell_np[330:360, :]
    r_raw, g_raw, b_raw = sub_raw[..., 0], sub_raw[..., 1], sub_raw[..., 2]
    dist_raw = np.sqrt((r_raw.astype(float)-255)**2 + g_raw.astype(float)**2 + (b_raw.astype(float)-255)**2)
    boots_mask = (r_raw < 85) & (g_raw < 85) & (b_raw < 85) & (dist_raw > 50)
    cols_boots = np.where(boots_mask.any(axis=0))[0]
    if len(cols_boots):
        raw_foot_center = (cols_boots[0] + cols_boots[-1]) / 2.0
    else:
        raw_foot_center = 335.0
        
    local_foot_x = raw_foot_center - cx0
    scaled_foot_x = local_foot_x * UNIFORM_SCALE
    px = int(round(CENTER_X - scaled_foot_x))
    
    # Clamp
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

# 1. Save individual frame PNGs to Unity Block directory
for i, frame in enumerate(processed_frames):
    out_path = OUT_DIR / f"block-{i+1}.png"
    frame.save(out_path, "PNG")
print(f"\nSaved 8 individual frames to {OUT_DIR}")

# 2. Save preview animation GIF to Unity and Design directories (85ms/frame)
gif_path_unity = OUT_DIR / "animation.gif"
gif_path_design = DESIGN_DIR / "block-animation.gif"
processed_frames[0].save(
    gif_path_unity,
    save_all=True,
    append_images=processed_frames[1:],
    duration=85,
    loop=0,
    disposal=2
)
shutil.copyfile(gif_path_unity, gif_path_design)
print(f"Saved block GIF -> {gif_path_unity}")

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
seq_path = DESIGN_DIR / "block-sequence.png"
seq.save(seq_path, "PNG")
print(f"Saved horizontal sequence filmstrip -> {seq_path}")
print("\nAll block frame assets generated successfully!")
