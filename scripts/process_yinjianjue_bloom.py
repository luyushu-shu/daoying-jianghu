#!/usr/bin/env python3
"""
Process Qingfeng Swordsman Skill 4 Bloom Form: 引剑诀 · 剑意绽放强化版 (万剑归宗 · 混元归渊 · QF-4E)
Pipeline:
1. Crop 8 frames with precise divider bypass (2x4 grid).
2. Clean text titles with localized inpainting for Cell 5 top shockwave.
3. Solid Magenta (#FF00FF) Chroma-key with Despill and Alpha Feathering.
4. Proportional Scaling to Standard Standing Height = 328px (matching all Qingfeng skills).
5. Foot baseline strictly locked to Y=437 on standard 680x480 canvas (PPU 214, Pivot (0.5, 0.09)).
6. Centering on X=340 with stance compensation.
7. Export 8 individual transparent PNGs, 5440x480 sequence strip, dark preview strip, and 255-color mediancut GIF.
8. Integrate into Unity directory with native 32-hex .meta files.
"""

import os
import shutil
import hashlib
import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import label

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_IMAGE = r"C:/Users/luyus/.gemini/antigravity/brain/7ae82753-faef-4cb8-8f99-31cd12839d86/.user_uploaded/media_1790558322927.jpg"

DIR_DESIGN_SKILL = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "04_引剑诀", "强化版_万剑归宗")
DIR_DESIGN_CLEAN = os.path.join(DIR_DESIGN_SKILL, "pure_clean_sprites")
DIR_UNITY_SKILL = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Yinjianjue_Bloom")

for d in [DIR_DESIGN_SKILL, DIR_DESIGN_CLEAN, DIR_UNITY_SKILL]:
    os.makedirs(d, exist_ok=True)

shutil.copyfile(SRC_IMAGE, os.path.join(DIR_DESIGN_SKILL, "yinjianjue_bloom_raw_sheet.jpg"))
shutil.copyfile(SRC_IMAGE, os.path.join(DIR_UNITY_SKILL, "yinjianjue_bloom_raw_sheet.jpg"))

CANVAS_W = 680
CANVAS_H = 480
TARGET_STAND_H = 328.0
RAW_STAND_H = 204.0
SCALE = TARGET_STAND_H / RAW_STAND_H  # ~1.607843
TARGET_FEET_Y = 437
CENTER_X = 340

# (idx, Chinese name, English filename, crop_box, feet_y_raw, body_center_x_raw)
FRAMES_CONFIG = [
    (1, "01_剑阵起势_万灵初唤", "yinjianjue-bloom-1", (0, 0, 255, 285), 244, 135),
    (2, "02_雷霆破晓_剑啸九霄", "yinjianjue-bloom-2", (257, 0, 511, 285), 243, 115),
    (3, "03_白虹贯日_万剑狂澜", "yinjianjue-bloom-3", (513, 0, 767, 285), 244, 125),
    (4, "04_混元归渊_裂隙初启", "yinjianjue-bloom-4", (769, 0, 1024, 285), 244, 112),
    (5, "05_极万钧合刃_冰破乾坤", "yinjianjue-bloom-5", (0, 287, 255, 571), 222, 128),
    (6, "06_八荒扫尽_残月斩空", "yinjianjue-bloom-6", (257, 287, 511, 571), 236, 116),
    (7, "07_龙吟归袖_云霞漫卷", "yinjianjue-bloom-7", (513, 287, 767, 571), 238, 130),
    (8, "08_万道归一_藏锋入鞘", "yinjianjue-bloom-8", (769, 287, 1024, 571), 239, 138),
]


