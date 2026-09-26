#!/usr/bin/env python3
"""
Process Mook Swordsman (杂兵刀手) Animation Frames (Walk, Attack, Idle) for Unity / Tuanjie Engine.
- Clean pure magenta (#FF00FF) background with despill and alpha feathering.
- Uniform proportional scaling (standing height = 312px, matching Player PPU 214 and 165cm height).
- Foot baseline aligned to Y=437 on 680x480 canvas (Pivot 0.5, 0.09).
- Generates individual PNGs, Unity .meta files, preview GIFs, and transparent sprite sheets.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import scipy.ndimage as ndi
import shutil
import uuid

# Base paths
BASE_DIR = Path(r"c:\Users\luyus\Desktop\刀影江湖")
BRAIN_DIR = Path(r"C:\Users\luyus\.gemini\antigravity\brain\aa365a6b-0bfa-442e-993c-e4f5df23b1f4")

RAW_WALK = BRAIN_DIR / "mook_blade_walk_raw_1790339458391.jpg"
RAW_ATTACK = BRAIN_DIR / "mook_blade_attack_raw_1790339701258.jpg"
RAW_IDLE = BRAIN_DIR / "mook_blade_idle_raw_1790339794664.jpg"

UNITY_ENEMY_ROOT = BASE_DIR / "New Tuanjie Project" / "Assets" / "Sprites" / "Enemies" / "MookSwordsman"
DESIGN_SEQ_DIR = BASE_DIR / "设计" / "杂兵帧序列"

DESIGN_SEQ_DIR.mkdir(parents=True, exist_ok=True)

# Specs
CANVAS_W = 680
CANVAS_H = 480
TARGET_STAND_H = 312.0
FOOT_Y = 437
CENTER_X = 340

def make_meta(guid):
    return f"""fileFormatVersion: 2
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
  ignoreMipmapLimit: 0
