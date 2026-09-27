#!/usr/bin/env python3
"""
Process Qingfeng Swordsman Skill 3: 一剑霜寒·剑意绽放强化版 (Absolute Frost · Glacial Peak Surge, QF-3E)
Directly postprocesses the user's master sprite sheet:
media_1790508962375.jpg

Features:
- Solid Magenta (#FF00FF) Chroma-key with Despill and Alpha Feathering.
- Intelligent separation of all 8 frames:
  1. 结势 · 霜降领域 (Qingfeng in horse stance, glowing circular ice magic circle with frost glyphs under feet)
  2. 提剑 · 千霜汇刃 (Raising sword with both hands, massive crystalline ice shards and double-layer ice vortex)
  3. 蓄力 · 镇岳极寒 (Planting sword into earth, massive crystalline ice spikes bursting out radially)
  4. 斩出 · 天幕惊芒 (Explosive wide horizontal slash, huge sweeping crescent ice blade cutting through the air)
  5. 前刺 · 冰峰破地 (Deep forward lunge, thrusting sword forward, a colossal wall of 2-meter sharp azure ice peaks)
  6. 冰封 · 绝对霜冻 (Forward stance, pointing sword, ground frozen glacial ice, enemies encased inside ice pillars)
  7. 振刃 · 碎峰万晶 (Flicking hand, ice peaks and crystals shattering into a storm of hundreds of diamond ice shards)
  8. 敛意 · 雪霁风宁 (Graceful sheath posture, upright standing, falling white snowflakes drifting gently down)
- Uniform Proportional Scaling (Standing Height = 328px, matching Idle/Run/Attack/Pokongci/Huifengwu).
- Foot baseline locked to Y=437 on 680x480 canvas (PPU 214, Pivot 0.5, 0.09).
- Exports individual transparent PNGs, 5440x480 sequence strip, dark bg preview, and transparent looping GIF.
- Synchronizes assets into Unity directory and creates valid native .meta files.
"""

import os
import shutil
import uuid
import numpy as np
from PIL import Image
from scipy.ndimage import label

RAW_SOURCE = r"C:/Users/luyus/.gemini/antigravity/brain/7ae82753-faef-4cb8-8f99-31cd12839d86/.user_uploaded/media_1790508962375.jpg"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "03_一剑霜寒", "强化版_冰魄玄峰")
UNITY_DIR = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Yijianshuanghan_Bloom")
CLEAN_DIR = os.path.join(SKILL_DIR, "pure_clean_sprites")
GEN_DIR = os.path.join(SKILL_DIR, "generated_sheet")

for d in [SKILL_DIR, UNITY_DIR, CLEAN_DIR, GEN_DIR]:
    os.makedirs(d, exist_ok=True)

# Archive raw sheet
shutil.copyfile(RAW_SOURCE, os.path.join(GEN_DIR, "raw-sheet.jpg"))

