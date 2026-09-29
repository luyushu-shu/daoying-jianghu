#!/usr/bin/env python3
"""
Process Qingfeng Swordsman Skill 6: 万剑归宗 (Ten Thousand Swords Return to Origin · QF-6 & QF-6E)
Processes:
1. Image 1: 万剑归宗 · 常态版 (QF-6) 4x4 Grid Sheet -> 16 transparent PNGs, 10880x480 sequence strip, dark preview, 255-color GIF.
2. Image 2: 万剑归宗 · 剑意绽放版 (QF-6E) 4x4 Grid Sheet -> 16 transparent PNGs, 10880x480 sequence strip, dark preview, 255-color GIF.
3. Image 3: 万剑归宗 · 电影级特效全案设定图 (Cinematic Concept Key Visual).
4. Image 4: 全屏落剑特效源图 · 常态青锋剑 (Sword Projectile & Weapon Splash · Normal).
5. Image 5: 全屏落剑特效源图 · 剑意绽放青锋神剑 (Sword Projectile & Weapon Splash · Bloom).
6. Generates valid Unity native .meta files and syncs to both 设计 and New Tuanjie Project directories.
"""

import os
import shutil
import hashlib
import numpy as np
from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SRC_NORMAL_4X4 = r"C:/Users/luyus/.gemini/antigravity/brain/6586bf7c-a2d8-4d8e-ae66-c6d91b7224a7/.user_uploaded/media_1790670325313.jpg"
SRC_BLOOM_4X4 = r"C:/Users/luyus/.gemini/antigravity/brain/6586bf7c-a2d8-4d8e-ae66-c6d91b7224a7/.user_uploaded/media_1790670349257.jpg"
SRC_CINEMATIC = r"C:/Users/luyus/.gemini/antigravity/brain/6586bf7c-a2d8-4d8e-ae66-c6d91b7224a7/.user_uploaded/media_1790670374555.jpg"
SRC_SWORD_NORMAL = r"C:/Users/luyus/.gemini/antigravity/brain/6586bf7c-a2d8-4d8e-ae66-c6d91b7224a7/.user_uploaded/media_1790670417415.png"
SRC_SWORD_BLOOM = r"C:/Users/luyus/.gemini/antigravity/brain/6586bf7c-a2d8-4d8e-ae66-c6d91b7224a7/.user_uploaded/media_1790670426187.jpg"

# Output directories
DIR_DESIGN_ROOT = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "06_万剑归宗")
DIR_NORMAL_DESIGN = os.path.join(DIR_DESIGN_ROOT, "常态_万剑归宗")
DIR_NORMAL_CLEAN = os.path.join(DIR_NORMAL_DESIGN, "pure_clean_sprites")
DIR_NORMAL_UNITY = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Wanjian")

DIR_BLOOM_DESIGN = os.path.join(DIR_DESIGN_ROOT, "强化版_万剑归宗_极")
DIR_BLOOM_CLEAN = os.path.join(DIR_BLOOM_DESIGN, "pure_clean_sprites")
DIR_BLOOM_UNITY = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Wanjian_Bloom")

DIR_PROJECTILES = os.path.join(DIR_DESIGN_ROOT, "全屏落剑特效源与武器立绘")

for d in [DIR_DESIGN_ROOT, DIR_NORMAL_DESIGN, DIR_NORMAL_CLEAN, DIR_NORMAL_UNITY,
          DIR_BLOOM_DESIGN, DIR_BLOOM_CLEAN, DIR_BLOOM_UNITY, DIR_PROJECTILES]:
    os.makedirs(d, exist_ok=True)

# Canvas & Physical parameters
CANVAS_W = 680
CANVAS_H = 480
TARGET_STAND_H = 328.0
RAW_STAND_H = 201.0
SCALE = TARGET_STAND_H / RAW_STAND_H  # ~1.63184
TARGET_FEET_Y = 437
CENTER_X = 340


