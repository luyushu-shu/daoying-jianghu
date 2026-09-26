#!/usr/bin/env python3
"""
Full 15-frame Mook Swordsman (杂兵刀手) Walk Cycle directly aligned with Qingfeng Swordsman (青锋剑客) Walk sequence.
- 15 frames in a 5x3 grid layout (2-step alternating walk cycle: Left step frames 1-7, Right step frames 8-15).
- Matches Qingfeng's exact walk speed: 140ms/frame, 2.1s cycle, PPU 214, pivot Y=0.09.
- Exports walk-1.png ~ walk-15.png, Unity .meta files, MookWalk.anim, animation.gif, and transparent sheet.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import shutil
import uuid

BASE_DIR = Path(r"c:\Users\luyus\Desktop\刀影江湖")
BRAIN_DIR = Path(r"C:\Users\luyus\.gemini\antigravity\brain\aa365a6b-0bfa-442e-993c-e4f5df23b1f4")

RAW_15F = BRAIN_DIR / "mook_blade_walk_15f_raw_1790349108904.jpg"
WALK_DIR = BASE_DIR / "New Tuanjie Project" / "Assets" / "Sprites" / "Enemies" / "MookSwordsman" / "Walk"
DESIGN_SEQ_DIR = BASE_DIR / "设计" / "杂兵帧序列"

WALK_DIR.mkdir(parents=True, exist_ok=True)
DESIGN_SEQ_DIR.mkdir(parents=True, exist_ok=True)

CANVAS_W = 680
CANVAS_H = 480
TARGET_H = 312.0
FOOT_Y = 437
CENTER_X = 340
RAW_H = 222.0
SCALE = TARGET_H / RAW_H

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

def clean_magenta(cell):
    arr = np.array(cell, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    dist = np.sqrt((r - 255.0)**2 + g**2 + (b - 255.0)**2)
    mag_tint = (r > 90) & (b > 90) & (g < 60) & (abs(r - b) < 60)
    spill = np.maximum(0, np.minimum(r - g, b - g))
    r_clean = np.clip(r - 0.95 * spill, 0, 255)
    b_clean = np.clip(b - 0.95 * spill, 0, 255)
    alpha = np.clip((dist - 45) / 35.0, 0, 1) * 255
    alpha[mag_tint & (dist < 120)] = 0
    alpha[:3, :] = 0; alpha[-3:, :] = 0; alpha[:, :3] = 0; alpha[:, -3:] = 0
    out = np.dstack([r_clean, g, b_clean, alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")

def main():
    print("Processing 15-frame Qingfeng-aligned natural Walk cycle for Mook Swordsman...")
    im = Image.open(RAW_15F)
    w, h = im.size
    cw = w / 5.0
    ch = h / 3.0
    
    frames = []
    guids = []
    
    for r in range(3):
        for c in range(5):
            x0 = int(round(c * cw))
            x1 = int(round((c + 1) * cw))
            y0 = int(round(r * ch))
            y1 = int(round((r + 1) * ch))
            cell = im.crop((x0, y0, x1, y1))
            cleaned = clean_magenta(cell)
            arr = np.array(cleaned)
            alpha = arr[..., 3]
            rows = np.where(alpha > 20)[0]
            cols = np.where(alpha > 20)[1]
            cy0, cy1 = rows.min(), rows.max()
            cx0, cx1 = cols.min(), cols.max()
            crop = cleaned.crop((cx0, cy0, cx1 + 1, cy1 + 1))
            
            nw = int(round(crop.width * SCALE))
            nh = int(round(crop.height * SCALE))
            scaled = crop.resize((nw, nh), Image.LANCZOS)
            
            ground_y = 244.0
            scaled_ground_offset = int(round((ground_y - cy0) * SCALE))
            py = FOOT_Y - scaled_ground_offset
            
            s_arr = np.array(scaled)
            s_alpha = s_arr[..., 3].astype(float)
            mid_h = nh // 2
            torso_slice = s_alpha[max(0, mid_h - 40):min(nh, mid_h + 40), :]
            if torso_slice.sum() > 10:
                torso_x = float((torso_slice * np.arange(nw)).sum() / torso_slice.sum())
            else:
                torso_x = nw / 2.0
            px = int(round(CENTER_X - torso_x))
            
            canv = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
            canv.paste(scaled, (px, py), scaled)
            frames.append(canv)
            
    # Clean old walk-*.png files in directory first
    for old_f in WALK_DIR.glob("walk-*.png*"):
        old_f.unlink()
        
    # Save individual frames 1..15
    for i, frame in enumerate(frames):
        p_path = WALK_DIR / f"walk-{i+1}.png"
        frame.save(p_path, "PNG")
        m_path = WALK_DIR / f"walk-{i+1}.png.meta"
        g = uuid.uuid4().hex
        guids.append(g)
        m_path.write_text(make_meta(g), encoding="utf-8")
        
    print(f"Saved {len(frames)} individual walk frames to {WALK_DIR}")
    
    # Save GIF preview (140ms/frame, matching Qingfeng exactly)
    gif_path = WALK_DIR / "animation.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=140,
        loop=0,
        disposal=2
    )
    shutil.copyfile(gif_path, DESIGN_SEQ_DIR / "walk-animation.gif")
    shutil.copyfile(gif_path, BRAIN_DIR / "mook_walk_animation.gif")
    print(f"Saved animation GIF -> {gif_path}")
    
    # Save 5x3 transparent sprite sheet
    sheet = Image.new("RGBA", (CANVAS_W * 5, CANVAS_H * 3), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        r, c = i // 5, i % 5
        sheet.paste(f, (c * CANVAS_W, r * CANVAS_H), f)
    sheet_path = WALK_DIR / "sheet-transparent.png"
    sheet.save(sheet_path, "PNG")
    print(f"Saved 5x3 sheet-transparent.png -> {sheet_path}")
    
    # Save 5x3 sequence filmstrip for design
    strip_path = DESIGN_SEQ_DIR / "walk-sequence.png"
    sheet.save(strip_path, "PNG")
    shutil.copyfile(strip_path, BRAIN_DIR / "mook_walk_sequence.png")
    print(f"Saved walk-sequence.png -> {strip_path}")
    
    # Update MookWalk.anim (15 frames @ 140ms/frame = 2.1s cycle)
    frame_duration = 0.140
    total_time = len(frames) * frame_duration
    sample_rate = 1.0 / frame_duration
    
    curve_points = []
    pptr_mappings = []
    for i, g in enumerate(guids):
        t = i * frame_duration
        curve_points.append(f"""    - time: {t:.4f}
      value: {{fileID: 21300000, guid: {g}, type: 3}}""")
        pptr_mappings.append(f"    - {{fileID: 21300000, guid: {g}, type: 3}}")
        
    curve_str = "\n".join(curve_points)
    pptr_str = "\n".join(pptr_mappings)
    
    anim_content = f"""%YAML 1.1
