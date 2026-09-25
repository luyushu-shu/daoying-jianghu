#!/usr/bin/env python3
"""
Process Qingfeng Swordsman 3-Tier Block & Parry Animations:
1. 没挡刀（纯姿势）- Guard Stance: Pure clean posture, NO sparks or hits.
2. 普通格挡成功（微弱亮光）- Normal Block Hit: Subtle, delicate cyan-white glint and small sparkles on sword blade.
3. 完美格挡成功（暴烈大特效）- Perfect Parry: Explosive golden-white radiating starlight burst + outward ink-wash sparks!
"""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import shutil

P1_SOURCE = Path(r"C:\Users\luyus\.gemini\antigravity\brain\000cfc7f-a167-4909-a0fc-768476b36049\qingfeng_block_p1_1790301990761.jpg")
P2_SOURCE = Path(r"C:\Users\luyus\.gemini\antigravity\brain\000cfc7f-a167-4909-a0fc-768476b36049\qingfeng_block_p2_1790302008756.jpg")

BASE_OUT_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\New Tuanjie Project\Assets\Sprites\Player\Block")
GUARD_DIR = BASE_OUT_DIR / "Guard"
HIT_DIR = BASE_OUT_DIR / "Hit"
PARRY_DIR = BASE_OUT_DIR / "Parry"
DESIGN_DIR = Path(r"C:\Users\luyus\Desktop\刀影江湖\设计\青锋帧序列")

for d in [BASE_OUT_DIR, GUARD_DIR, HIT_DIR, PARRY_DIR, DESIGN_DIR]:
    d.mkdir(parents=True, exist_ok=True)

CANVAS_W = 680
CANVAS_H = 480
TARGET_STAND_H = 328
RAW_STAND_H = 343.0
UNIFORM_SCALE = TARGET_STAND_H / RAW_STAND_H
FOOT_Y = 437
CENTER_X = 340

