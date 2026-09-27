#!/usr/bin/env python3
"""
Generate and Export Qingfeng Swordsman Skill 2: 回风舞 (Whirling Wind Dance, QF-2 / QF-2E)
8-Frame Sequential Sprites Aligned to 680x480, PPU 214, Feet Anchor Y=437.

Features:
- Anatomical and martial arts adherence to '设计/刀影江湖-回风舞动作帧设计表.md':
  F1: 拧腰抱剑 (Coil & Sinking)
  F2: 旋足踏风 (Pivot & Wind Swirl)
  F3: 剑轮初开 (Active 1 / First Whirlwind Slash)
  F4: 顺风展袖 (Mid-Spin Flow)
  F5: 双层风暴 (Active 2 / Dual Storm Whirlwind)
  F6: 侧步插剑 (Side-Step Brake)
  F7: 挽花收剑 (Wrist Flourish)
  F8: 拂袖敛意 (Neutral Stance)
- Procedural multi-layer martial-arts VFX:
  - Ground ink vortex decal (水墨磨盘阵)
  - 360° horizontal and diagonal cyan-white blade rings (双层风暴剑轮)
  - Helical wind streamers and ink splatter debris (24风旋墨雨)
  - Ground brake shockwave (踏地定风冲击波)
  - Dissipating sword intent motes (剑气余韵光粒)
- Exports transparent individual PNGs, sequence strip, and high-fidelity transparent GIF.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CANVAS_W = 680
CANVAS_H = 480
TARGET_FEET_Y = 437
CENTER_X = 340

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "02_回风舞")
UNITY_DIR = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Huifengwu")
CLEAN_DIR = os.path.join(SKILL_DIR, "pure_clean_sprites")

os.makedirs(SKILL_DIR, exist_ok=True)
os.makedirs(UNITY_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)

def align_body_to_canvas(img_path, target_feet_y=TARGET_FEET_Y, center_x=CENTER_X, flip_x=False):
    """Load body sprite, compute feet position, and place cleanly onto 680x480 canvas."""
    raw = Image.open(img_path).convert('RGBA')
    if flip_x:
        raw = raw.transpose(Image.FLIP_LEFT_RIGHT)
    arr = np.array(raw)
    alpha = arr[:, :, 3]
    ys, xs = np.where(alpha > 40)
    
    if len(ys) == 0:
        return Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    
    cur_feet_y = np.max(ys)
    cur_center_x = int(np.median(xs))
    
    shift_x = center_x - cur_center_x
    shift_y = target_feet_y - cur_feet_y
    
    canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.paste(raw, (shift_x, shift_y), raw)
    return canvas

def draw_ground_vortex(canvas, intensity=1.0, radius=90, rot_angle=0.0):
    """Draw procedural ground ink vortex decal beneath feet at Y=437."""
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = CENTER_X, TARGET_FEET_Y - 4
    
    # Draw nested swirling ink rings with squashed perspective (flattened ellipse)
    for r in range(int(radius * 0.3), int(radius), 8):
        box = (cx - r, cy - int(r * 0.28), cx + r, cy + int(r * 0.28))
        a = int(50 * intensity * (1.0 - r / radius))
        # Ink black rim
        draw.arc(box, start=int(rot_angle), end=int(rot_angle + 270), fill=(18, 24, 30, a), width=3)
        # Faint cyan glow inside
        if r % 16 == 0:
            draw.arc(box, start=int(rot_angle + 90), end=int(rot_angle + 340), fill=(46, 229, 212, int(a * 0.7)), width=2)
            
    overlay = overlay.filter(ImageFilter.GaussianBlur(1.5))
    return Image.alpha_composite(canvas, overlay)

def draw_blade_ring(canvas, cx, cy, rx, ry, tilt_deg=0.0, intensity=1.0, start_deg=0, sweep_deg=360):
    """Draw a 360° sweeping cyan-white blade ring with glowing core and ink trail."""
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Outer ink brush wash (dark teal/black)
    outer_box = (cx - rx, cy - ry, cx + rx, cy + ry)
    ink_alpha = int(140 * intensity)
    draw.arc(outer_box, start=start_deg, end=start_deg + sweep_deg, fill=(17, 35, 42, ink_alpha), width=14)
    
    # Cyan outer energy aura (#2EE5D4)
    cyan_alpha = int(220 * intensity)
    draw.arc(outer_box, start=start_deg + 15, end=start_deg + sweep_deg - 5, fill=(46, 229, 212, cyan_alpha), width=8)
    
    # Bright white core razor line (#FFFFFF)
    white_alpha = int(255 * intensity)
    draw.arc(outer_box, start=start_deg + 30, end=start_deg + sweep_deg - 10, fill=(255, 255, 255, white_alpha), width=3)
    
    # If tilted, rotate the overlay around (cx, cy)
    if abs(tilt_deg) > 0.1:
        overlay = overlay.rotate(-tilt_deg, center=(cx, cy), resample=Image.BICUBIC)
        
    blurred_glow = overlay.filter(ImageFilter.GaussianBlur(2.0))
    result = Image.alpha_composite(canvas, blurred_glow)
    result = Image.alpha_composite(result, overlay)
    return result

def draw_wind_swirls(canvas, cx, cy, count=12, intensity=1.0, seed=42):
    """Draw spiraling wind streamers and ink splatter motes."""
    np.random.seed(seed)
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    for _ in range(count):
        # Parametric logarithmic spiral arc
        angle0 = np.random.uniform(0, 2 * math.pi)
        r0 = np.random.uniform(20, 80)
        pts = []
        for step in range(8):
            theta = angle0 + step * 0.25
            r = r0 + step * 14
            px = cx + r * math.cos(theta) * 1.3
            py = cy + r * math.sin(theta) * 0.65 - step * 5
            pts.append((px, py))
            
        a = int(np.random.uniform(100, 200) * intensity)
        color = (46, 229, 212, a) if np.random.rand() > 0.4 else (18, 24, 32, int(a * 1.2))
        if len(pts) > 1:
            draw.line(pts, fill=color, width=np.random.randint(2, 4))
            
        # Splatter droplet at tip
        tip_x, tip_y = pts[-1]
        rad = np.random.randint(2, 5)
        draw.ellipse((tip_x - rad, tip_y - rad, tip_x + rad, tip_y + rad), fill=color)
        
    blurred = overlay.filter(ImageFilter.GaussianBlur(1.0))
    return Image.alpha_composite(canvas, blurred)

def draw_shockwave_brake(canvas, cx, cy, radius=180, intensity=1.0):
    """Draw expanding ground brake shockwave ring for Frame 6."""
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Horizontal flattened shock ring on floor
    box = (cx - radius, cy - int(radius * 0.22), cx + radius, cy + int(radius * 0.22))
    draw.ellipse(box, outline=(46, 229, 212, int(180 * intensity)), width=5)
    
    inner_box = (cx - int(radius * 0.9), cy - int(radius * 0.20), cx + int(radius * 0.9), cy + int(radius * 0.20))
    draw.ellipse(inner_box, outline=(255, 255, 255, int(220 * intensity)), width=2)
    
    # Ground dust / ink splash rays
    for i in range(16):
        ang = i * (math.pi / 8)
        rx = cx + math.cos(ang) * radius
        ry = cy + math.sin(ang) * (radius * 0.22)
        draw.line([(cx + math.cos(ang) * (radius * 0.7), cy + math.sin(ang) * (radius * 0.16)), (rx, ry)],
                  fill=(18, 28, 36, int(150 * intensity)), width=3)
        
    blurred = overlay.filter(ImageFilter.GaussianBlur(2.0))
    res = Image.alpha_composite(canvas, blurred)
    res = Image.alpha_composite(res, overlay)
    return res

def draw_residual_motes(canvas, cx, cy, count=16, intensity=1.0, seed=101):
    """Draw soft dissipating sword intent particles and ink wisps for Recovery."""
    np.random.seed(seed)
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    for _ in range(count):
        px = cx + np.random.uniform(-140, 140)
        py = cy + np.random.uniform(-180, 40)
        sz = np.random.uniform(1.5, 4.0)
        a = int(np.random.uniform(60, 160) * intensity)
        c = (255, 255, 255, a) if np.random.rand() > 0.5 else (46, 229, 212, a)
        draw.ellipse((px - sz, py - sz, px + sz, py + sz), fill=c)
        
    blurred = overlay.filter(ImageFilter.GaussianBlur(1.2))
    return Image.alpha_composite(canvas, blurred)

def build_all_frames():
    print("=== Generating Qingfeng Skill 2: 回风舞 (8 Sequential Frames) ===")
    
    # Pose sources from Player animation library
    P_HT = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "HeavyThrust")
    P_ATK = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Attack")
    P_DODGE = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Dodge")
    P_JUMP = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Jump")
    
    frame_defs = [
        # (index, chinese_name, english_role, source_path, flip_x, vfx_func)
        (1, "01_拧腰抱剑", "Coil & Sinking", os.path.join(P_HT, "heavy-1.png"), False, "vfx_f1"),
        (2, "02_旋足踏风", "Pivot & Swirl", os.path.join(P_DODGE, "dodge-7.png"), False, "vfx_f2"),
        (3, "03_剑轮初开", "Active 1 Slash", os.path.join(P_ATK, "attack-11.png"), False, "vfx_f3"),
        (4, "04_顺风展袖", "Mid-Spin Flow", os.path.join(P_JUMP, "jump-4.png"), False, "vfx_f4"),
        (5, "05_双层风暴", "Active 2 Whirlwind", os.path.join(P_ATK, "attack-10.png"), False, "vfx_f5"),
        (6, "06_侧步插剑", "Side-Step Brake", os.path.join(P_HT, "heavy-6.png"), False, "vfx_f6"),
        (7, "07_挽花收剑", "Wrist Flourish", os.path.join(P_HT, "heavy-7.png"), False, "vfx_f7"),
        (8, "08_拂袖敛意", "Neutral Return", os.path.join(P_HT, "heavy-8.png"), False, "vfx_f8"),
    ]
    
    generated_frames = []
    
    for idx, cname, ename, src_path, flip, vfx_type in frame_defs:
        print(f"Building Frame {idx}: {cname} ({ename})...")
        
        # 1. Base canvas with background VFX
        frame = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        
        # Background VFX layer
        if vfx_type == "vfx_f1":
            frame = draw_ground_vortex(frame, intensity=0.7, radius=80, rot_angle=20)
        elif vfx_type == "vfx_f2":
            frame = draw_ground_vortex(frame, intensity=0.9, radius=110, rot_angle=60)
            frame = draw_wind_swirls(frame, CENTER_X, TARGET_FEET_Y - 120, count=8, intensity=0.8, seed=20)
        elif vfx_type == "vfx_f3":
            frame = draw_ground_vortex(frame, intensity=1.1, radius=140, rot_angle=120)
            # Full 360° horizontal whirlwind blade ring (radius 220px = 1.0m+ in canvas)
            frame = draw_blade_ring(frame, cx=CENTER_X, cy=TARGET_FEET_Y - 130, rx=230, ry=58, tilt_deg=2.0, intensity=1.2, start_deg=10, sweep_deg=340)
            frame = draw_wind_swirls(frame, CENTER_X, TARGET_FEET_Y - 130, count=16, intensity=1.1, seed=33)
        elif vfx_type == "vfx_f4":
            frame = draw_ground_vortex(frame, intensity=0.8, radius=110, rot_angle=180)
            # Diagonal shifting blade ribbon
            frame = draw_blade_ring(frame, cx=CENTER_X - 10, cy=TARGET_FEET_Y - 150, rx=190, ry=50, tilt_deg=-15.0, intensity=0.9, start_deg=30, sweep_deg=280)
            frame = draw_wind_swirls(frame, CENTER_X, TARGET_FEET_Y - 150, count=12, intensity=0.9, seed=44)
        elif vfx_type == "vfx_f5":
            frame = draw_ground_vortex(frame, intensity=1.3, radius=160, rot_angle=240)
            # Dual-layer storm: horizontal ring + 35° diagonal intersecting ring!
            frame = draw_blade_ring(frame, cx=CENTER_X, cy=TARGET_FEET_Y - 135, rx=245, ry=62, tilt_deg=4.0, intensity=1.4, start_deg=0, sweep_deg=360)
            frame = draw_blade_ring(frame, cx=CENTER_X, cy=TARGET_FEET_Y - 150, rx=220, ry=56, tilt_deg=35.0, intensity=1.3, start_deg=20, sweep_deg=320)
            frame = draw_wind_swirls(frame, CENTER_X, TARGET_FEET_Y - 140, count=24, intensity=1.4, seed=55)
        elif vfx_type == "vfx_f6":
            # Expanding floor brake shockwave
            frame = draw_shockwave_brake(frame, cx=CENTER_X, cy=TARGET_FEET_Y - 6, radius=210, intensity=1.2)
            frame = draw_residual_motes(frame, CENTER_X, TARGET_FEET_Y - 100, count=14, intensity=1.0, seed=66)
        elif vfx_type == "vfx_f7":
            # Wrist flourish circular ink ribbon
            frame = draw_blade_ring(frame, cx=CENTER_X + 20, cy=TARGET_FEET_Y - 120, rx=90, ry=28, tilt_deg=-10.0, intensity=0.8, start_deg=40, sweep_deg=260)
            frame = draw_residual_motes(frame, CENTER_X, TARGET_FEET_Y - 110, count=18, intensity=0.8, seed=77)
        elif vfx_type == "vfx_f8":
            # Dissipating faint sparks
            frame = draw_residual_motes(frame, CENTER_X, TARGET_FEET_Y - 120, count=8, intensity=0.4, seed=88)
            
        # 2. Character Body Layer
        body = align_body_to_canvas(src_path, target_feet_y=TARGET_FEET_Y, center_x=CENTER_X, flip_x=flip)
        
        # Composite body over background VFX
        composite = Image.alpha_composite(frame, body)
        
        # Foreground VFX overlay (cutting blade highlights on top of body)
        fg = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        if vfx_type == "vfx_f3":
            fg = draw_blade_ring(fg, cx=CENTER_X, cy=TARGET_FEET_Y - 130, rx=230, ry=58, tilt_deg=2.0, intensity=0.8, start_deg=160, sweep_deg=160)
        elif vfx_type == "vfx_f5":
            fg = draw_blade_ring(fg, cx=CENTER_X, cy=TARGET_FEET_Y - 135, rx=245, ry=62, tilt_deg=4.0, intensity=1.0, start_deg=150, sweep_deg=180)
            fg = draw_blade_ring(fg, cx=CENTER_X, cy=TARGET_FEET_Y - 150, rx=220, ry=56, tilt_deg=35.0, intensity=0.9, start_deg=140, sweep_deg=160)
        elif vfx_type == "vfx_f7":
            fg = draw_blade_ring(fg, cx=CENTER_X + 20, cy=TARGET_FEET_Y - 120, rx=90, ry=28, tilt_deg=-10.0, intensity=0.6, start_deg=150, sweep_deg=120)
            
        final_frame = Image.alpha_composite(composite, fg)
        generated_frames.append((idx, cname, final_frame))
        
        # Save individual PNGs into all target directories
        fn_std = f"huifengwu-{idx}.png"
        fn_named = f"{cname}.png"
        fn_aligned = f"aligned_{cname}.png"
        
        # Unity project folder
        final_frame.save(os.path.join(UNITY_DIR, fn_std))
        final_frame.save(os.path.join(UNITY_DIR, fn_named))
        
        # Design folders
        final_frame.save(os.path.join(CLEAN_DIR, fn_std))
        final_frame.save(os.path.join(CLEAN_DIR, fn_named))
        final_frame.save(os.path.join(CLEAN_DIR, fn_aligned))
        final_frame.save(os.path.join(SKILL_DIR, fn_std))
        final_frame.save(os.path.join(SKILL_DIR, fn_named))

    # 3. Build Sequence Strip (8 frames side by side: 5440 x 480)
    strip_w = CANVAS_W * len(generated_frames)
    strip = Image.new('RGBA', (strip_w, CANVAS_H), (0, 0, 0, 0))
    for idx, cname, fr in generated_frames:
        strip.paste(fr, ((idx - 1) * CANVAS_W, 0), fr)
        
    strip.save(os.path.join(UNITY_DIR, "huifengwu-sequence.png"))
    strip.save(os.path.join(SKILL_DIR, "huifengwu-sequence.png"))
    strip.save(os.path.join(CLEAN_DIR, "huifengwu-sequence.png"))
    print(f"Sequence strip saved: {strip.size}")

    # 4. Build Transparent Animated GIF with zero halos
    # Frame durations in ms corresponding to 60 FPS design table:
    # F1 (4f -> 70ms), F2 (5f -> 85ms), F3 (4f -> 70ms), F4 (3f -> 50ms),
    # F5 (4f -> 70ms), F6 (5f -> 85ms), F7 (5f -> 85ms), F8 (6f -> 100ms)
    durations = [70, 85, 70, 50, 70, 85, 85, 100]
    
    gif_frames = []
    for idx, cname, fr in generated_frames:
        c_data = np.array(fr)
        # Transparent mask
        trans_mask = c_data[:, :, 3] < 80
        c_data[trans_mask] = [0, 0, 0, 0]
        c_data[~trans_mask, 3] = 255
        
        p_img = Image.fromarray(c_data, 'RGBA').convert('RGBA')
        alpha_channel = p_img.split()[3]
        p_img_rgb = p_img.convert('RGB')
        p_img_p = p_img_rgb.quantize(colors=255, method=Image.MEDIANCUT)
        
        p_data = np.array(p_img_p)
        p_data[np.array(alpha_channel) == 0] = 255
        
        final_gif_fr = Image.fromarray(p_data, mode='P')
        palette = p_img_p.getpalette()
        while len(palette) < 256 * 3:
            palette.extend([0, 0, 0])
        final_gif_fr.putpalette(palette)
        final_gif_fr.info['transparency'] = 255
        gif_frames.append(final_gif_fr)

    gif_path_unity = os.path.join(UNITY_DIR, "huifengwu-animation.gif")
    gif_path_skill = os.path.join(SKILL_DIR, "huifengwu-animation.gif")
    gif_path_clean = os.path.join(CLEAN_DIR, "huifengwu-animation.gif")
    
    for gpath in [gif_path_unity, gif_path_skill, gif_path_clean]:
        gif_frames[0].save(
            gpath,
            save_all=True,
            append_images=gif_frames[1:],
            duration=durations,
            loop=0,
            transparency=255,
            disposal=2
        )
    print("All GIFs generated successfully!")
    print("=== All 8 Huifengwu frames and sequences generated perfectly! ===")

if __name__ == '__main__':
    build_all_frames()
