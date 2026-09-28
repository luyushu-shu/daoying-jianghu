#!/usr/bin/env python3
"""
Process Qingfeng Swordsman Skill 5: 以剑御气 · 苍龙玄天钟 (Kinetic Aegis / Azure Dragon Bell · QF-5)
16-Frame 4x4 Grid Pipeline:
1. Solid Magenta (#FF00FF) Chroma-key with Despill, Edge Feathering, and Protection Rules.
2. Standard Standing Height Scaling to 328px.
3. Foot baseline strictly locked to Y=437 on standard 680x480 canvas (PPU 214, Pivot (0.5, 0.09)).
4. Centering on X=340 with stance compensation.
5. Export 16 individual transparent PNGs, 10880x480 sequence strip, dark preview strip, and 255-color mediancut GIF.
6. Copy concept art and raw sheet to permanent design directories.
7. Integrate into Unity directory with native .meta files.
"""

import os
import shutil
import hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import label

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_NORMAL_IMAGE = r"C:/Users/luyus/.gemini/antigravity/brain/f6c7a99b-91e5-4d92-b89d-be1b8bf529c3/.user_uploaded/media_1790582424613.jpg"
SRC_CONCEPT_IMAGE = r"C:/Users/luyus/.gemini/antigravity/brain/f6c7a99b-91e5-4d92-b89d-be1b8bf529c3/.user_uploaded/media_1790582690257.jpg"

DIR_DESIGN_SKILL = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "05_以剑御气")
DIR_DESIGN_CLEAN = os.path.join(DIR_DESIGN_SKILL, "pure_clean_sprites")
DIR_UNITY_SKILL = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Yijianyuqi")

for d in [DIR_DESIGN_SKILL, DIR_DESIGN_CLEAN, DIR_UNITY_SKILL]:
    os.makedirs(d, exist_ok=True)

# Copy source assets
shutil.copyfile(SRC_NORMAL_IMAGE, os.path.join(DIR_DESIGN_SKILL, "yijianyuqi_normal_raw_sheet.jpg"))
shutil.copyfile(SRC_NORMAL_IMAGE, os.path.join(DIR_UNITY_SKILL, "yijianyuqi_normal_raw_sheet.jpg"))
shutil.copyfile(SRC_CONCEPT_IMAGE, os.path.join(DIR_DESIGN_SKILL, "以剑御气-剑意绽放-电影级特效全案设定图.jpg"))
shutil.copyfile(SRC_CONCEPT_IMAGE, os.path.join(DIR_UNITY_SKILL, "以剑御气-剑意绽放-电影级特效全案设定图.jpg"))

CANVAS_W = 680
CANVAS_H = 480
TARGET_STAND_H = 328.0
RAW_STAND_H = 236.0
SCALE = TARGET_STAND_H / RAW_STAND_H  # ~1.38983
TARGET_FEET_Y = 437
CENTER_X = 340

FRAMES_CONFIG = [
    (1, "01_起势_沉步引龙", "yijianyuqi-1", (0, 0, 256, 256), 251, 127),
    (2, "02_立桩_按剑横胸", "yijianyuqi-2", (256, 0, 512, 256), 249, 130),
    (3, "03_聚气_苍龙盘虚", "yijianyuqi-3", (512, 0, 768, 256), 249, 125),
    (4, "04_凝界_双龙合钟", "yijianyuqi-4", (768, 0, 1024, 256), 249, 129),
    (5, "05_定界_琉璃晶壁", "yijianyuqi-5", (0, 256, 256, 512), 250, 140),
    (6, "06_固守_刃芒流转", "yijianyuqi-6", (256, 256, 512, 512), 249, 140),
    (7, "07_脉动_八卦金印", "yijianyuqi-7", (512, 256, 768, 512), 249, 142),
    (8, "08_触界_星芒微爆", "yijianyuqi-8", (768, 256, 1024, 512), 248, 135),
    (9, "09_顿挫_墨痕裂钟", "yijianyuqi-9", (0, 512, 256, 768), 250, 142),
    (10, "10_反震_暴烈推刃", "yijianyuqi-10", (256, 512, 512, 768), 248, 148),
    (11, "11_激波_龙吟破壁", "yijianyuqi-11", (512, 512, 768, 768), 250, 125),
    (12, "12_碎晶_漫天琉璃", "yijianyuqi-12", (768, 512, 1024, 768), 249, 124),
    (13, "13_直身_星尘飞瀑", "yijianyuqi-13", (0, 768, 256, 1024), 253, 126),
    (14, "14_挽花_狂草残月", "yijianyuqi-14", (256, 768, 512, 1024), 250, 138),
    (15, "15_拂刃_龙吟振雪", "yijianyuqi-15", (512, 768, 768, 1024), 250, 129),
    (16, "16_归立_敛息入道", "yijianyuqi-16", (768, 768, 1024, 1024), 252, 124),
]


