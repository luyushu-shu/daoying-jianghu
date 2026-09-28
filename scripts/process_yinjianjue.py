#!/usr/bin/env python3
"""
Process Qingfeng Swordsman Skill 4: 引剑诀 · 流光溯影 (Radiant Flying Sword Recall)
Pipeline:
1. Solid Magenta (#FF00FF) Chroma-key with Despill and Alpha Feathering.
2. Boundary isolation to bypass top English/Chinese text titles cleanly.
3. Proportional Scaling to Standard Standing Height = 328px (matching all Qingfeng skills).
4. Foot baseline strictly locked to Y=437 on standard 680x480 canvas (PPU 214, Pivot (0.5, 0.09)).
5. Centering on X=340 with stance compensation.
6. Export 8 individual transparent PNGs, 5440x480 sequence strip, dark preview strip, and 255-color mediancut GIF.
7. Integrate into Unity directory with native .meta files.
"""

import os
import shutil
import uuid
import numpy as np
from PIL import Image
from scipy.ndimage import label

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_IMAGE = r"C:/Users/luyus/.gemini/antigravity/brain/7ae82753-faef-4cb8-8f99-31cd12839d86/.user_uploaded/media_1790557001074.jpg"

DIR_DESIGN_SKILL = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "04_引剑诀")
DIR_DESIGN_CLEAN = os.path.join(DIR_DESIGN_SKILL, "pure_clean_sprites")
DIR_UNITY_SKILL = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Yinjianjue")

for d in [DIR_DESIGN_SKILL, DIR_DESIGN_CLEAN, DIR_UNITY_SKILL]:
    os.makedirs(d, exist_ok=True)

shutil.copyfile(SRC_IMAGE, os.path.join(DIR_DESIGN_SKILL, "yinjianjue_raw_sheet.jpg"))

CANVAS_W = 680
CANVAS_H = 480
TARGET_STAND_H = 328.0
TARGET_FEET_Y = 437
CENTER_X = 340


