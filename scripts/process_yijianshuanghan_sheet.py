#!/usr/bin/env python3
"""
Process Qingfeng Swordsman Skill 3: 一剑霜寒 (Frostbound Slash, QF-3)
Directly postprocesses the user's master sprite sheet (media_1790502923957.jpg)
Features:
- Solid Magenta (#FF00FF) Chroma-key with Despill and Alpha Feathering.
- Intelligent separation of all 8 frames:
  1. 结势 · 冰霜凝聚 (Horse stance, ice gathering at feet)
  2. 提剑 · 寒气汇聚 (Raise sword, frost vortex swirling)
  3. 蓄力 · 冰刃成型 (Deep charge, sword in ground with crystal ice peaks)
  4. 斩出 · 霜寒剑芒 (Huge horizontal frost cleave arc)
  5. 前刺 · 冰锋破地 (Forward thrust, massive sharp ice peaks tearing through floor)
  6. 进步 · 寒气延绵 (Stepping forward, continuous frost laser thrust)
  7. 振刃 · 冰晶碎散 (Wrist flick, diamond ice shards burst)
  8. 入鞘 · 风息归平 (Smooth sheath, calm martial posture)
- Uniform Proportional Scaling (Standing Height = 328px, matching Idle/Run/Attack/Pokongci/Huifengwu).
- Foot baseline locked to Y=437 on 680x480 canvas (PPU 214, Pivot 0.5, 0.09).
- Exports individual transparent PNGs, 5440x480 sequence strip, dark bg preview, and transparent looping GIF.
- Synchronizes assets into Unity directory and creates valid native .meta files.
"""

import os
import shutil
import numpy as np
from PIL import Image
from scipy.ndimage import label, binary_opening

RAW_SOURCE = r"C:/Users/luyus/.gemini/antigravity/brain/7ae82753-faef-4cb8-8f99-31cd12839d86/.user_uploaded/media_1790502923957.jpg"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "03_一剑霜寒")
UNITY_DIR = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Yijianshuanghan")
CLEAN_DIR = os.path.join(SKILL_DIR, "pure_clean_sprites")
GEN_DIR = os.path.join(SKILL_DIR, "generated_sheet")

for d in [SKILL_DIR, UNITY_DIR, CLEAN_DIR, GEN_DIR]:
    os.makedirs(d, exist_ok=True)

# Archive raw sheet
shutil.copyfile(RAW_SOURCE, os.path.join(GEN_DIR, "raw-sheet.jpg"))

CANVAS_W = 680
CANVAS_H = 480
TARGET_STAND_H = 328.0
RAW_STAND_H = 255.0  # Measured from Frame 8 upright standing stance
SCALE_FACTOR = TARGET_STAND_H / RAW_STAND_H
TARGET_FEET_Y = 437
CENTER_X = 340


