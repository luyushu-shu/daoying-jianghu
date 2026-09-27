#!/usr/bin/env python3
"""
Process Qingfeng Swordsman Skill 2: 回风舞 (Whirling Wind Dance)
Redesign Processing Pipeline for BOTH:
1. Normal Version: 回风舞 · 常态版 (QF-2) from media_1790510065644.jpg
2. Sword Intent Bloom Version: 极·回风舞 · 青鸾风暴 (QF-2E) from media_1790510105862.jpg

Features:
- Dual-Mode Chroma-key (#EE0070 Crimson Magenta & #FA00C8 Vivid Magenta) with despill.
- Protection of cyan/teal robes (#2EE5D4), phoenix-gold (#FFDF78), white-hot cores (#FFFFFF), and black ink/boots (#0C1217).
- Uniform Proportional Scaling (Standing Height = 328px, matching Idle/Run/Attack/Pokongci/Yijianshuanghan).
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
SRC_NORMAL = r"C:/Users/luyus/.gemini/antigravity/brain/7ae82753-faef-4cb8-8f99-31cd12839d86/.user_uploaded/media_1790510065644.jpg"
SRC_BLOOM = r"C:/Users/luyus/.gemini/antigravity/brain/7ae82753-faef-4cb8-8f99-31cd12839d86/.user_uploaded/media_1790510105862.jpg"

# Output directories
DIR_NORMAL_SKILL = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "02_回风舞")
DIR_NORMAL_CLEAN = os.path.join(DIR_NORMAL_SKILL, "pure_clean_sprites")
DIR_NORMAL_UNITY = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Huifengwu")

DIR_BLOOM_SKILL = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "02_回风舞", "强化版_青鸾风暴")
DIR_BLOOM_CLEAN = os.path.join(DIR_BLOOM_SKILL, "pure_clean_sprites")
DIR_BLOOM_GEN = os.path.join(DIR_BLOOM_SKILL, "generated_sheet")
DIR_BLOOM_UNITY = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Huifengwu_Bloom")

for d in [DIR_NORMAL_SKILL, DIR_NORMAL_CLEAN, DIR_NORMAL_UNITY,
          DIR_BLOOM_SKILL, DIR_BLOOM_CLEAN, DIR_BLOOM_GEN, DIR_BLOOM_UNITY]:
    os.makedirs(d, exist_ok=True)

# Archive raw sheets
shutil.copyfile(SRC_NORMAL, os.path.join(DIR_NORMAL_SKILL, "huifengwu_normal_raw_sheet.jpg"))
shutil.copyfile(SRC_BLOOM, os.path.join(DIR_BLOOM_GEN, "raw-sheet.jpg"))
shutil.copyfile(SRC_BLOOM, os.path.join(DIR_BLOOM_SKILL, "huifengwu_bloom_raw_sheet.jpg"))

# Standard Canvas & Scaling Constants
CANVAS_W = 680
CANVAS_H = 480
TARGET_STAND_H = 328.0
TARGET_FEET_Y = 437
CENTER_X = 340


def clean_cell_normal(crop_img):
    """
    Chroma-key for Image 1 (Normal): background ~ (238, 1, 111)
    """
    arr = np.array(crop_img, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    
    dist = np.sqrt((r - 238.0)**2 + (g - 1.0)**2 + (b - 111.0)**2)
    
    # Protection rules
    is_white_slash = (r > 170.0) & (g > 160.0) & (b > 160.0)
    is_teal = (g > 50.0) & ((g > r - 30.0) | (b > r - 20.0))
    is_skin = (r > 135.0) & (g > 85.0) & (b > 65.0) & ((r - g) < 90.0) & (g > b - 20.0)
    is_dark = (r < 65.0) & (g < 65.0) & (b < 65.0)
    is_protected = is_white_slash | is_teal | is_skin | is_dark
    
    # Background detection
    is_bg = (g < 32.0) & (r > 175.0) & (b > 65.0) & (b < 165.0) & (dist < 115.0)
    is_bg = is_bg & (~is_protected)
    
    # Alpha falloff
    alpha = np.clip((dist - 40.0) / 60.0, 0.0, 1.0)
    alpha[is_bg] = 0.0
    alpha[dist < 35.0] = 0.0
    alpha[is_protected] = 1.0
    
    # Despill
    spill = np.clip((r - np.maximum(g, b * 0.8)) / 2.0, 0.0, 255.0)
    non_protected_spill = spill * (~is_teal) * (~is_white_slash)
    clean_r = np.clip(r - non_protected_spill * 0.9, 0.0, 255.0)
    clean_g = g
    clean_b = np.clip(b - non_protected_spill * 0.4, 0.0, 255.0)
    
    # Noise cleanup
    solid = alpha > 0.15
    lbl, num = label(solid)
    if num > 0:
        counts = np.bincount(lbl.ravel())
        small_mask = np.isin(lbl, np.where(counts < 16)[0])
        alpha[small_mask] = 0.0
        
    rgba = np.dstack([clean_r, clean_g, clean_b, alpha * 255.0]).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def clean_cell_bloom(crop_img):
    """
    Chroma-key for Image 2 (Bloom): background ~ (250, 0, 200)
    """
    arr = np.array(crop_img, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    
    dist = np.sqrt((r - 250.0)**2 + (g - 0.0)**2 + (b - 200.0)**2)
    mag_dominance = np.minimum(r, b) - g
    
    # Protection rules
    is_white = (r > 175.0) & (g > 175.0) & (b > 175.0)
    is_gold = (r > 155.0) & (g > 135.0) & (b < 185.0) & (r > b + 15.0)
    is_cyan = (g > 55.0) & ((b > r - 20.0) | (g > r - 20.0))
    is_skin = (r > 130.0) & (g > 85.0) & (b > 65.0) & ((r - g) < 80.0) & (g > b - 20.0)
    is_dark = (r < 65.0) & (g < 65.0) & (b < 65.0)
    is_protected = is_white | is_gold | is_cyan | is_skin | is_dark
    
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
    non_protected_spill = spill * (~is_cyan) * (~is_white) * (~is_gold)
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
    print("\n================== PROCESSING NORMAL HUIFENGWU (QF-2) ==================")
    raw_sheet = Image.open(SRC_NORMAL).convert('RGB')
    
    # Calibration: F8 measured upright standing height = 245.0 px (boot 618, hair 373)
    raw_stand_h = 245.0
    scale_factor = TARGET_STAND_H / raw_stand_h  # 1.338776
    print(f"Normal Scale Factor: {scale_factor:.6f}")
    
    # 8 Frames config
    # Row 1 (y: 0..343): cols [0..256, 256..512, 512..768, 768..1024]
    # Row 2 (y: 343..687): cols [0..256, 256..512, 512..768, 768..1024]
    frames_config = [
        (1, "01_蓄势_回风引气", "huifengwu-1", (0, 0, 256, 343), None),
        (2, "02_起势_扶摇旋风", "huifengwu-2", (256, 0, 512, 343), None),
        (3, "03_凌空_双层风暴", "huifengwu-3", (512, 0, 768, 343), None),
        (4, "04_舒臂_顺风展袖", "huifengwu-4", (768, 0, 1024, 343), None),
        (5, "05_绝杀_双月交叉", "huifengwu-5", (0, 343, 256, 687), None),
        (6, "06_定地_沉剑裂风", "huifengwu-6", (256, 343, 512, 687), "mask_normal_f6"),
        (7, "07_挽花_回风散意", "huifengwu-7", (512, 343, 768, 687), None),
        (8, "08_敛意_秋水入鞘", "huifengwu-8", (768, 343, 1024, 687), None),
    ]
    
    processed_frames = []
    
    for idx, cname, std_name, box, mask_type in frames_config:
        print(f"Normal Frame {idx}: {cname}...")
        cell = raw_sheet.crop(box)
        
        if mask_type == "mask_normal_f6":
            # Trim 2px on left/right borders where ground ink touches adjacent cells
            arr_cell = np.array(cell)
            arr_cell[:, :2] = [238, 1, 111]
            arr_cell[:, -2:] = [238, 1, 111]
            cell = Image.fromarray(arr_cell)
            
        clean_rgba = clean_cell_normal(cell)
        
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
                # Ground wind circle extends ~6px below feet
                feet_y_local = int(round(ys.max() - 6 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 2:
                # Jumping up slightly (+0.12m)
                feet_y_local = int(round(ys.max() + 18 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 3:
                # Midair peak (+0.25m)
                feet_y_local = int(round(ys.max() + 32 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 4:
                # Midair float glide (+0.20m)
                feet_y_local = int(round(ys.max() + 26 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 5:
                # Descending cross-slash
                feet_y_local = int(round(ys.max() - 5 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 6:
                # Sword tip in ground with ink splash
                feet_y_local = int(round(ys.max() - 8 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 7:
                # Flourish standing
                feet_y_local = int(round(ys.max() - 6 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            else: # F8
                feet_y_local = int(round(ys.max() - 3 * scale_factor))
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
    strip.save(os.path.join(DIR_NORMAL_UNITY, "huifengwu-sequence.png"))
    strip.save(os.path.join(DIR_NORMAL_SKILL, "huifengwu-sequence.png"))
    strip.save(os.path.join(DIR_NORMAL_CLEAN, "huifengwu-sequence.png"))
    create_unity_meta(os.path.join(DIR_NORMAL_UNITY, "huifengwu-sequence.png"), is_sprite=True)
    
    # Dark Preview
    dark_strip = Image.new('RGB', (CANVAS_W * 8, CANVAS_H), (10, 16, 24))
    dark_strip.paste(strip, (0, 0), strip)
    dark_strip.save(os.path.join(DIR_NORMAL_SKILL, "huifengwu-darkbg-preview.png"))
    
    # High-Fidelity 255-Color GIF
    durations = [120, 100, 100, 100, 120, 140, 120, 160]
    generate_gif(processed_frames, durations, os.path.join(DIR_NORMAL_SKILL, "huifengwu-animation.gif"))
    generate_gif(processed_frames, durations, os.path.join(DIR_NORMAL_UNITY, "huifengwu-animation.gif"))
    create_unity_meta(os.path.join(DIR_NORMAL_UNITY, "huifengwu-animation.gif"), is_sprite=False)


def process_bloom():
    print("\n================== PROCESSING BLOOM HUIFENGWU (QF-2E) ==================")
    raw_sheet = Image.open(SRC_BLOOM).convert('RGB')
    
    # Calibration: F8 measured upright standing height = 267.0 px (boot 632, hair 365)
    raw_stand_h = 267.0
    scale_factor = TARGET_STAND_H / raw_stand_h  # 1.228464
    print(f"Bloom Scale Factor: {scale_factor:.6f}")
    
    # 8 Frames config with boundary calibration
    frames_config = [
        (1, "01_起势_太极阴阳涡", "huifengwu-bloom-1", (0, 0, 260, 340), "mask_bloom_f1"),
        (2, "02_旋足_青鸾振翼", "huifengwu-bloom-2", (260, 0, 514, 340), "mask_bloom_f2"),
        (3, "03_狂舞_双风连环", "huifengwu-bloom-3", (514, 0, 767, 340), "mask_bloom_f3"),
        (4, "04_法相_青鸾冲霄", "huifengwu-bloom-4", (767, 0, 1024, 340), "mask_bloom_f4"),
        (5, "05_绝杀_双鸾绞刃", "huifengwu-bloom-5", (0, 340, 252, 687), "mask_bloom_f5"),
        (6, "06_沉势_定地破岚", "huifengwu-bloom-6", (248, 340, 522, 687), "mask_bloom_f6"),
        (7, "07_挽花_散羽归虚", "huifengwu-bloom-7", (522, 340, 775, 687), "mask_bloom_f7"),
        (8, "08_敛息_秋水归渊", "huifengwu-bloom-8", (770, 340, 1024, 687), "mask_bloom_f8"),
    ]
    
    processed_frames = []
    
    for idx, cname, std_name, box, mask_type in frames_config:
        print(f"Bloom Frame {idx}: {cname}...")
        cell = raw_sheet.crop(box)
        
        arr_cell = np.array(cell)
        
        if mask_type == "mask_bloom_f1":
            # Right edge clean (x > 255)
            arr_cell[:, 256:] = [250, 0, 200]
        elif mask_type == "mask_bloom_f2":
            # Left edge clean (x < 3)
            arr_cell[:, :2] = [250, 0, 200]
        elif mask_type == "mask_bloom_f3":
            # Right edge clean (x > 250)
            arr_cell[:, -3:] = [250, 0, 200]
        elif mask_type == "mask_bloom_f4":
            # Left edge clean (x < 3)
            arr_cell[:, :2] = [250, 0, 200]
        elif mask_type == "mask_bloom_f5":
            # Right edge clean (x > 248)
            arr_cell[:, -4:] = [250, 0, 200]
        elif mask_type == "mask_bloom_f6":
            # In F6 crop (x in 248..522):
            # Sword tip is at x in [0..6] for y > 180 (global y > 520)
            # For y < 180, mask out left edge x < 8 to ensure no bleed from F5
            arr_cell[:180, :8] = [250, 0, 200]
        elif mask_type == "mask_bloom_f7":
            # Left edge clean (x < 3)
            arr_cell[:, :3] = [250, 0, 200]
            # Right edge clean for y > 200 where F8 sword is
            arr_cell[200:, -5:] = [250, 0, 200]
        elif mask_type == "mask_bloom_f8":
            # Left edge clean for y < 190 where F7 feather is
            arr_cell[:190, :10] = [250, 0, 200]
            
        cell = Image.fromarray(arr_cell)
        clean_rgba = clean_cell_bloom(cell)
        
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
                # Taiji yin-yang vortex extends ~12px below feet
                feet_y_local = int(round(ys.max() - 12 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 2:
                # Jumping up with phoenix wing (+0.14m)
                feet_y_local = int(round(ys.max() + 20 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 3:
                # Midair spinning double storm (+0.28m)
                feet_y_local = int(round(ys.max() + 36 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 4:
                # Peak phoenix wings avatar (+0.30m)
                feet_y_local = int(round(ys.max() + 38 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 5:
                # Descending explosive cross X-slash
                feet_y_local = int(round(ys.max() - 6 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 6:
                # Ground slam cracking tiles & shockwave
                feet_y_local = int(round(ys.max() - 10 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 7:
                # Flourish with dissolving wings/feathers
                feet_y_local = int(round(ys.max() - 8 * scale_factor))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            else: # F8
                # Calm sheath stance, ground wind mist extends 5px below boots
                feet_y_local = int(round(ys.max() - 5 * scale_factor))
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
    strip.save(os.path.join(DIR_BLOOM_UNITY, "huifengwu-bloom-sequence.png"))
    strip.save(os.path.join(DIR_BLOOM_SKILL, "huifengwu-bloom-sequence.png"))
    strip.save(os.path.join(DIR_BLOOM_CLEAN, "huifengwu-bloom-sequence.png"))
    create_unity_meta(os.path.join(DIR_BLOOM_UNITY, "huifengwu-bloom-sequence.png"), is_sprite=True)
    
    # Dark Preview
    dark_strip = Image.new('RGB', (CANVAS_W * 8, CANVAS_H), (10, 16, 24))
    dark_strip.paste(strip, (0, 0), strip)
    dark_strip.save(os.path.join(DIR_BLOOM_SKILL, "huifengwu-bloom-darkbg-preview.png"))
    
    # High-Fidelity 255-Color GIF
    durations = [140, 100, 100, 120, 140, 140, 120, 160]
    generate_gif(processed_frames, durations, os.path.join(DIR_BLOOM_SKILL, "huifengwu-bloom-animation.gif"))
    generate_gif(processed_frames, durations, os.path.join(DIR_BLOOM_UNITY, "huifengwu-bloom-animation.gif"))
    create_unity_meta(os.path.join(DIR_BLOOM_UNITY, "huifengwu-bloom-animation.gif"), is_sprite=False)


if __name__ == "__main__":
    process_normal()
    process_bloom()
    print("\n[SUCCESS] Both Normal and Bloom Huifengwu pipelines finished successfully!")