def clean_cell_magenta(crop_arr, idx):
    arr = crop_arr.copy()
    h, w, _ = arr.shape
    
    # Text removal per cell
    if idx in [1, 3, 4]:
        arr[0:31, :] = [253, 2, 250]
    elif idx == 2:
        # Protect lightning at top right (x >= 180)
        arr[0:31, 0:180] = [253, 2, 250]
    elif idx in [5, 6, 7, 8]:
        # Bottom Chinese and English titles in row 2
        arr[241:, :] = [253, 2, 250]
        if idx in [6, 7, 8]:
            arr[0:32, :] = [253, 2, 250]
        elif idx == 5:
            # Inpaint top title over the shockwave array
            r = arr[..., 0]
            g = arr[..., 1]
            b = arr[..., 2]
            mask = np.zeros((h, w), dtype=np.uint8)
            mask[5:32, 55:205] = 1
            is_black = (r < 50) & (g < 50) & (b < 50)
            is_white = (r > 190) & (g > 190) & (b > 190)
            text_mask = (is_black | is_white) & (mask == 1)
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(text_mask.astype(np.uint8), kernel, iterations=2)
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            inpainted_bgr = cv2.inpaint(bgr, dilated, 3, cv2.INPAINT_TELEA)
            arr = cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)

    r = arr[..., 0].astype(np.float32)
    g = arr[..., 1].astype(np.float32)
    b = arr[..., 2].astype(np.float32)
    
    dist = np.sqrt((r - 253.0)**2 + (g - 2.0)**2 + (b - 250.0)**2)
    mag_dominance = np.minimum(r, b) - g
    
    # Protection rules
    is_white = (r > 175.0) & (g > 175.0) & (b > 175.0)
    is_gold = (r > 135.0) & (g > 115.0) & (b < 185.0) & (r > b + 15.0)
    is_cyan = (g > 75.0) & (b > 90.0) & (g > r - 15.0)
    is_frost = (b > 150.0) & (g > 135.0) & (r < 210.0)
    is_skin = (r > 130.0) & (g > 85.0) & (b > 65.0) & ((r - g) < 80.0) & (g > b - 20.0) & (mag_dominance < 30.0)
    is_dark = (r < 65.0) & (g < 65.0) & (b < 65.0)
    is_talisman = (idx == 1) & (r > 150.0) & (g > 120.0)
    
    is_protected = is_white | is_cyan | is_skin | is_dark | is_gold | is_frost | is_talisman
    
    # Background detection
    is_bg = (dist < 130.0) | ((mag_dominance > 30.0) & (g < 140.0))
    is_bg = is_bg & (~is_protected)
    
    # Alpha falloff
    alpha = np.clip((dist - 45.0) / 60.0, 0.0, 1.0)
    alpha[is_bg] = 0.0
    alpha[mag_dominance > 60.0] = 0.0
    alpha[is_protected] = 1.0
    
    # Despill
    spill = np.maximum(0.0, mag_dominance)
    clean_r = np.clip(r - spill * 1.2, 0.0, 255.0)
    clean_g = g
    clean_b = np.clip(b - spill * 0.8, 0.0, 255.0)
    
    # Clean floating noise
    solid = alpha > 0.15
    lbl, num = label(solid)
    if num > 0:
        counts = np.bincount(lbl.ravel())
        small_mask = np.isin(lbl, np.where(counts < 16)[0])
        alpha[small_mask] = 0.0
        
    rgba = np.dstack([clean_r, clean_g, clean_b, alpha * 255.0]).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def generate_gif(processed_frames, frame_durations, gif_output_path):
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
        disposal=2,
        optimize=False
    )
    print(f"Generated clean GIF without black silhouettes: {gif_output_path}")


def write_unity_meta(file_path):
    # Deterministic 32-hex GUID
    rel_path = os.path.relpath(file_path, PROJECT_ROOT).replace('\\', '/')
    guid = hashlib.md5(rel_path.encode('utf-8')).hexdigest()
    
    meta_path = file_path + ".meta"
    meta_content = f"""fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 14
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
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
    flipGreenChannel: 0
  isReadable: 1
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMasterTextureLimit: 0
  doesTextureContainColorSpaceInfo: 1
  grayScaleToAlpha: 0
  generateCubemap: 6
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
  assetBundleName: 
  assetBundleVariant: 
"""
    with open(meta_path, 'w', encoding='utf-8') as f:
        f.write(meta_content)