def clean_magenta(cell, thresh=45, feather=35):
    arr = np.array(cell, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    dist = np.sqrt((r - 255.0)**2 + g**2 + (b - 255.0)**2)
    mag_tint = (r > 90) & (b > 90) & (g < 60) & (abs(r - b) < 60)
    spill = np.maximum(0, np.minimum(r - g, b - g))
    r_clean = np.clip(r - 0.95 * spill, 0, 255)
    b_clean = np.clip(b - 0.95 * spill, 0, 255)
    alpha = np.clip((dist - thresh) / feather, 0, 1) * 255
    alpha[mag_tint & (dist < 120)] = 0
    alpha[:3, :] = 0; alpha[-3:, :] = 0; alpha[:, :3] = 0; alpha[:, -3:] = 0
    out = np.dstack([r_clean, g, b_clean, alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")

def tight_crop(rgba_img):
    arr = np.array(rgba_img)
    alpha = arr[..., 3]
    rows = np.where(alpha.max(axis=1) > 20)[0]
    cols = np.where(alpha.max(axis=0) > 20)[0]
    if len(rows) == 0 or len(cols) == 0:
        return rgba_img, (0, 0, rgba_img.width, rgba_img.height)
    return rgba_img.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1)), (int(cols[0]), int(rows[0]), int(cols[-1] + 1), int(rows[-1] + 1))

def process_single_frame(img, x0, y0, x1, y1, text_mask):
    cell = img.crop((x0, y0, x1, y1))
    if text_mask is not None:
        cell_arr = np.array(cell)
        if isinstance(text_mask, list):
            for my, mx in text_mask:
                cell_arr[:my, :mx, :] = [255, 0, 255]
        else:
            my, mx = text_mask
            cell_arr[:my, :mx, :] = [255, 0, 255]
        cell = Image.fromarray(cell_arr)
        
    cleaned = clean_magenta(cell)
    cropped, (cx0, cy0, cx1, cy1) = tight_crop(cleaned)
    nw = int(round(cropped.width * UNIFORM_SCALE))
    nh = int(round(cropped.height * UNIFORM_SCALE))
    scaled = cropped.resize((nw, nh), Image.LANCZOS)
    
    # Ground sole alignment
    c_arr = np.array(cropped)
    boot_local_y = cropped.height - 1
    for r in range(cropped.height - 1, max(0, cropped.height - 40), -1):
        row = c_arr[r, :, :]
        alpha_row = row[:, 3]
        dark = (row[:, 0] < 90) & (row[:, 1] < 90) & (row[:, 2] < 90) & (alpha_row > 120)
        if dark.sum() > 4:
            boot_local_y = r
            break
            
    scaled_boot_y = int(round(boot_local_y * UNIFORM_SCALE))
    py = FOOT_Y - scaled_boot_y
    
    # Foot center X alignment
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
    
    if px + nw > CANVAS_W - 5: px = CANVAS_W - 5 - nw
    if px < 5: px = 5
    if py + nh > CANVAS_H - 2: py = CANVAS_H - 2 - nh
    if py < 5: py = 5
    
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.paste(scaled, (px, py), scaled)
    return canvas

img1 = Image.open(P1_SOURCE)
img2 = Image.open(P2_SOURCE)

# Extract raw base frames
f_b1 = process_single_frame(img1, 0, 0, 688, 384, (98, 225))     # 沉腰拔势
f_b2 = process_single_frame(img1, 688, 0, 1376, 384, [(60, 430), (98, 310)])   # 剑横胸前
f_b3_spark = process_single_frame(img1, 0, 384, 688, 768, (65, 560)) # 完美格挡大火花星芒
f_b4_guard = process_single_frame(img1, 688, 384, 1376, 768, (60, 220)) # 格挡坚实架势（纯姿态）
f_b5 = process_single_frame(img2, 0, 0, 688, 384, None)           # 凝神屏息
f_b6 = process_single_frame(img2, 688, 0, 1376, 384, None)         # 劲力蓄势
f_b7 = process_single_frame(img2, 0, 384, 688, 768, None)         # 翻腕卸劲
f_b8 = process_single_frame(img2, 688, 384, 1376, 768, None)         # 敛剑归正

print("Raw base frames processed successfully.")

# ==============================================================================
# 1. 没挡刀（纯姿势，Guard Stance）: 7 帧纯身法，绝无受击火花
# ==============================================================================
guard_frames = [f_b1, f_b2, f_b4_guard, f_b5, f_b6, f_b7, f_b8]
for i, f in enumerate(guard_frames):
    f.save(GUARD_DIR / f"guard-{i+1}.png", "PNG")

guard_gif = GUARD_DIR / "animation.gif"
guard_frames[0].save(
    guard_gif,
    save_all=True,
    append_images=guard_frames[1:],
    duration=90,
    loop=0,
    disposal=2
)
shutil.copyfile(guard_gif, DESIGN_DIR / "block-guard-animation.gif")
print("Saved 1. 没挡刀（纯姿势 Guard） -> 7 帧 PNG & GIF")

# ==============================================================================
# 2. 普通格挡成功（微弱亮光，Normal Block Hit）: 4 帧受击微震 + 刃口微弱亮光
# ==============================================================================
# Helper to create subtle glint overlay
def make_subtle_glint_frame(base_img, offset_x=0, glint_scale=1.0, spark_alpha=200):
    base = base_img.copy()
    if offset_x != 0:
        shifted = Image.new("RGBA", base.size, (0, 0, 0, 0))
        shifted.paste(base, (offset_x, 0))
        base = shifted
        
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Sword blade impact contact point (adjusted with offset)
    cx, cy = 425 + offset_x, 205
    
    # Soft circular cyan glow
    r_max = int(16 * glint_scale)
    for r in range(r_max, 0, -2):
        alpha = int(40 * (1.0 - r / float(r_max))**1.5)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(130, 240, 255, alpha))
        
    # Delicate sharp 4-point cross glint
    ray_l = int(22 * glint_scale)
    ray_w = 2
    draw.polygon([(cx - ray_l, cy), (cx, cy - ray_w), (cx + ray_l, cy), (cx, cy + ray_w)], fill=(225, 255, 255, spark_alpha))
    draw.polygon([(cx, cy - ray_l), (cx - ray_w, cy), (cx, cy + ray_l), (cx + ray_w, cy)], fill=(225, 255, 255, spark_alpha))
    
    # 45-degree smaller rays
    diag_l = int(8 * glint_scale)
    draw.polygon([(cx - diag_l, cy - diag_l), (cx + diag_l, cy + diag_l), (cx + diag_l - 1, cy + diag_l), (cx - diag_l + 1, cy - diag_l)], fill=(180, 240, 255, int(spark_alpha * 0.7)))
    draw.polygon([(cx - diag_l, cy + diag_l), (cx + diag_l, cy - diag_l), (cx + diag_l - 1, cy - diag_l), (cx - diag_l + 1, cy + diag_l)], fill=(180, 240, 255, int(spark_alpha * 0.7)))
    
    # Crisp white center core
    c_r = max(1, int(3 * glint_scale))
    draw.ellipse((cx - c_r, cy - c_r, cx + c_r, cy + c_r), fill=(255, 255, 255, spark_alpha))
    
    # 3-4 tiny sparks
    sparks = [
        (cx + int(11 * glint_scale), cy - int(9 * glint_scale), 1.2),
        (cx - int(13 * glint_scale), cy - int(7 * glint_scale), 1.0),
        (cx + int(15 * glint_scale), cy + int(11 * glint_scale), 1.0),
        (cx - int(9 * glint_scale), cy + int(13 * glint_scale), 1.2),
    ]
    for sx, sy, sr in sparks:
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(200, 250, 255, int(spark_alpha * 0.8)))
        
    return Image.alpha_composite(base, overlay)

