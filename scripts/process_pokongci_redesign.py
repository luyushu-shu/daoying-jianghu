#!/usr/bin/env python3
"""
Process Qingfeng Swordsman Skill 1: 破空刺 (Piercing Void Thrust)
Redesign Processing Pipeline for BOTH:
1. Normal Version: 破空刺 · 常态版 (QF-1 · 瞬透飞身刺) from media_1790555363030.jpg
2. Sword Intent Bloom Version: 极·破空刺 (QF-1E · 虚空裂隙 · 四灵飞剑) from media_1790555429693.jpg

Features:
- Solid Magenta (#FF00FF) Chroma-key with Despill and Alpha Feathering.
- Grid line isolation for Bloom sheet (bypassing interior 4px black borders).
- Protection of cyan/teal robes (#2EE5D4), phoenix-gold (#FFDF78), white-hot cores (#FFFFFF), icy frost (#D6F6FF), and black ink/boots (#0C1217).
- Uniform Proportional Scaling (Standing Height = 328px, matching Idle/Run/Attack/Huifengwu/Yijianshuanghan).
- Foot baseline strictly locked to Y=437 on 680x480 canvas (PPU 214, Pivot (0.5, 0.09)).
- Exports individual transparent PNGs, 5440x480 sequence strips, dark preview strips, and 255-color GIFs.
- Synchronizes assets into Unity directory and creates valid native .meta files.
"""

import os
import shutil
import uuid
import numpy as np
from PIL import Image
from scipy.ndimage import label

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Input sources
SRC_NORMAL = r"C:/Users/luyus/.gemini/antigravity/brain/7ae82753-faef-4cb8-8f99-31cd12839d86/.user_uploaded/media_1790555363030.jpg"
SRC_BLOOM = r"C:/Users/luyus/.gemini/antigravity/brain/7ae82753-faef-4cb8-8f99-31cd12839d86/.user_uploaded/media_1790555429693.jpg"

# Output directories
DIR_NORMAL_SKILL = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "01_破空刺")
DIR_NORMAL_CLEAN = os.path.join(DIR_NORMAL_SKILL, "pure_clean_sprites")
DIR_NORMAL_UNITY = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Pokongci")

DIR_BLOOM_SKILL = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "01_破空刺", "强化版_极破空刺")
DIR_BLOOM_CLEAN = os.path.join(DIR_BLOOM_SKILL, "pure_clean_sprites")
DIR_BLOOM_GEN = os.path.join(DIR_BLOOM_SKILL, "generated_sheet")
DIR_BLOOM_UNITY = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Pokongci_Bloom")

for d in [DIR_NORMAL_SKILL, DIR_NORMAL_CLEAN, DIR_NORMAL_UNITY,
          DIR_BLOOM_SKILL, DIR_BLOOM_CLEAN, DIR_BLOOM_GEN, DIR_BLOOM_UNITY]:
    os.makedirs(d, exist_ok=True)

# Archive raw sheets
shutil.copyfile(SRC_NORMAL, os.path.join(DIR_NORMAL_SKILL, "pokongci_normal_raw_sheet.jpg"))
shutil.copyfile(SRC_BLOOM, os.path.join(DIR_BLOOM_GEN, "raw-sheet.jpg"))
shutil.copyfile(SRC_BLOOM, os.path.join(DIR_BLOOM_SKILL, "pokongci_bloom_raw_sheet.jpg"))

# Standard Canvas & Scaling Constants
CANVAS_W = 680
CANVAS_H = 480
TARGET_STAND_H = 328.0
TARGET_FEET_Y = 437
CENTER_X = 340