def clean_cell_magenta(crop_img):
    arr = np.array(crop_img, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    
    dist = np.sqrt((r - 253.0)**2 + (g - 2.0)**2 + (b - 250.0)**2)
    mag_dominance = np.minimum(r, b) - g
    
    # Protection rules
    is_white = (r > 175.0) & (g > 175.0) & (b > 175.0)
    is_gold = (r > 155.0) & (g > 135.0) & (b < 185.0) & (r > b + 15.0)
    is_cyan = (g > 55.0) & ((b > r - 20.0) | (g > r - 20.0))
    is_frost = (b > 160.0) & (g > 140.0) & (r < 220.0)
    is_skin = (r > 130.0) & (g > 85.0) & (b > 65.0) & ((r - g) < 80.0) & (g > b - 20.0)
    is_dark = (r < 65.0) & (g < 65.0) & (b < 65.0)
    
    is_protected = is_white | is_cyan | is_skin | is_dark | is_gold | is_frost
    
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
    non_protected_spill = spill * (~is_cyan) * (~is_white) * (~is_frost)
    
    clean_r = np.clip(r - non_protected_spill * 1.1, 0.0, 255.0)
    clean_g = g
    clean_b = np.clip(b - non_protected_spill * 0.7, 0.0, 255.0)
    
    # Noise cleanup: remove small isolated pixel clusters
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
        meta_content = f"""fileFormatVersion: 2
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
  spriteColliderType: 1
  textureType: 8
  pixelPerUnit: 214
"""
    else:
        meta_content = f"""fileFormatVersion: 2
guid: {guid}
DefaultImporter:
  externalObjects: {{}}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(meta_content)


def main():
    sheet_img = Image.open(SRC_IMAGE).convert("RGB")
    W, H = sheet_img.size
    print(f"Loaded sheet: {SRC_IMAGE} ({W}x{H})")

    # Cell definitions avoiding top text labels
    # (col_idx, crop_x0, crop_y0, crop_x1, crop_y1, stance_center_x, foot_baseline_y, cname, std_name)
    frames_meta = [
        (1, 0, 44, 256, 285, 134.5, 282.0, "01_结印_引灵指.png", "yinjianjue-1.png"),
        (2, 256, 44, 513, 285, 381.0, 282.0, "02_遥召_破空鸣.png", "yinjianjue-2.png"),
        (3, 513, 44, 770, 285, 647.5, 279.0, "03_牵引_流光穿.png", "yinjianjue-3.png"),
        (4, 770, 44, 1024, 285, 896.5, 282.0, "04_候刃_展臂迎.png", "yinjianjue-4.png"),
        (5, 0, 330, 256, 568, 122.0, 563.0, "05_握柄_雷爆定.png", "yinjianjue-5.png"),
        (6, 256, 333, 512, 568, 386.0, 562.0, "06_旋腕_剑花破.png", "yinjianjue-6.png"),
        (7, 512, 333, 768, 568, 642.5, 565.0, "07_拂袖_振刃鸣.png", "yinjianjue-7.png"),
        (8, 768, 313, 1024, 568, 909.0, 565.0, "08_敛息_垂剑立.png", "yinjianjue-8.png"),
    ]

    # Reference standing height from F8: top Y=313 to foot Y=565 = 253px
    standing_h_raw = 565.0 - 313.0 + 1.0  # 253.0
    scale_factor = TARGET_STAND_H / standing_h_raw
    print(f"Standing height raw: {standing_h_raw}px -> Scale factor: {scale_factor:.6f}")

    processed_frames = []

    for f_num, x0, y0, x1, y1, stance_cx, foot_y, cname, std_name in frames_meta:
        cell_crop = sheet_img.crop((x0, y0, x1, y1))
        cleaned_cell = clean_cell_magenta(cell_crop)

        # Scale proportionally
        orig_w, orig_h = cleaned_cell.size
        new_w = int(round(orig_w * scale_factor))
        new_h = int(round(orig_h * scale_factor))
        scaled_cell = cleaned_cell.resize((new_w, new_h), Image.LANCZOS)

        # Align on target canvas 680x480
        canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))

        # Position foot baseline to Y=437
        foot_offset_in_crop = foot_y - y0
        scaled_foot_y = foot_offset_in_crop * scale_factor
        dest_y = int(round(TARGET_FEET_Y - scaled_foot_y))

        # Position stance center to X=340
        cx_offset_in_crop = stance_cx - x0
        scaled_cx = cx_offset_in_crop * scale_factor
        dest_x = int(round(CENTER_X - scaled_cx))

        canvas.paste(scaled_cell, (dest_x, dest_y), scaled_cell)
        processed_frames.append((f_num, cname, std_name, canvas))

        # Save single transparent PNGs
        # 1. In design folder (Chinese named)
        canvas.save(os.path.join(DIR_DESIGN_SKILL, cname))
        canvas.save(os.path.join(DIR_DESIGN_CLEAN, cname))
        # 2. In design folder (Standard named)
        canvas.save(os.path.join(DIR_DESIGN_SKILL, std_name))
        canvas.save(os.path.join(DIR_DESIGN_CLEAN, std_name))
        # 3. In Unity folder
        unity_png_path = os.path.join(DIR_UNITY_SKILL, std_name)
        canvas.save(unity_png_path)
        create_unity_meta(unity_png_path, is_sprite=True)

        print(f"Processed F{f_num}: {std_name} ({cname}) - placed at ({dest_x}, {dest_y})")

    # Sequence Strip: 8 * 680 = 5440 x 480
    strip = Image.new("RGBA", (CANVAS_W * 8, CANVAS_H), (0, 0, 0, 0))
    for i, (_, _, _, fr) in enumerate(processed_frames):
        strip.paste(fr, (i * CANVAS_W, 0))

    strip_design_path = os.path.join(DIR_DESIGN_SKILL, "yinjianjue-sequence.png")
    strip_clean_path = os.path.join(DIR_DESIGN_CLEAN, "yinjianjue-sequence.png")
    strip_unity_path = os.path.join(DIR_UNITY_SKILL, "yinjianjue-sequence.png")

    strip.save(strip_design_path)
    strip.save(strip_clean_path)
    strip.save(strip_unity_path)
    create_unity_meta(strip_unity_path, is_sprite=True)
    print("Saved sequence strip: 5440x480")

    # Dark background preview strip
    dark_bg = Image.new("RGBA", (CANVAS_W * 8, CANVAS_H), (20, 24, 32, 255))
    dark_preview = Image.alpha_composite(dark_bg, strip)
    dark_preview.save(os.path.join(DIR_DESIGN_SKILL, "yinjianjue-darkbg-preview.png"))
    dark_preview.save(os.path.join(DIR_DESIGN_CLEAN, "yinjianjue-darkbg-preview.png"))
    print("Saved darkbg preview strip")

    # Animated GIF with mediancut palette protection
    durations = [120, 120, 140, 100, 180, 120, 120, 160]
    gif_design_path = os.path.join(DIR_DESIGN_SKILL, "yinjianjue-animation.gif")
    gif_unity_path = os.path.join(DIR_UNITY_SKILL, "yinjianjue-animation.gif")

    generate_gif(processed_frames, durations, gif_design_path)
    shutil.copyfile(gif_design_path, gif_unity_path)
    create_unity_meta(gif_unity_path, is_sprite=False)

    # Copy raw sheet into Unity
    unity_raw_sheet = os.path.join(DIR_UNITY_SKILL, "yinjianjue_raw_sheet.jpg")
    shutil.copyfile(SRC_IMAGE, unity_raw_sheet)
    create_unity_meta(unity_raw_sheet, is_sprite=False)

    print("=== All Yinjianjue assets successfully generated and synced! ===")


if __name__ == "__main__":
    main()