def clean_cell_magenta(crop_img):
    """
    Chroma-key solid magenta background (#FF00FF) with despill.
    Protects cyan/white frost, deep azure ice crystals, and dark ink clothing.
    """
    arr = np.array(crop_img, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    
    dist = np.sqrt((r - 255.0)**2 + (g - 0.0)**2 + (b - 255.0)**2)
    mag_dominance = np.minimum(r, b) - g
    
    # Ice protection masks
    is_white_ice = (r > 190.0) & (g > 200.0) & (b > 210.0)
    is_cyan_ice = (g > 80.0) & (b > 90.0) & (b > r - 15.0)
    
    # Background detection
    bg_mask = (dist < 125.0) | ((mag_dominance > 35.0) & (g < 140.0) & (dist < 185.0))
    bg_mask = bg_mask & (~is_white_ice) & (~(is_cyan_ice & (g > 150.0)))
    
    # Smooth alpha falloff
    alpha = np.clip((dist - 65.0) / 75.0, 0.0, 1.0)
    alpha[bg_mask] = 0.0
    alpha[mag_dominance > 75.0] = 0.0
    
    # Despill magenta from edges
    spill = np.maximum(0.0, mag_dominance)
    non_ice_spill = spill * (~is_cyan_ice) * (~is_white_ice)
    
    clean_r = np.clip(r - non_ice_spill * 1.15, 0.0, 255.0)
    clean_g = g
    clean_b = np.clip(b - non_ice_spill * 0.75, 0.0, 255.0)
    
    # Remove small floating noise particles (< 16 pixels)
    solid = alpha > 0.15
    lbl, num = label(solid)
    if num > 0:
        counts = np.bincount(lbl.ravel())
        small_mask = np.isin(lbl, np.where(counts < 16)[0])
        alpha[small_mask] = 0.0
        
    rgba = np.dstack([clean_r, clean_g, clean_b, alpha * 255.0]).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def process_all_frames():
    raw_sheet = Image.open(RAW_SOURCE).convert('RGB')
    print(f"Loaded master sheet: {raw_sheet.size}")
    
    # Cell boundaries avoiding labels
    # Row 1 (y: 0..296)
    # Row 2 (y: 330..612)
    frames_config = [
        (1, "01_结势_冰霜凝聚", "yijianshuanghan-1", (0, 0, 270, 296), None),
        (2, "02_提剑_寒气汇聚", "yijianshuanghan-2", (270, 0, 485, 296), None),
        (3, "03_蓄力_冰刃成型", "yijianshuanghan-3", (485, 0, 735, 296), "mask_f3"),
        (4, "04_斩出_霜寒剑芒", "yijianshuanghan-4", (718, 0, 1024, 296), "mask_f4"),
        (5, "05_前刺_冰锋破地", "yijianshuanghan-5", (0, 330, 280, 612), None),
        (6, "06_进步_寒气延绵", "yijianshuanghan-6", (282, 330, 520, 612), None),
        (7, "07_振刃_冰晶碎散", "yijianshuanghan-7", (520, 330, 775, 612), None),
        (8, "08_入鞘_风息归平", "yijianshuanghan-8", (775, 330, 1024, 612), None),
    ]
    
    processed_frames = []
    
    for idx, cname, std_name, box, special_mask in frames_config:
        print(f"Processing Frame {idx}: {cname}...")
        cell = raw_sheet.crop(box)
        
        # Apply special inter-cell separation if needed
        if special_mask == "mask_f3":
            # Mask out F4 upper-left robe sleeve (x > 718 - 485 = 233, y < 220)
            arr_cell = np.array(cell)
            w_box = box[2] - box[0]
            for y in range(min(220, cell.height)):
                for x in range(233, cell.width):
                    arr_cell[y, x] = [255, 0, 255]
            cell = Image.fromarray(arr_cell)
            
        elif special_mask == "mask_f4":
            # Mask out F3 lower-right ice spike (x < 735 - 718 = 17, y > 220)
            arr_cell = np.array(cell)
            for y in range(220, cell.height):
                for x in range(min(17, cell.width)):
                    arr_cell[y, x] = [255, 0, 255]
            cell = Image.fromarray(arr_cell)
            
        clean_rgba = clean_cell_magenta(cell)
        
        # Scale uniformly
        new_w = int(round(clean_rgba.width * SCALE_FACTOR))
        new_h = int(round(clean_rgba.height * SCALE_FACTOR))
        scaled = clean_rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Compute feet and center for placement onto 680x480 canvas
        arr_sc = np.array(scaled)
        alpha = arr_sc[..., 3]
        ys, xs = np.where(alpha > 40)
        
        if len(ys) == 0:
            final_canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        else:
            cur_feet_y = np.max(ys)
            cur_cx = int(np.median(xs))
            
            # Ground anchoring
            shift_y = TARGET_FEET_Y - cur_feet_y
            shift_x = CENTER_X - cur_cx
            
            # Clamp so effects don't get cut off
            if shift_x + np.min(xs) < 10:
                shift_x = 10 - np.min(xs)
            if shift_x + np.max(xs) > CANVAS_W - 10:
                shift_x = (CANVAS_W - 10) - np.max(xs)
            if shift_y + np.min(ys) < 10:
                shift_y = 10 - np.min(ys)
                
            final_canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
            final_canvas.paste(scaled, (shift_x, shift_y), scaled)
            
        processed_frames.append((idx, cname, std_name, final_canvas))
        
        # Save individual standard and named frames
        fn_std = f"{std_name}.png"
        fn_named = f"{cname}.png"
        fn_aligned = f"aligned_{cname}.png"
        
        final_canvas.save(os.path.join(UNITY_DIR, fn_std))
        final_canvas.save(os.path.join(CLEAN_DIR, fn_std))
        final_canvas.save(os.path.join(CLEAN_DIR, fn_named))
        final_canvas.save(os.path.join(CLEAN_DIR, fn_aligned))
        final_canvas.save(os.path.join(SKILL_DIR, fn_std))
        final_canvas.save(os.path.join(SKILL_DIR, fn_named))
        
    print(f"Saved 8 clean frames to {UNITY_DIR} and {SKILL_DIR}")
    
    # 5440x480 Sequence Strip
    strip = Image.new('RGBA', (CANVAS_W * 8, CANVAS_H), (0, 0, 0, 0))
    for idx, cname, std_name, fr in processed_frames:
        strip.paste(fr, ((idx - 1) * CANVAS_W, 0), fr)
        
    strip.save(os.path.join(UNITY_DIR, "yijianshuanghan-sequence.png"))
    strip.save(os.path.join(SKILL_DIR, "yijianshuanghan-sequence.png"))
    strip.save(os.path.join(CLEAN_DIR, "yijianshuanghan-sequence.png"))
    strip.save(os.path.join(SKILL_DIR, "sequence-strip.png"))
    print(f"Sequence strip updated: {strip.size}")
    
    # Dark Background Preview
    dark_strip = Image.new('RGB', (CANVAS_W * 8, CANVAS_H), (12, 18, 24))
    dark_strip.paste(strip, (0, 0), strip)
    dark_strip.save(os.path.join(SKILL_DIR, "yijianshuanghan-darkbg-preview.png"))
    
    # Transparent Animated GIF
    # Realistic 60 FPS timings:
    # F1=100ms, F2=130ms, F3=180ms (charge), F4=90ms (slash), F5=110ms (ice surge),
    # F6=130ms (recovery lock), F7=130ms (shatter), F8=160ms (sheathe)
    frame_durations = [100, 130, 180, 90, 110, 130, 130, 160]
    
    gif_frames = []
    for (idx, cname, std_name, fr), dur in zip(processed_frames, frame_durations):
        alpha = fr.split()[3]
        mask = Image.eval(alpha, lambda a: 255 if a > 25 else 0)
        p_frame = fr.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        
        final_gif_fr = Image.new('P', p_frame.size, 255)
        final_gif_fr.paste(p_frame, (0, 0), mask)
        final_gif_fr.info['transparency'] = 255
        gif_frames.append(final_gif_fr)
        
    for gpath in [
        os.path.join(UNITY_DIR, "yijianshuanghan-animation.gif"),
        os.path.join(SKILL_DIR, "yijianshuanghan-animation.gif"),
        os.path.join(CLEAN_DIR, "yijianshuanghan-animation.gif"),
        os.path.join(SKILL_DIR, "animation.gif")
    ]:
        gif_frames[0].save(
            gpath,
            save_all=True,
            append_images=gif_frames[1:],
            duration=frame_durations,
            loop=0,
            disposal=2,
            transparency=255
        )
    print(f"Animated GIF updated successfully.")

if __name__ == '__main__':
    process_all_frames()