def clean_cell_magenta(crop_img, is_bloom=False):
    """
    Chroma-key solid magenta background (#FF00FF) with despill.
    """
    arr = np.array(crop_img, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    
    dist = np.sqrt((r - 252.0)**2 + (g - 5.0)**2 + (b - 250.0)**2)
    mag_dominance = np.minimum(r, b) - g
    
    # Protection rules
    is_white = (r > 175.0) & (g > 175.0) & (b > 175.0)
    is_gold = (r > 155.0) & (g > 135.0) & (b < 185.0) & (r > b + 15.0)
    is_cyan = (g > 55.0) & ((b > r - 20.0) | (g > r - 20.0))
    is_frost = (b > 160.0) & (g > 140.0) & (r < 220.0)
    is_skin = (r > 130.0) & (g > 85.0) & (b > 65.0) & ((r - g) < 80.0) & (g > b - 20.0)
    is_dark = (r < 65.0) & (g < 65.0) & (b < 65.0)
    
    is_protected = is_white | is_cyan | is_skin | is_dark
    if is_bloom:
        is_protected = is_protected | is_gold | is_frost
        
    # Background detection
    is_bg = (dist < 125.0) | ((mag_dominance > 35.0) & (g < 140.0) & (dist < 185.0))
    is_bg = is_bg & (~is_protected)
    
    # Alpha falloff
    alpha = np.clip((dist - 50.0) / 70.0, 0.0, 1.0)
    alpha[is_bg] = 0.0
    alpha[mag_dominance > 75.0] = 0.0
    alpha[is_protected] = 1.0
    
    # Despill
    spill = np.maximum(0.0, mag_dominance)
    non_protected_spill = spill * (~is_cyan) * (~is_white)
    if is_bloom:
        non_protected_spill = non_protected_spill * (~is_gold) * (~is_frost)
        
    clean_r = np.clip(r - non_protected_spill * 1.1, 0.0, 255.0)
    clean_g = g
    clean_b = np.clip(b - non_protected_spill * 0.7, 0.0, 255.0)
    
    # Noise cleanup
    solid = alpha > 0.15
    lbl, num = label(solid)
    if num > 0:
        counts = np.bincount(lbl.ravel())
        small_mask = np.isin(lbl, np.where(counts < 16)[0])
        alpha[small_mask] = 0.0
        
    rgba = np.dstack([clean_r, clean_g, clean_b, alpha * 255.0]).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def generate_gif(processed_frames, frame_durations, gif_output_path):
    """
    Builds 255-color high-fidelity looping animated GIF with clean 1-bit transparency.
    Uses MEDIANCUT palette quantization and explicit palette injection to prevent black silhouette bug.
    """
    gif_frames = []
    for (f_num, cname, std_name, fr), dur in zip(processed_frames, frame_durations):
        arr = np.array(fr)
        alpha = arr[..., 3]
        trans_mask = alpha < 40
        arr[trans_mask] = [0, 0, 0, 0]
        arr[~trans_mask, 3] = 255
        clean_rgba = Image.fromarray(arr, 'RGBA')
        
        rgb_img = clean_rgba.convert('RGB')
        p_img = rgb_img.quantize(colors=255, method=Image.MEDIANCUT)
        
        palette = list(p_img.getpalette())
        while len(palette) < 256 * 3:
            palette.extend([0, 0, 0])
        palette[255 * 3 : 255 * 3 + 3] = [0, 0, 0]
        
        final_fr = Image.new('P', clean_rgba.size, 255)
        final_fr.putpalette(palette)
        
        p_arr = np.array(p_img, dtype=np.uint8)
        p_arr[trans_mask] = 255
        final_fr.paste(Image.fromarray(p_arr, 'P'), (0, 0))
        
        final_fr.info['transparency'] = 255
        final_fr.info['duration'] = dur
        gif_frames.append(final_fr)
        
    gif_frames[0].save(
        gif_output_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=frame_durations,
        loop=0,
        transparency=255,
        disposal=2
    )
    print(f"Exported GIF: {gif_output_path}")


def create_unity_meta(filepath, is_sprite=True):
    meta_path = filepath + ".meta"
    if os.path.exists(meta_path):
        return
    guid = uuid.uuid4().hex
    if is_sprite:
        content = f"""fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 12
  mipmaps:
    mipMapMode: 0
    enableBMIPContours: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
  isReadable: 1
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMasterTextureLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 0
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: 1
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 9
  spritePivot: {{x: 0.5, y: 0.09}}
  spritePixelsToUnits: 214
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 1
  alphaIsTransparency: 1
  spriteChildren: []
  alphaSource: 1
  platformSettings: []
"""
    else:
        content = f"""fileFormatVersion: 2
guid: {guid}
DefaultImporter:
  externalObjects: {{}}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""
    with open(meta_path, 'w', encoding='utf-8') as f:
        f.write(content)


def process_normal():
    print("\n================== PROCESSING NORMAL POKONGCI (QF-1) ==================")
    raw_sheet = Image.open(SRC_NORMAL).convert('RGB')
    
    # Calibration: F8 measured upright standing height = 273.0 px (boot 661, hair 388)
    raw_stand_h = 273.0
    scale_factor = TARGET_STAND_H / raw_stand_h  # 1.201465
    print(f"Normal Scale Factor: {scale_factor:.6f}")
    
    # 8 Frames config
    frames_config = [
        (1, "01_起势_贴地敛气", "pokongci-1", (0, 0, 256, 343), None),
        (2, "02_离弦_激射飞身", "pokongci-2", (256, 0, 510, 343), None),
        (3, "03_瞬影_贯体穿透", "pokongci-3", (510, 0, 768, 343), None),
        (4, "04_刹车_单膝跪滑", "pokongci-4", (768, 0, 1024, 343), None),
        (5, "05_延时_墨爆裂体", "pokongci-5", (0, 343, 256, 687), None),
        (6, "06_旋剑_回锋抽意", "pokongci-6", (256, 343, 528, 687), None),
        (7, "07_拂袖_导刃回鞘", "pokongci-7", (528, 343, 774, 687), None),
        (8, "08_敛息_秋水归渊", "pokongci-8", (774, 343, 1024, 687), None),
    ]
    
    processed_frames = []
    
    for idx, cname, std_name, box, mask_type in frames_config:
        print(f"Normal Frame {idx}: {cname}...")
        cell = raw_sheet.crop(box)
        clean_rgba = clean_cell_magenta(cell, is_bloom=False)
        
        new_w = int(round(clean_rgba.width * scale_factor))
        new_h = int(round(clean_rgba.height * scale_factor))
        scaled = clean_rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        arr_sc = np.array(scaled)
        alpha = arr_sc[..., 3]
        ys, xs = np.where(alpha > 40)
        
        if len(ys) == 0:
            final_canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        else:
            if idx == 1:
                # F1 Low crouch stance, boots on ground
                feet_y_local = int(round(ys.max() - 2 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 2:
                # F2 Airborne forward launch (+0.25m hop)
                feet_y_local = int(round(ys.max() + 32 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 3:
                # F3 Airborne phasing blur (+0.25m hop)
                feet_y_local = int(round(ys.max() + 32 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 4:
                # F4 Sliding single knee brake on ground
                feet_y_local = int(round(ys.max() - 2 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 5:
                # F5 Sliding brake + delayed ink burst behind
                # Character is on right half of cell, burst on left
                feet_y_local = int(round(ys.max() - 2 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) * 0.55))
            elif idx == 6:
                # F6 Rising flourish with circular ink arc
                feet_y_local = int(round(ys.max() - 3 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) * 0.45))
            elif idx == 7:
                # F7 Turning half-profile, guiding blade to sheath
                feet_y_local = int(round(ys.max() - 2 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            else: # F8
                # F8 Upright standing calm sheath
                feet_y_local = int(round(ys.max() - 2 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
                
            paste_x = CENTER_X - body_center_x_local
            paste_y = TARGET_FEET_Y - feet_y_local
            
            final_canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
            final_canvas.paste(scaled, (paste_x, paste_y), scaled)
            
        processed_frames.append((idx, cname, std_name, final_canvas))
        
        final_canvas.save(os.path.join(DIR_NORMAL_SKILL, f"{cname}.png"))
        final_canvas.save(os.path.join(DIR_NORMAL_SKILL, f"{std_name}.png"))
        final_canvas.save(os.path.join(DIR_NORMAL_CLEAN, f"{cname}.png"))
        final_canvas.save(os.path.join(DIR_NORMAL_CLEAN, f"{std_name}.png"))
        final_canvas.save(os.path.join(DIR_NORMAL_UNITY, f"{std_name}.png"))
        create_unity_meta(os.path.join(DIR_NORMAL_UNITY, f"{std_name}.png"), is_sprite=True)
        
    print(f"Normal: Saved 8 frames to {DIR_NORMAL_UNITY}")
    
    # 5440x480 Strip
    strip = Image.new('RGBA', (CANVAS_W * 8, CANVAS_H), (0, 0, 0, 0))
    for idx, (f_num, cname, std_name, fr) in enumerate(processed_frames):
        strip.paste(fr, (idx * CANVAS_W, 0), fr)
    strip.save(os.path.join(DIR_NORMAL_UNITY, "pokongci-sequence.png"))
    strip.save(os.path.join(DIR_NORMAL_SKILL, "pokongci-sequence.png"))
    strip.save(os.path.join(DIR_NORMAL_CLEAN, "pokongci-sequence.png"))
    create_unity_meta(os.path.join(DIR_NORMAL_UNITY, "pokongci-sequence.png"), is_sprite=True)
    
    # Dark Preview
    dark_strip = Image.new('RGB', (CANVAS_W * 8, CANVAS_H), (10, 16, 24))
    dark_strip.paste(strip, (0, 0), strip)
    dark_strip.save(os.path.join(DIR_NORMAL_SKILL, "pokongci-darkbg-preview.png"))
    
    # High-Fidelity 255-Color GIF
    # Realistic timing:
    # F1=80ms (low skim), F2=60ms (launch), F3=60ms (phasing), F4=100ms (slide brake),
    # F5=140ms (delayed burst), F6=120ms (flourish), F7=120ms (draw sheath), F8=160ms (calm idle)
    durations = [80, 60, 60, 100, 140, 120, 120, 160]
    generate_gif(processed_frames, durations, os.path.join(DIR_NORMAL_SKILL, "pokongci-animation.gif"))
    generate_gif(processed_frames, durations, os.path.join(DIR_NORMAL_UNITY, "pokongci-animation.gif"))
    create_unity_meta(os.path.join(DIR_NORMAL_UNITY, "pokongci-animation.gif"), is_sprite=False)


def process_bloom():
    print("\n================== PROCESSING BLOOM POKONGCI (QF-1E) ==================")
    raw_sheet = Image.open(SRC_BLOOM).convert('RGB')
    
    # Calibration: F8 measured upright standing height = 257.0 px (boot 666, hair 409)
    raw_stand_h = 257.0
    scale_factor = TARGET_STAND_H / raw_stand_h  # 1.276265
    print(f"Bloom Scale Factor: {scale_factor:.6f}")
    
    # 8 Frames config (bypassing interior 4px black grid borders)
    frames_config = [
        (1, "01_起势_引虚空隙", "pokongci-bloom-1", (0, 0, 253, 340), None),
        (2, "02_聚势_四灵剑环", "pokongci-bloom-2", (256, 0, 510, 340), None),
        (3, "03_破障_身化残影", "pokongci-bloom-3", (514, 0, 768, 340), None),
        (4, "04_爆发_虚空穿透", "pokongci-bloom-4", (771, 0, 1024, 340), None),
        (5, "05_落地_共鸣蓄爆", "pokongci-bloom-5", (0, 345, 253, 687), None),
        (6, "06_引爆_三度墨爆", "pokongci-bloom-6", (256, 345, 510, 687), None),
        (7, "07_结界_回风抽剑", "pokongci-bloom-7", (514, 345, 768, 687), None),
        (8, "08_余韵_霜华散尽", "pokongci-bloom-8", (771, 345, 1024, 687), None),
    ]
    
    processed_frames = []
    
    for idx, cname, std_name, box, mask_type in frames_config:
        print(f"Bloom Frame {idx}: {cname}...")
        cell = raw_sheet.crop(box)
        clean_rgba = clean_cell_magenta(cell, is_bloom=True)
        
        new_w = int(round(clean_rgba.width * scale_factor))
        new_h = int(round(clean_rgba.height * scale_factor))
        scaled = clean_rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        arr_sc = np.array(scaled)
        alpha = arr_sc[..., 3]
        ys, xs = np.where(alpha > 40)
        
        if len(ys) == 0:
            final_canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        else:
            if idx == 1:
                # F1 Low horse stance, boots on ground, spatial rift on right
                feet_y_local = int(round(ys.max() - 2 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) * 0.45))
            elif idx == 2:
                # F2 Deep forward crouch with 4 orbiting swords
                feet_y_local = int(round(ys.max() - 2 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 3:
                # F3 Airborne barrier breach (+0.25m hop)
                feet_y_local = int(round(ys.max() + 32 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 4:
                # F4 Airborne supreme thrust into spatial fracture (+0.25m hop)
                feet_y_local = int(round(ys.max() + 32 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) * 0.46))
            elif idx == 5:
                # F5 Grounding in deep lunge behind enemy, boots on ground
                feet_y_local = int(round(ys.max() - 2 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) * 0.44))
            elif idx == 6:
                # F6 Triple spatial shatter burst, boots on ground
                feet_y_local = int(round(ys.max() - 2 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 7:
                # F7 Frost domain on ground, boots on ground, frost extends 6px below
                feet_y_local = int(round(ys.max() - 6 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            else: # F8
                # F8 Upright sheathing, drifting snowflakes, boots on ground
                feet_y_local = int(round(ys.max() - 2 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
                
            paste_x = CENTER_X - body_center_x_local
            paste_y = TARGET_FEET_Y - feet_y_local
            
            final_canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
            final_canvas.paste(scaled, (paste_x, paste_y), scaled)
            
        processed_frames.append((idx, cname, std_name, final_canvas))
        
        final_canvas.save(os.path.join(DIR_BLOOM_SKILL, f"{cname}.png"))
        final_canvas.save(os.path.join(DIR_BLOOM_SKILL, f"{std_name}.png"))
        final_canvas.save(os.path.join(DIR_BLOOM_CLEAN, f"{cname}.png"))
        final_canvas.save(os.path.join(DIR_BLOOM_CLEAN, f"{std_name}.png"))
        final_canvas.save(os.path.join(DIR_BLOOM_UNITY, f"{std_name}.png"))
        create_unity_meta(os.path.join(DIR_BLOOM_UNITY, f"{std_name}.png"), is_sprite=True)
        
    print(f"Bloom: Saved 8 frames to {DIR_BLOOM_UNITY}")
    
    # 5440x480 Strip
    strip = Image.new('RGBA', (CANVAS_W * 8, CANVAS_H), (0, 0, 0, 0))
    for idx, (f_num, cname, std_name, fr) in enumerate(processed_frames):
        strip.paste(fr, (idx * CANVAS_W, 0), fr)
    strip.save(os.path.join(DIR_BLOOM_UNITY, "pokongci-bloom-sequence.png"))
    strip.save(os.path.join(DIR_BLOOM_SKILL, "pokongci-bloom-sequence.png"))
    strip.save(os.path.join(DIR_BLOOM_CLEAN, "pokongci-bloom-sequence.png"))
    create_unity_meta(os.path.join(DIR_BLOOM_UNITY, "pokongci-bloom-sequence.png"), is_sprite=True)
    
    # Dark Preview
    dark_strip = Image.new('RGB', (CANVAS_W * 8, CANVAS_H), (10, 16, 24))
    dark_strip.paste(strip, (0, 0), strip)
    dark_strip.save(os.path.join(DIR_BLOOM_SKILL, "pokongci-bloom-darkbg-preview.png"))
    
    # High-Fidelity 255-Color GIF
    # Realistic timing:
    # F1=100ms (void rift), F2=80ms (4 swords), F3=60ms (breach), F4=80ms (void thrust),
    # F5=120ms (resonance), F6=160ms (triple shatter), F7=140ms (frost domain), F8=180ms (snowfall idle)
    durations = [100, 80, 60, 80, 120, 160, 140, 180]
    generate_gif(processed_frames, durations, os.path.join(DIR_BLOOM_SKILL, "pokongci-bloom-animation.gif"))
    generate_gif(processed_frames, durations, os.path.join(DIR_BLOOM_UNITY, "pokongci-bloom-animation.gif"))
    create_unity_meta(os.path.join(DIR_BLOOM_UNITY, "pokongci-bloom-animation.gif"), is_sprite=False)


if __name__ == "__main__":
    process_normal()
    process_bloom()
    print("\n[SUCCESS] Both Normal and Bloom Pokongci pipelines finished successfully!")