"""

def clean_magenta(cell, thresh=45, feather=35, is_attack=False):
    """Clean solid magenta (#FF00FF) background with despill to eliminate magenta edge glow."""
    arr = np.array(cell, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    dist = np.sqrt((r - 255.0)**2 + g**2 + (b - 255.0)**2)
    
    # Magenta detector
    mag_tint = (r > 90) & (b > 90) & (g < 60) & (abs(r - b) < 60)
    
    # Despill: suppress magenta fringe reflected onto sprite edges
    spill = np.maximum(0, np.minimum(r - g, b - g))
    r_clean = np.clip(r - 0.95 * spill, 0, 255)
    b_clean = np.clip(b - 0.95 * spill, 0, 255)
    
    alpha = np.clip((dist - thresh) / feather, 0, 1) * 255
    alpha[mag_tint & (dist < 120)] = 0
    # Clear outer 4px edge to avoid JPEG border grid lines
    alpha[:4, :] = 0; alpha[-4:, :] = 0; alpha[:, :4] = 0; alpha[:, -4:] = 0
    
    # Clear ground shadow line if present
    if not is_attack:
        for y in range(483, cell.height):
            row_a = alpha[y, :]
            nz = np.where(row_a > 30)[0]
            if len(nz) > 150:
                alpha[y, :] = 0
                
    # Filter small disconnected noise components
    mask = (alpha > 25)
    labeled, num_features = ndi.label(mask)
    if num_features > 1:
        sizes = ndi.sum(mask, labeled, range(1, num_features + 1))
        # Keep components with size > 1500 pixels (keeps character body + slash arcs)
        valid_labels = [idx + 1 for idx, s in enumerate(sizes) if s > 1500]
        if valid_labels:
            keep_mask = np.isin(labeled, valid_labels)
            alpha[~keep_mask] = 0
            
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

def process_action(raw_img_path, action_name, frame_prefix, out_sub_dir, duration_ms, is_attack=False):
    print(f"\n================ Processing {action_name} ================")
    out_dir = UNITY_ENEMY_ROOT / out_sub_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    
    img = Image.open(raw_img_path)
    w, h = img.size
    cell_w, cell_h = w // 2, h // 2
    
    # 2x2 grid cut coordinates
    cells = [
        (img.crop((0, 0, cell_w, cell_h)), f"{action_name} Frame 1"),
        (img.crop((cell_w, 0, w, cell_h)), f"{action_name} Frame 2"),
        (img.crop((0, cell_h, cell_w, h)), f"{action_name} Frame 3"),
        (img.crop((cell_w, cell_h, w, h)), f"{action_name} Frame 4"),
    ]
    
    # Determine raw standing scale from Frame 1
    raw_c0 = clean_magenta(cells[0][0], is_attack=is_attack)
    _, (cx0, cy0, cx1, cy1) = tight_crop(raw_c0)
    raw_h = cy1 - cy0
    scale = TARGET_STAND_H / max(raw_h, 300.0)
    print(f"Action: {action_name}, Raw Height: {raw_h}px, Uniform Scale: {scale:.4f}")
    
    processed_frames = []
    
    for idx, (cell, desc) in enumerate(cells):
        cleaned = clean_magenta(cell, is_attack=is_attack)
        cropped, (cx0, cy0, cx1, cy1) = tight_crop(cleaned)
        
        nw = int(round(cropped.width * scale))
        nh = int(round(cropped.height * scale))
        scaled = cropped.resize((nw, nh), Image.LANCZOS)
        
        # Ground foot alignment: in 512 cell, feet rest near cy1
        # Reference ground is cy1 in the cell
        local_ground_y = cy1 - cy0
        scaled_ground_y = int(round(local_ground_y * scale))
        py = FOOT_Y - scaled_ground_y
        
        # Horizontal placement
        s_arr = np.array(scaled)
        s_alpha = s_arr[..., 3].astype(float)
        mid_h = nh // 2
        torso_slice = s_alpha[max(0, mid_h - 40):min(nh, mid_h + 40), :]
        if torso_slice.sum() > 10:
            torso_x = float((torso_slice * np.arange(nw)).sum() / torso_slice.sum())
        else:
            torso_x = nw / 2.0
            
        px = int(round(CENTER_X - torso_x))
        
        # Safety clamping
        px = max(5, min(CANVAS_W - 5 - nw, px))
        py = max(5, min(CANVAS_H - 2 - nh, py))
        
        canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        canvas.paste(scaled, (px, py), scaled)
        processed_frames.append(canvas)
        print(f"  Frame {idx+1}: {desc} -> {nw}x{nh} placed at ({px}, {py})")
        
    # 1. Save individual PNGs and Unity .meta files
    for i, frame in enumerate(processed_frames):
        p_path = out_dir / f"{frame_prefix}-{i+1}.png"
        frame.save(p_path, "PNG")
        m_path = out_dir / f"{frame_prefix}-{i+1}.png.meta"
        m_guid = uuid.uuid4().hex
        m_path.write_text(make_meta(m_guid), encoding="utf-8")
        
    print(f"  Saved 4 individual frames and .meta files to {out_dir}")
    
    # 2. Save preview GIF (Unity + Design)
    gif_path_unity = out_dir / "animation.gif"
    gif_path_design = DESIGN_SEQ_DIR / f"{frame_prefix}-animation.gif"
    processed_frames[0].save(
        gif_path_unity,
        save_all=True,
        append_images=processed_frames[1:],
        duration=duration_ms,
        loop=0,
        disposal=2
    )
    shutil.copyfile(gif_path_unity, gif_path_design)
    print(f"  Saved animation GIF -> {gif_path_unity}")
    
    # 3. Save 2x2 transparent sprite sheet
    sheet = Image.new("RGBA", (CANVAS_W * 2, CANVAS_H * 2), (0, 0, 0, 0))
    for i, frame in enumerate(processed_frames):
        r, c = i // 2, i % 2
        sheet.paste(frame, (c * CANVAS_W, r * CANVAS_H), frame)
    sheet_path = out_dir / "sheet-transparent.png"
    sheet.save(sheet_path, "PNG")
    print(f"  Saved 2x2 transparent sheet -> {sheet_path}")
    
    # 4. Save 4x1 horizontal sequence strip for design documentation
    strip = Image.new("RGBA", (CANVAS_W * 4, CANVAS_H), (0, 0, 0, 0))
    for i, frame in enumerate(processed_frames):
        strip.paste(frame, (i * CANVAS_W, 0), frame)
    strip_path = DESIGN_SEQ_DIR / f"{frame_prefix}-sequence.png"
    strip.save(strip_path, "PNG")
    print(f"  Saved horizontal sequence strip -> {strip_path}")

def main():
    print("Starting Mook Swordsman Sprite Processor...")
    # Walk: 4 frames, ~150ms/frame (600ms total cycle, aligns with 38f @ 60fps)
    process_action(RAW_WALK, "Mook Walk", "walk", "Walk", duration_ms=150, is_attack=False)
    # Attack: 4 frames, ~140ms/frame (~560ms total, aligns with 36f @ 60fps)
    process_action(RAW_ATTACK, "Mook Attack", "attack", "AttackA", duration_ms=140, is_attack=True)
    # Idle: 4 frames, ~200ms/frame (~800ms total breathing loop)
    process_action(RAW_IDLE, "Mook Idle", "idle", "Idle", duration_ms=200, is_attack=False)
    print("\nAll Mook Swordsman assets processed successfully!")

if __name__ == "__main__":
    main()