def clean_cell_magenta(crop_img):
    """
    High-precision Chroma-key for 100% solid magenta (#FF00FF).
    Protects cyan, gold, white-hot cores, skin, black ink, and ice crystals.
    Removes edge border pixels cleanly.
    """
    arr = np.array(crop_img, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    
    # Distance to pure magenta (255, 0, 255)
    dist = np.sqrt((r - 255.0)**2 + (g - 0.0)**2 + (b - 255.0)**2)
    mag_dominance = np.minimum(r, b) - g
    
    # Protection rules
    is_white = (r > 175.0) & (g > 175.0) & (b > 175.0)
    is_gold = (r > 140.0) & (g > 115.0) & (b < 190.0) & (r > b + 15.0)
    is_cyan = (g > 70.0) & (b > 85.0) & (g > r - 25.0)
    is_frost = (b > 150.0) & (g > 135.0) & (r < 215.0)
    is_skin = (r > 130.0) & (g > 85.0) & (b > 65.0) & ((r - g) < 80.0) & (g > b - 20.0) & (mag_dominance < 30.0)
    is_dark = (r < 65.0) & (g < 65.0) & (b < 65.0)
    
    is_protected = is_white | is_cyan | is_skin | is_dark | is_gold | is_frost
    
    # Background detection
    is_bg = (dist < 130.0) | ((mag_dominance > 35.0) & (g < 140.0) & (dist < 190.0))
    is_bg = is_bg & (~is_protected)
    
    # Alpha falloff
    alpha = np.clip((dist - 45.0) / 75.0, 0.0, 1.0)
    alpha[is_bg] = 0.0
    alpha[mag_dominance > 75.0] = 0.0
    alpha[is_protected] = 1.0
    
    # Boundary cleanup: zero out 2 outer edge pixels to avoid any black border lines
    alpha[0:3, :] = 0.0
    alpha[-3:, :] = 0.0
    alpha[:, 0:3] = 0.0
    alpha[:, -3:] = 0.0
    
    # Edge feathering (pixels 3 to 6)
    for i in range(3, 7):
        factor = (i - 2) / 5.0
        alpha[i, :] *= factor
        alpha[-1-i, :] *= factor
        alpha[:, i] *= factor
        alpha[:, -1-i] *= factor
        
    out = arr.copy()
    # Despill: replace magenta tinted halo with neutral dark / cyan
    magenta_tint = (mag_dominance > 20.0) & (~is_protected)
    out[magenta_tint, 0] = np.minimum(out[magenta_tint, 0], out[magenta_tint, 1] + 20.0)
    out[magenta_tint, 2] = np.minimum(out[magenta_tint, 2], out[magenta_tint, 1] + 20.0)
    
    rgba = np.dstack([out.astype(np.uint8), (alpha * 255.0).astype(np.uint8)])
    return Image.fromarray(rgba, 'RGBA')


def generate_gif(frames, frame_durations, gif_output_path):
    """
    Generate crisp, transparent GIF with 255-color mediancut palette and alpha transparency.
    """
    gif_frames = []
    for fr, dur in zip(frames, frame_durations):
        clean_rgba = fr.copy()
        arr = np.array(clean_rgba)
        trans_mask = arr[..., 3] < 30
        
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
    mipMapsPreservesCoverage: 0
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
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 4096
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
  spritePivot: {{x: 0.5, y: 0.08958333}}
  spritePixelsToUnits: 214
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 1
  alphaIsTransparency: 1
  spriteChildren: []
  alphaSource: 1
  platformSettings: []
  tierSettings: []
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


def process_4x4_sheet(src_path, prefix, design_dir, clean_dir, unity_dir):
    im = Image.open(src_path)
    w, h = im.size
    cell_w = w // 4  # 256
    cell_h = h // 4  # 256
    
    processed_frames = []
    
    # We crop inner [3:253, 3:253] for each 256x256 cell (width 250, height 250)
    for idx in range(16):
        r = idx // 4
        c = idx % 4
        x0 = c * cell_w + 3
        y0 = r * cell_h + 3
        x1 = (c + 1) * cell_w - 3
        y1 = (r + 1) * cell_h - 3
        
        cell_raw = im.crop((x0, y0, x1, y1))
        cell_clean = clean_cell_magenta(cell_raw)
        
        # Scale to standard standing height
        w_scaled = int(round(cell_clean.width * SCALE))
        h_scaled = int(round(cell_clean.height * SCALE))
        cell_scaled = cell_clean.resize((w_scaled, h_scaled), Image.LANCZOS)
        
        # Anchor alignment:
        # Inner cell center is at (122), standing feet is at 232
        feet_y_raw = 232.0
        center_x_raw = 122.0
        
        paste_x = int(round(CENTER_X - (center_x_raw * SCALE)))
        paste_y = int(round(TARGET_FEET_Y - (feet_y_raw * SCALE)))
        
        canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        canvas.paste(cell_scaled, (paste_x, paste_y), cell_scaled)
        
        std_name = f"{prefix}-{idx+1}"
        p_clean = os.path.join(clean_dir, f"{std_name}.png")
        p_design = os.path.join(design_dir, f"{std_name}.png")
        p_unity = os.path.join(unity_dir, f"{std_name}.png")
        
        canvas.save(p_clean)
        canvas.save(p_design)
        canvas.save(p_unity)
        create_unity_meta(p_unity, is_sprite=True)
        
        processed_frames.append(canvas)
        print(f"[{prefix}] Processed Frame {idx+1:02d}: {std_name}.png")
        
    # Sequence Strip (16 * 680 = 10880 x 480)
    total_w = CANVAS_W * len(processed_frames)
    strip = Image.new("RGBA", (total_w, CANVAS_H), (0, 0, 0, 0))
    for i, fr in enumerate(processed_frames):
        strip.paste(fr, (i * CANVAS_W, 0), fr)
        
    p_strip_design = os.path.join(design_dir, f"{prefix}-sequence.png")
    p_strip_clean = os.path.join(clean_dir, f"{prefix}-sequence.png")
    p_strip_unity = os.path.join(unity_dir, f"{prefix}-sequence.png")
    strip.save(p_strip_design)
    strip.save(p_strip_clean)
    strip.save(p_strip_unity)
    create_unity_meta(p_strip_unity, is_sprite=True)
    
    # Dark Preview Strip
    dark_bg = Image.new("RGB", (total_w, CANVAS_H), (15, 20, 25))
    dark_bg.paste(strip, (0, 0), strip)
    dark_bg.save(os.path.join(design_dir, f"{prefix}-darkbg-preview.png"))
    dark_bg.save(os.path.join(unity_dir, f"{prefix}-darkbg-preview.png"))
    create_unity_meta(os.path.join(unity_dir, f"{prefix}-darkbg-preview.png"), is_sprite=False)
    
    # Timing for 16-frame ultimate:
    # F1-F4: Startup (4 * 70ms = 280ms)
    # F5-F8: Downward Barrage (4 * 60ms = 240ms)
    # F9-F12: Black Hole & Supernova (100ms, 90ms, 120ms, 80ms = 390ms)
    # F13-F16: Stardust Settle (70ms, 80ms, 90ms, 140ms = 380ms)
    durations = [70, 70, 70, 70, 60, 60, 60, 60, 100, 90, 120, 80, 70, 80, 90, 140]
    gif_design = os.path.join(design_dir, f"{prefix}-animation.gif")
    gif_unity = os.path.join(unity_dir, f"{prefix}-animation.gif")
    generate_gif(processed_frames, durations, gif_design)
    shutil.copyfile(gif_design, gif_unity)
    create_unity_meta(gif_unity, is_sprite=False)
    
    return strip, gif_design


def main():
    print("=== Starting 刀影江湖 · 万剑归宗 全套资产自动化处理 ===")
    
    # 1. Archive raw source sheets into design & unity folders
    shutil.copyfile(SRC_NORMAL_4X4, os.path.join(DIR_NORMAL_DESIGN, "wanjian_normal_raw_sheet.jpg"))
    shutil.copyfile(SRC_NORMAL_4X4, os.path.join(DIR_NORMAL_UNITY, "wanjian_normal_raw_sheet.jpg"))
    create_unity_meta(os.path.join(DIR_NORMAL_UNITY, "wanjian_normal_raw_sheet.jpg"), is_sprite=False)
    
    shutil.copyfile(SRC_BLOOM_4X4, os.path.join(DIR_BLOOM_DESIGN, "wanjian_bloom_raw_sheet.jpg"))
    shutil.copyfile(SRC_BLOOM_4X4, os.path.join(DIR_BLOOM_UNITY, "wanjian_bloom_raw_sheet.jpg"))
    create_unity_meta(os.path.join(DIR_BLOOM_UNITY, "wanjian_bloom_raw_sheet.jpg"), is_sprite=False)
    
    # 2. Archive Cinematic Concept Art (Image 3)
    p_cin_design = os.path.join(DIR_DESIGN_ROOT, "万剑归宗-电影级特效全案设定图.jpg")
    p_cin_unity1 = os.path.join(DIR_NORMAL_UNITY, "万剑归宗-电影级特效全案设定图.jpg")
    p_cin_unity2 = os.path.join(DIR_BLOOM_UNITY, "万剑归宗-电影级特效全案设定图.jpg")
    shutil.copyfile(SRC_CINEMATIC, p_cin_design)
    shutil.copyfile(SRC_CINEMATIC, p_cin_unity1)
    shutil.copyfile(SRC_CINEMATIC, p_cin_unity2)
    create_unity_meta(p_cin_unity1, is_sprite=False)
    create_unity_meta(p_cin_unity2, is_sprite=False)
    print("Archived Image 3: 电影级特效全案设定图")
    
    # 3. Archive Falling Sword Projectiles & Weapon Splash (Image 4 & Image 5)
    shutil.copyfile(SRC_SWORD_NORMAL, os.path.join(DIR_PROJECTILES, "青锋剑_常态_全屏落剑特效源.png"))
    shutil.copyfile(SRC_SWORD_NORMAL, os.path.join(DIR_NORMAL_UNITY, "sword_projectile_normal.png"))
    create_unity_meta(os.path.join(DIR_NORMAL_UNITY, "sword_projectile_normal.png"), is_sprite=True)
    
    shutil.copyfile(SRC_SWORD_BLOOM, os.path.join(DIR_PROJECTILES, "青锋剑_剑意绽放_全屏落剑特效源.jpg"))
    shutil.copyfile(SRC_SWORD_BLOOM, os.path.join(DIR_BLOOM_UNITY, "sword_projectile_bloom.jpg"))
    create_unity_meta(os.path.join(DIR_BLOOM_UNITY, "sword_projectile_bloom.jpg"), is_sprite=True)
    print("Archived Images 4 & 5: 全屏落剑特效源与武器立绘")
    
    # 4. Process Normal Form (Image 1)
    print("--- Processing 万剑归宗 · 常态版 (QF-6) ---")
    strip_n, gif_n = process_4x4_sheet(SRC_NORMAL_4X4, "wanjian", DIR_NORMAL_DESIGN, DIR_NORMAL_CLEAN, DIR_NORMAL_UNITY)
    # Also update legacy sequence and animation in DIR_DESIGN_ROOT
    shutil.copyfile(os.path.join(DIR_NORMAL_DESIGN, "wanjian-sequence.png"), os.path.join(DIR_DESIGN_ROOT, "sequence-strip.png"))
    shutil.copyfile(gif_n, os.path.join(DIR_DESIGN_ROOT, "animation.gif"))
    
    # 5. Process Bloom Form (Image 2)
    print("--- Processing 万剑归宗 · 剑意绽放强化版 (QF-6E) ---")
    strip_b, gif_b = process_4x4_sheet(SRC_BLOOM_4X4, "wanjian-bloom", DIR_BLOOM_DESIGN, DIR_BLOOM_CLEAN, DIR_BLOOM_UNITY)
    shutil.copyfile(os.path.join(DIR_BLOOM_DESIGN, "wanjian-bloom-sequence.png"), os.path.join(DIR_DESIGN_ROOT, "wanjian-bloom-sequence.png"))
    shutil.copyfile(gif_b, os.path.join(DIR_DESIGN_ROOT, "wanjian-bloom-animation.gif"))
    
    print("=== 所有万剑归宗资产切片、对齐、GIF 及 Unity 资源同步完毕！ ===")


if __name__ == "__main__":
    main()