%TAG !u! tag:yousandi.cn,2023:
--- !u!74 &7400000
AnimationClip:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: MookWalk
  serializedVersion: 11
  m_Legacy: 0
  m_Compressed: 0
  m_UseHighQualityCurve: 1
  m_RotationCurves: []
  m_CompressedRotationCurves: []
  m_EulerCurves: []
  m_PositionCurves: []
  m_ScaleCurves: []
  m_FloatCurves: []
  m_PPtrCurves:
  - serializedVersion: 2
    curve:
{curve_str}
    attribute: m_Sprite
    path: 
    classID: 212
    script: {{fileID: 0}}
    flags: 2
  m_SampleRate: {sample_rate:.4f}
  m_WrapMode: 0
  m_Bounds:
    m_Center: {{x: 0, y: 0, z: 0}}
    m_Extent: {{x: 0, y: 0, z: 0}}
  m_ClipBindingConstant:
    genericBindings:
    - serializedVersion: 2
      path: 0
      attribute: 0
      script: {{fileID: 0}}
      typeID: 212
      customType: 23
      isPPtrCurve: 1
      isIntCurve: 0
      isSerializeReferenceCurve: 0
    pptrCurveMapping:
{pptr_str}
  m_AnimationClipSettings:
    serializedVersion: 3
    m_AdditiveReferencePoseClip: {{fileID: 0}}
    m_AdditiveReferencePoseTime: 0
    m_StartTime: 0
    m_StopTime: {total_time:.4f}
    m_OrientationOffsetY: 0
    m_Level: 0
    m_CycleOffset: 0
    m_AdditiveType: 0
    m_BasePoseType: 0
    m_AdditiveSelectedAnimation: {{fileID: 0}}
    m_AdditiveSelectedAnimationFrameIndex: 0
    m_HasAdditiveReferencePose: 0
    m_LockToRoot: 0
    m_LoopTime: 1
    m_LoopBlend: 0
    m_LoopBlendOrientation: 0
    m_LoopBlendPositionY: 0
    m_LoopBlendPositionXZ: 0
    m_KeepOriginalOrientation: 0
    m_KeepOriginalPositionY: 1
    m_KeepOriginalPositionXZ: 0
    m_HeightFromFeet: 0
    m_Mirror: 0
  m_EditorCurves: []
  m_EulerEditorCurves: []
  m_HasGenericRootTransform: 0
  m_HasMotionFloatCurves: 0
  m_Events: []
  m_Intervals: []
  m_ACLContext:
    ACLCompressionLevel: 0
    ACLCurvePrecision: 0.01
    UseACLCurve: 0
    UseACLFastSampleMode: 1
  m_MuscleEncodeContext:
    type: 0
    rotationError: 0
    positionError: 0
    scaleError: 0
"""
    anim_path = WALK_DIR / "MookWalk.anim"
    anim_path.write_text(anim_content, encoding="utf-8")
    print(f"Updated {anim_path}")
    print("\n15-frame Qingfeng-aligned natural walk processing completed successfully!")

if __name__ == "__main__":
    main()