# Hit 1: Contact moment (sharp subtle glint on blade)
hit_1 = make_subtle_glint_frame(f_b4_guard, offset_x=0, glint_scale=1.1, spark_alpha=230)
# Hit 2: Impact recoil (absorbed slightly back 3px, glint fading into dispersing sparkles)
hit_2 = make_subtle_glint_frame(f_b4_guard, offset_x=-3, glint_scale=0.75, spark_alpha=150)
# Hit 3: Bracing reset (recovering forward 1px, faint spark embers disappearing)
hit_3 = make_subtle_glint_frame(f_b4_guard, offset_x=-1, glint_scale=0.35, spark_alpha=70)
# Hit 4: Settled back into firm guard (no glint, rock steady)
hit_4 = f_b4_guard.copy()

hit_frames = [hit_1, hit_2, hit_3, hit_4]
for i, f in enumerate(hit_frames):
    f.save(HIT_DIR / f"hit-{i+1}.png", "PNG")

hit_gif = HIT_DIR / "animation.gif"
hit_frames[0].save(
    hit_gif,
    save_all=True,
    append_images=hit_frames[1:],
    duration=75,
    loop=0,
    disposal=2
)
shutil.copyfile(hit_gif, DESIGN_DIR / "block-hit-animation.gif")
print("Saved 2. 普通格挡成功（微弱亮光 Hit） -> 4 帧 PNG & GIF")

# ==============================================================================
# 3. 完美格挡成功（暴烈大特效 Parry Success）: 6 帧华丽弹反星芒与墨浪迸发
# ==============================================================================
parry_frames = [f_b3_spark, f_b3_spark, f_b4_guard, f_b6, f_b7, f_b8]
for i, f in enumerate(parry_frames):
    f.save(PARRY_DIR / f"parry-{i+1}.png", "PNG")

parry_gif = PARRY_DIR / "animation.gif"
parry_frames[0].save(
    parry_gif,
    save_all=True,
    append_images=parry_frames[1:],
    duration=85,
    loop=0,
    disposal=2
)
shutil.copyfile(parry_gif, DESIGN_DIR / "block-parry-animation.gif")
print("Saved 3. 完美格挡成功（暴烈大特效 Parry） -> 6 帧 PNG & GIF")

# Also copy top-level animation.gif to be the clean guard animation
shutil.copyfile(guard_gif, BASE_OUT_DIR / "animation.gif")

print("\nAll 3 block variations generated and saved!")