def clean_cell_magenta(crop_img):
    arr = np.array(crop_img, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    
    dist = np.sqrt((r - 254.0)**2 + (g - 1.0)**2 + (b - 250.0)**2)
    mag_dominance = np.minimum(r, b) - g
    
    # Protection rules
    is_white = (r > 175.0) & (g > 175.0) & (b > 175.0)
    is_gold = (r > 135.0) & (g > 115.0) & (b < 185.0) & (r > b + 15.0)
    is_cyan = (g > 70.0) & (b > 85.0) & (g > r - 20.0)
    is_frost = (b > 150.0) & (g > 135.0) & (r < 215.0)
    is_skin = (r > 130.0) & (g > 85.0) & (b > 65.0) & ((r - g) < 80.0) & (g > b - 20.0) & (mag_dominance < 30.0)
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
    
    # Boundary feathering (4 outer edge pixels) to eliminate square border artifacts
    for i in range(4):
        factor = i / 4.0
        alpha[i, :] *= factor
        alpha[-1-i, :] *= factor
        alpha[:, i] *= factor
        alpha[:, -1-i] *= factor
        
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
    for fr, dur in zip(processed_frames, frame_durations):
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
    hasher = hashlib.md5()
    hasher.update(os.path.relpath(filepath, PROJECT_ROOT).replace("\\", "/").encode("utf-8"))
    guid = hasher.hexdigest()
    
    if is_sprite:
        meta_content = f"""fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 12
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
    sheet_img = Image.open(SRC_NORMAL_IMAGE).convert("RGB")
    W, H = sheet_img.size
    print(f"Loaded sheet: {SRC_NORMAL_IMAGE} ({W}x{H})")
    
    processed_canvas_frames = []
    
    for idx, cname, std_name, crop_box, feet_y_raw, center_x_raw in FRAMES_CONFIG:
        cell_raw = sheet_img.crop(crop_box)
        cell_clean = clean_cell_magenta(cell_raw)
        
        # Scale to standard standing height
        w_scaled = int(round(256 * SCALE))
        h_scaled = int(round(256 * SCALE))
        cell_scaled = cell_clean.resize((w_scaled, h_scaled), Image.LANCZOS)
        
        # Canvas placement: align feet to TARGET_FEET_Y (437), center_x to CENTER_X (340)
        paste_x = int(round(CENTER_X - (center_x_raw * SCALE)))
        paste_y = int(round(TARGET_FEET_Y - (feet_y_raw * SCALE)))
        
        canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        canvas.paste(cell_scaled, (paste_x, paste_y), cell_scaled)
        
        # Save individual PNGs
        p_cname = os.path.join(DIR_DESIGN_CLEAN, f"{cname}.png")
        p_std_design = os.path.join(DIR_DESIGN_SKILL, f"{std_name}.png")
        p_std_unity = os.path.join(DIR_UNITY_SKILL, f"{std_name}.png")
        
        canvas.save(p_cname)
        canvas.save(p_std_design)
        canvas.save(p_std_unity)
        create_unity_meta(p_std_unity, is_sprite=True)
        
        processed_canvas_frames.append(canvas)
        print(f"Processed Frame {idx:02d}: {cname} -> {std_name}.png")

    # Generate sequence strip (16 frames * 680 = 10880 x 480)
    total_w = CANVAS_W * len(processed_canvas_frames)
    strip = Image.new("RGBA", (total_w, CANVAS_H), (0, 0, 0, 0))
    for i, fr in enumerate(processed_canvas_frames):
        strip.paste(fr, (i * CANVAS_W, 0), fr)
        
    p_strip_design = os.path.join(DIR_DESIGN_SKILL, "yijianyuqi-sequence.png")
    p_strip_clean = os.path.join(DIR_DESIGN_CLEAN, "yijianyuqi-sequence.png")
    p_strip_unity = os.path.join(DIR_UNITY_SKILL, "yijianyuqi-sequence.png")
    strip.save(p_strip_design)
    strip.save(p_strip_clean)
    strip.save(p_strip_unity)
    create_unity_meta(p_strip_unity, is_sprite=True)
    print(f"Exported sequence strip: {p_strip_design} ({total_w}x{CANVAS_H})")
    
    # Generate dark preview strip
    dark_bg = Image.new("RGB", (total_w, CANVAS_H), (15, 20, 25))
    dark_bg.paste(strip, (0, 0), strip)
    dark_bg.save(os.path.join(DIR_DESIGN_SKILL, "yijianyuqi-darkbg-preview.png"))
    dark_bg.save(os.path.join(DIR_UNITY_SKILL, "yijianyuqi-darkbg-preview.png"))
    create_unity_meta(os.path.join(DIR_UNITY_SKILL, "yijianyuqi-darkbg-preview.png"), is_sprite=False)
    
    # Generate GIF (timing optimized for 16-frame action rhythm)
    durations = [
        60, 60, 60, 60,   # F1-F4: Startup (0.24s)
        70, 70, 70, 70,   # F5-F8: Guard & Pulses (0.28s)
        100, 70, 80, 90,  # F9-F12: Hitstop (100ms) & Shockwave & Shatter (0.34s)
        70, 90, 80, 120   # F13-F16: Flourish, Flick, Settle Idle (0.36s)
    ]
    gif_design = os.path.join(DIR_DESIGN_SKILL, "yijianyuqi-animation.gif")
    gif_unity = os.path.join(DIR_UNITY_SKILL, "yijianyuqi-animation.gif")
    generate_gif(processed_canvas_frames, durations, gif_design)
    shutil.copyfile(gif_design, gif_unity)
    create_unity_meta(gif_unity, is_sprite=False)
    
    # Also update legacy sequence-strip.png and animation.gif in DIR_DESIGN_SKILL
    shutil.copyfile(p_strip_design, os.path.join(DIR_DESIGN_SKILL, "sequence-strip.png"))
    shutil.copyfile(gif_design, os.path.join(DIR_DESIGN_SKILL, "animation.gif"))
    print("Normal Form (QF-5) Processing Complete!")


if __name__ == "__main__":
    main()