def main():
    print(f"Loading master sheet: {SRC_IMAGE}")
    raw_sheet = Image.open(SRC_IMAGE).convert('RGB')
    arr_raw = np.array(raw_sheet)
    
    processed_frames = []
    
    for idx, cname, std_name, (x1, y1, x2, y2), feet_y_raw, body_center_x_raw in FRAMES_CONFIG:
        print(f"Processing Bloom Frame {idx}: {cname}...")
        crop = arr_raw[y1:y2, x1:x2]
        clean_img = clean_cell_magenta(crop, idx)
        
        # Scale to standard height
        new_w = int(round(clean_img.width * SCALE))
        new_h = int(round(clean_img.height * SCALE))
        scaled = clean_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Lock to standard canvas (680x480)
        paste_x = CENTER_X - int(round(body_center_x_raw * SCALE))
        paste_y = TARGET_FEET_Y - int(round(feet_y_raw * SCALE))
        
        canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        canvas.paste(scaled, (paste_x, paste_y), scaled)
        
        # Save individual PNG
        design_png = os.path.join(DIR_DESIGN_CLEAN, f"{std_name}.png")
        canvas.save(design_png, "PNG")
        
        unity_png = os.path.join(DIR_UNITY_SKILL, f"{std_name}.png")
        canvas.save(unity_png, "PNG")
        write_unity_meta(unity_png)
        
        processed_frames.append((idx, cname, std_name, canvas))
        
    print(f"All 8 transparent PNG frames exported successfully to {DIR_DESIGN_CLEAN} and {DIR_UNITY_SKILL}!")
    
    # 5440x480 Sequence Strip
    strip_w = CANVAS_W * 8
    seq_strip = Image.new('RGBA', (strip_w, CANVAS_H), (0, 0, 0, 0))
    dark_strip = Image.new('RGB', (strip_w, CANVAS_H), (20, 24, 30))
    
    for i, (_, _, _, fr) in enumerate(processed_frames):
        seq_strip.paste(fr, (i * CANVAS_W, 0), fr)
        dark_strip.paste(fr, (i * CANVAS_W, 0), fr)
        
    seq_path_design = os.path.join(DIR_DESIGN_SKILL, "yinjianjue-bloom-sequence.png")
    seq_strip.save(seq_path_design, "PNG")
    seq_path_unity = os.path.join(DIR_UNITY_SKILL, "yinjianjue-bloom-sequence.png")
    seq_strip.save(seq_path_unity, "PNG")
    write_unity_meta(seq_path_unity)
    
    dark_path_design = os.path.join(DIR_DESIGN_SKILL, "yinjianjue-bloom-dark-preview.png")
    dark_strip.save(dark_path_design, "PNG")
    dark_path_unity = os.path.join(DIR_UNITY_SKILL, "yinjianjue-bloom-dark-preview.png")
    dark_strip.save(dark_path_unity, "PNG")
    write_unity_meta(dark_path_unity)
    
    # 255-Color MedianCut GIF (Bloom Timings)
    # F1: 0.10s, F2: 0.12s, F3: 0.14s, F4: 0.12s, F5: 0.20s, F6: 0.14s, F7: 0.14s, F8: 0.18s
    frame_durations = [100, 120, 140, 120, 200, 140, 140, 180]
    gif_path_design = os.path.join(DIR_DESIGN_SKILL, "yinjianjue-bloom-animation.gif")
    generate_gif(processed_frames, frame_durations, gif_path_design)
    
    gif_path_unity = os.path.join(DIR_UNITY_SKILL, "yinjianjue-bloom-animation.gif")
    shutil.copyfile(gif_path_design, gif_path_unity)
    write_unity_meta(gif_path_unity)
    
    # Unity raw sheet meta
    write_unity_meta(os.path.join(DIR_UNITY_SKILL, "yinjianjue_bloom_raw_sheet.jpg"))
    
    # Folder meta
    write_unity_meta(DIR_UNITY_SKILL)
    
    print("\n=======================================================")
    print(" 引剑诀 · 剑意绽放强化版 (万剑归宗 · QF-4E) 处理完成！")
    print("=======================================================")


if __name__ == "__main__":
    main()