CANVAS_W = 680
CANVAS_H = 480
TARGET_STAND_H = 328.0
RAW_STAND_H = 272.0  # Measured from Frame 8 upright standing stance
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
    
    # Precise boundaries
    # Row 1 (y: 0..335)
    # Row 2 (y: 340..682)
    frames_config = [
        (1, "01_结势_霜降领域", "yijianshuanghan-bloom-1", (0, 0, 265, 335), None),
        (2, "02_提剑_千霜汇刃", "yijianshuanghan-bloom-2", (265, 0, 506, 335), "mask_f2"),
        (3, "03_蓄力_镇岳极寒", "yijianshuanghan-bloom-3", (495, 0, 748, 335), "mask_f3"),
        (4, "04_斩出_天幕惊芒", "yijianshuanghan-bloom-4", (745, 0, 1024, 335), "mask_f4"),
        (5, "05_前刺_冰峰破地", "yijianshuanghan-bloom-5", (0, 340, 258, 682), None),
        (6, "06_冰封_绝对霜冻", "yijianshuanghan-bloom-6", (258, 340, 544, 682), None),
        (7, "07_振刃_碎峰万晶", "yijianshuanghan-bloom-7", (544, 340, 770, 682), None),
        (8, "08_敛意_雪霁风宁", "yijianshuanghan-bloom-8", (770, 340, 1024, 682), None),
    ]
    
    processed_frames = []
    
    for idx, cname, std_name, box, special_mask in frames_config:
        print(f"Processing Bloom Frame {idx}: {cname}...")
        cell = raw_sheet.crop(box)
        
        # Apply special inter-cell separation if needed
        if special_mask == "mask_f2":
            # Mask out F3 lower-left ground ice spike: (x in cell > 495 - 265 = 230, y > 200)
            arr_cell = np.array(cell)
            for y in range(200, cell.height):
                for x in range(230, cell.width):
                    arr_cell[y, x] = [255, 0, 255]
            cell = Image.fromarray(arr_cell)
            
        elif special_mask == "mask_f3":
            # Mask out F2 sword tip: (x in cell < 506 - 495 = 11, y < 200)
            arr_cell = np.array(cell)
            for y in range(min(200, cell.height)):
                for x in range(min(11, cell.width)):
                    arr_cell[y, x] = [255, 0, 255]
            # Mask out F4 sleeve: (x in cell > 745 - 495 = 250, y < 200)
            for y in range(min(200, cell.height)):
                for x in range(250, cell.width):
                    arr_cell[y, x] = [255, 0, 255]
            cell = Image.fromarray(arr_cell)
            
        elif special_mask == "mask_f4":
            # Mask out F3 ground ice tip: (x in cell < 748 - 745 = 3, y > 200)
            arr_cell = np.array(cell)
            for y in range(200, cell.height):
                for x in range(min(3, cell.width)):
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
            # Baseline calibration per frame:
            if idx == 1:
                # F1 has magic circle extending ~5px below feet
                feet_y_local = int(round(ys.max() - 5 * SCALE_FACTOR))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 3:
                # F3 ground ice burst extends ~8px below feet
                feet_y_local = int(round(ys.max() - 6 * SCALE_FACTOR))
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
            elif idx == 6:
                # F6 ground frozen decal extends ~15px below feet
                feet_y_local = int(round(ys.max() - 15 * SCALE_FACTOR))
                # Center character (character is on the left half, ice pillars on right)
                # Keep character positioned near center-left
                body_center_x_local = int(round((xs.min() + xs.max()) * 0.45))
            elif idx == 5:
                # F5 massive forward lunge with ice peaks on right
                feet_y_local = ys.max()
                body_center_x_local = int(round((xs.min() + xs.max()) * 0.44))
            elif idx == 4:
                # F4 wide slash arc on right
                feet_y_local = ys.max()
                body_center_x_local = int(round((xs.min() + xs.max()) * 0.46))
            else:
                feet_y_local = ys.max()
                body_center_x_local = int(round((xs.min() + xs.max()) / 2.0))
                
            paste_x = CENTER_X - body_center_x_local
            paste_y = TARGET_FEET_Y - feet_y_local
            
            final_canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
            final_canvas.paste(scaled, (paste_x, paste_y), scaled)
            
        processed_frames.append((idx, cname, std_name, final_canvas))
        
        # Save individual PNGs
        final_canvas.save(os.path.join(SKILL_DIR, f"{cname}.png"))
        final_canvas.save(os.path.join(SKILL_DIR, f"{std_name}.png"))
        final_canvas.save(os.path.join(CLEAN_DIR, f"{cname}.png"))
        final_canvas.save(os.path.join(CLEAN_DIR, f"{std_name}.png"))
        final_canvas.save(os.path.join(UNITY_DIR, f"{std_name}.png"))

    print(f"Saved 8 clean frames to {UNITY_DIR} and {SKILL_DIR}")
    
    # 5440x480 Sequence Strip
    strip = Image.new('RGBA', (CANVAS_W * 8, CANVAS_H), (0, 0, 0, 0))
    for idx, (f_num, cname, std_name, fr) in enumerate(processed_frames):
        strip.paste(fr, (idx * CANVAS_W, 0), fr)
        
    strip.save(os.path.join(UNITY_DIR, "yijianshuanghan-bloom-sequence.png"))
    strip.save(os.path.join(SKILL_DIR, "yijianshuanghan-bloom-sequence.png"))
    strip.save(os.path.join(CLEAN_DIR, "yijianshuanghan-bloom-sequence.png"))
    print(f"Sequence strip updated: {strip.size}")
    
    # Dark Background Preview
    dark_strip = Image.new('RGB', (CANVAS_W * 8, CANVAS_H), (10, 16, 24))
    dark_strip.paste(strip, (0, 0), strip)
    dark_strip.save(os.path.join(SKILL_DIR, "yijianshuanghan-bloom-darkbg-preview.png"))
    
    # Transparent Animated GIF with high 255-color fidelity
    # Realistic 60 FPS timings:
    # F1=120ms (domain), F2=140ms (gather), F3=180ms (charge), F4=100ms (celestial slash),
    # F5=120ms (ice peak surge), F6=160ms (freeze freeze), F7=140ms (shatter burst), F8=180ms (snowfall)
    frame_durations = [120, 140, 180, 100, 120, 160, 140, 180]
    
    gif_frames = []
    for (f_num, cname, std_name, fr), dur in zip(processed_frames, frame_durations):
        # 1. Clean alpha for 1-bit GIF transparency
        arr = np.array(fr)
        alpha = arr[..., 3]
        trans_mask = alpha < 40
        arr[trans_mask] = [0, 0, 0, 0]
        arr[~trans_mask, 3] = 255
        clean_rgba = Image.fromarray(arr, 'RGBA')
        
        # 2. Quantize RGB to 255 colors (MEDIANCUT)
        rgb_img = clean_rgba.convert('RGB')
        p_img = rgb_img.quantize(colors=255, method=Image.MEDIANCUT)
        
        # 3. Build 256-color palette reserving index 255 for transparency
        palette = list(p_img.getpalette())
        while len(palette) < 256 * 3:
            palette.extend([0, 0, 0])
        palette[255 * 3 : 255 * 3 + 3] = [0, 0, 0]
        
        p_data = np.array(p_img)
        p_data[trans_mask] = 255
        
        final_gif_fr = Image.fromarray(p_data, mode='P')
        final_gif_fr.putpalette(palette)
        final_gif_fr.info['transparency'] = 255
        gif_frames.append(final_gif_fr)
        
    for gpath in [
        os.path.join(UNITY_DIR, "yijianshuanghan-bloom-animation.gif"),
        os.path.join(SKILL_DIR, "yijianshuanghan-bloom-animation.gif"),
        os.path.join(CLEAN_DIR, "yijianshuanghan-bloom-animation.gif"),
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
    print("Bloom Animated GIF updated successfully with full 255-color fidelity!")

    # Generate Unity .meta files
    for i in range(1, 9):
        png_path = os.path.join(UNITY_DIR, f"yijianshuanghan-bloom-{i}.png")
        meta_path = png_path + ".meta"
        if not os.path.exists(meta_path):
            guid = uuid.uuid5(uuid.NAMESPACE_DNS, f"yijianshuanghan-bloom-{i}").hex
            sprite_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"yijianshuanghan-bloom-sp-{i}").hex
            content = f"""fileFormatVersion: 2
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
  isReadable: 0
  webStreaming: 0
  priorityLevel: 0
  uploadedMode: 2
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMipmapLimit: 0
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
    wrapU: 0
    wrapV: 0
    wrapW: 0
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
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    maxPlaceholderSize: 32
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    physicsShape: []
    bones: []
    spriteID: {sprite_id}
    internalID: 0
    vertices: []
    indices: 
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {{}}
  mipmapLimitGroupName: 
  pSDRemoveMatte: 0
  doOverrideTextureManagerOperations: 0
  platformOperationGroupSettings: 
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""
            with open(meta_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Generated meta: {meta_path}")

if __name__ == '__main__':
    process_all_frames()
