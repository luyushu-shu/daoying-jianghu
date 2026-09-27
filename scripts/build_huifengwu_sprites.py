#!/usr/bin/env python3
"""
Generate and Export Qingfeng Swordsman Skill 2: 回风舞 (Whirling Wind Dance, QF-2 / QF-2E)
V3: Full Hands Sword-Swinging Actions (纯正双手大幅挥剑动作 + 狂草残月斩 + 剑尖寒芒)
NO idle poses, NO tornado hoops. Authentic martial-arts swordplay in hands and blade.

Features:
- Dynamic, visible hand and sword-slashing poses for all 8 frames:
  - F1: 拧腰蓄剑 (attack-5: 手臂高拉蓄劲，剑尖凝起寒芒星爆)
  - F2: 旋身撩剑 (attack-7: 双手由下向上猛烈撩斩，剑锋拉出月牙弧光)
  - F3: 剑轮初开 (attack-3: 大步向前大幅横斩！手臂完全舒展，白刃残月斩破空)
  - F4: 展袖换势 (attack-8: 顺势回旋，双手带剑划过身前流光)
  - F5: 双层风暴 (attack-11: 360°全速横斩怒挥，双手全力挥剑，双重残月交错绝杀)
  - F6: 侧步插剑 (attack-6: 双手重重劈剑沉地，剑尖入地定风裂痕)
  - F7: 挽花收剑 (attack-12: 手腕轻抖挽出精致水墨剑花)
  - F8: 拂袖敛意 (attack-4: 剑锋翻转回纳，秋水敛锋入鞘)
- Strict engine alignment: Canvas 680x480, PPU 214, Feet Anchor Y=437, Center X=340.
- Exports transparent individual PNGs, sequence strip, and halo-free transparent GIF.
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

def draw_sword_star_glint(canvas, gx, gy, size=24, intensity=1.0, color_glow=(46, 229, 212)):
    """Draw a blazing 4-point cross starburst at the sword tip."""
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    hl = size * 1.5
    draw.line([(gx - hl, gy), (gx + hl, gy)], fill=(255, 255, 255, int(255 * intensity)), width=2)
    vl = size * 1.0
    draw.line([(gx, gy - vl), (gx, gy + vl)], fill=(255, 255, 255, int(255 * intensity)), width=2)
    
    dl = size * 0.6
    draw.line([(gx - dl, gy - dl), (gx + dl, gy + dl)], fill=(color_glow[0], color_glow[1], color_glow[2], int(180 * intensity)), width=1)
    draw.line([(gx - dl, gy + dl), (gx + dl, gy - dl)], fill=(color_glow[0], color_glow[1], color_glow[2], int(180 * intensity)), width=1)
    
    cr = size * 0.35
    draw.polygon([(gx - cr, gy), (gx, gy - cr), (gx + cr, gy), (gx, gy + cr)], fill=(255, 255, 255, 255))
    
    glow = overlay.filter(ImageFilter.GaussianBlur(3.0))
    res = Image.alpha_composite(canvas, glow)
    res = Image.alpha_composite(res, overlay)
    return res

def draw_crescent_slash(canvas, cx, cy, radius, y_squash=0.45, start_angle=-2.8, sweep=3.0,
                        tilt_deg=0.0, width=42, intensity=1.0, add_ink_tail=True):
    """Draw an organic calligraphy crescent sword slash."""
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    steps = 45
    angles = np.linspace(start_angle, start_angle + sweep, steps)
    
    if add_ink_tail:
        pts_ink_out = []
        pts_ink_in = []
        for a in angles:
            t = (a - angles[0]) / (angles[-1] - angles[0])
            w = (math.sin(t * math.pi) ** 0.65) * (width * 1.4)
            ro = radius + w * 0.35
            ri = radius - w * 0.75
            pts_ink_out.append((cx + ro * math.cos(a), cy + ro * math.sin(a) * y_squash))
            pts_ink_in.append((cx + ri * math.cos(a), cy + ri * math.sin(a) * y_squash))
        poly_ink = pts_ink_out + pts_ink_in[::-1]
        if len(poly_ink) > 3:
            draw.polygon(poly_ink, fill=(16, 24, 30, int(150 * intensity)))
            
    pts_cyan_out = []
    pts_cyan_in = []
    for a in angles:
        t = (a - angles[0]) / (angles[-1] - angles[0])
        w = (math.sin(t * math.pi) ** 0.75) * (width * 0.85)
        ro = radius + w * 0.25
        ri = radius - w * 0.75
        pts_cyan_out.append((cx + ro * math.cos(a), cy + ro * math.sin(a) * y_squash))
        pts_cyan_in.append((cx + ri * math.cos(a), cy + ri * math.sin(a) * y_squash))
    poly_cyan = pts_cyan_out + pts_cyan_in[::-1]
    if len(poly_cyan) > 3:
        draw.polygon(poly_cyan, fill=(46, 229, 212, int(220 * intensity)))
        
    pts_white = []
    for a in angles:
        t = (a - angles[0]) / (angles[-1] - angles[0])
        ro = radius + ((math.sin(t * math.pi) ** 0.75) * (width * 0.25))
        pts_white.append((cx + ro * math.cos(a), cy + ro * math.sin(a) * y_squash))
    if len(pts_white) > 1:
        draw.line(pts_white, fill=(255, 255, 255, int(255 * intensity)), width=3)
        
    if abs(tilt_deg) > 0.1:
        overlay = overlay.rotate(-tilt_deg, center=(cx, cy), resample=Image.BICUBIC)
        
    glow = overlay.filter(ImageFilter.GaussianBlur(2.5))
    res = Image.alpha_composite(canvas, glow)
    res = Image.alpha_composite(res, overlay)
    return res

def draw_ink_flecks_and_sparks(canvas, cx, cy, count=16, radius=180, spread_angle=(-0.5, 0.5), intensity=1.0, seed=42):
    """Draw dynamic ink flecks and sword sparks along the swing path."""
    np.random.seed(seed)
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    for _ in range(count):
        ang = np.random.uniform(spread_angle[0], spread_angle[1])
        dist = np.random.uniform(radius * 0.7, radius * 1.3)
        px = cx + math.cos(ang) * dist
        py = cy + math.sin(ang) * (dist * 0.45)
        
        length = np.random.uniform(4, 12)
        dx = math.cos(ang + 0.3) * length
        dy = math.sin(ang + 0.3) * (length * 0.45)
        
        is_spark = np.random.rand() > 0.4
        color = (255, 255, 255, int(220 * intensity)) if np.random.rand() > 0.6 else (46, 229, 212, int(200 * intensity))
        if not is_spark:
            color = (18, 26, 32, int(180 * intensity))
            
        draw.line([(px, py), (px + dx, py + dy)], fill=color, width=np.random.randint(1, 3))
        
    glow = overlay.filter(ImageFilter.GaussianBlur(1.2))
    res = Image.alpha_composite(canvas, glow)
    res = Image.alpha_composite(res, overlay)
    return res

def draw_ground_sword_shock(canvas, tip_x, tip_y, intensity=1.0):
    """Draw linear ground shock lines bursting horizontally from sword tip on floor (Frame 6)."""
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    draw.line([(tip_x - 140, tip_y), (tip_x + 140, tip_y)], fill=(46, 229, 212, int(200 * intensity)), width=4)
    draw.line([(tip_x - 100, tip_y), (tip_x + 100, tip_y)], fill=(255, 255, 255, int(240 * intensity)), width=2)
    
    for dx, h in [(-90, 18), (-50, 30), (-15, 45), (15, 40), (60, 25), (95, 16)]:
        draw.line([(tip_x + dx, tip_y), (tip_x + dx * 1.1, tip_y - h)], fill=(255, 255, 255, int(200 * intensity)), width=2)
        draw.ellipse([(tip_x + dx * 1.1 - 2, tip_y - h - 2), (tip_x + dx * 1.1 + 2, tip_y - h + 2)], fill=(18, 26, 32, 180))
        
    glow = overlay.filter(ImageFilter.GaussianBlur(2.0))
    res = Image.alpha_composite(canvas, glow)
    res = Image.alpha_composite(res, overlay)
    return res

def build_all_frames_v3():
    print("=== Generating Qingfeng Skill 2: 回风舞 (V3 Full Sword-Swinging Hands) ===")
    
    P_ATK = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Attack")
    
    # 8 Frames with authentic, visible hand & sword swinging actions
    frame_defs = [
        (1, "01_拧腰抱剑", "Coil & Winding Up", os.path.join(P_ATK, "attack-5.png")),
        (2, "02_旋足踏风", "Pivot & Rising Slash", os.path.join(P_ATK, "attack-7.png")),
        (3, "03_剑轮初开", "Active 1 Full Slash", os.path.join(P_ATK, "attack-3.png")),
        (4, "04_顺风展袖", "Mid-Spin Sword Flow", os.path.join(P_ATK, "attack-8.png")),
        (5, "05_双层风暴", "Active 2 Whirlwind Slash", os.path.join(P_ATK, "attack-11.png")),
        (6, "06_侧步插剑", "Grounded Brake Slash", os.path.join(P_ATK, "attack-6.png")),
        (7, "07_挽花收剑", "Wrist Flourish", os.path.join(P_ATK, "attack-12.png")),
        (8, "08_拂袖敛意", "Neutral Sword Return", os.path.join(P_ATK, "attack-4.png")),
    ]
    
    generated_frames = []
    
    for idx, cname, ename, src_path in frame_defs:
        print(f"Crafting Frame {idx}: {cname} ({ename}) from {os.path.basename(src_path)}...")
        
        bg_vfx = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        fg_vfx = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        
        if idx == 1:
            # F1: attack-5 (双手引剑高提蓄力) —— 剑尖蓄势寒芒，剑身冷冽流光
            fg_vfx = draw_sword_star_glint(fg_vfx, gx=475, gy=230, size=24, intensity=1.2)
            fg_vfx = draw_ink_flecks_and_sparks(fg_vfx, cx=460, cy=240, count=6, radius=40, spread_angle=(-0.5, 0.5), intensity=0.8, seed=11)
            
        elif idx == 2:
            # F2: attack-7 (双手猛烈挑剑撩斩) —— 向上扬起的狂草青墨月牙弧光
            bg_vfx = draw_crescent_slash(bg_vfx, cx=340, cy=260, radius=180, y_squash=0.6,
                                         start_angle=-0.9, sweep=2.0, tilt_deg=22.0, width=36, intensity=1.1)
            fg_vfx = draw_sword_star_glint(fg_vfx, gx=465, gy=160, size=22, intensity=1.1)
            fg_vfx = draw_ink_flecks_and_sparks(fg_vfx, cx=465, cy=165, count=14, radius=70, spread_angle=(-0.5, 0.5), intensity=1.0, seed=22)
            
        elif idx == 3:
            # F3: attack-3 (双手大幅舒展向前横斩) —— 凌厉白刃残月斩，呼啸横扫半屏！
            bg_vfx = draw_crescent_slash(bg_vfx, cx=340, cy=290, radius=240, y_squash=0.40,
                                         start_angle=-2.9, sweep=2.9, tilt_deg=-2.0, width=48, intensity=1.3)
            fg_vfx = draw_crescent_slash(fg_vfx, cx=340, cy=290, radius=240, y_squash=0.40,
                                         start_angle=-0.7, sweep=1.0, tilt_deg=-2.0, width=48, intensity=1.2)
            fg_vfx = draw_sword_star_glint(fg_vfx, gx=560, gy=285, size=30, intensity=1.5)
            fg_vfx = draw_ink_flecks_and_sparks(fg_vfx, cx=530, cy=285, count=22, radius=90, spread_angle=(-0.4, 0.6), intensity=1.2, seed=33)
            
        elif idx == 4:
            # F4: attack-8 (双手回带转剑流光) —— 飘逸的高位换势剑意流光
            bg_vfx = draw_crescent_slash(bg_vfx, cx=335, cy=250, radius=190, y_squash=0.55,
                                         start_angle=-2.2, sweep=2.1, tilt_deg=-18.0, width=34, intensity=0.95)
            fg_vfx = draw_sword_star_glint(fg_vfx, gx=440, gy=210, size=20, intensity=1.0)
            fg_vfx = draw_ink_flecks_and_sparks(fg_vfx, cx=430, cy=220, count=12, radius=60, spread_angle=(-0.5, 0.5), intensity=0.9, seed=44)
            
        elif idx == 5:
            # F5: attack-11 (360°回旋横斩，双手全力挥舞) —— 双重残月交叉绝杀，中心爆鸣星芒！
            bg_vfx = draw_crescent_slash(bg_vfx, cx=340, cy=295, radius=245, y_squash=0.40,
                                         start_angle=-3.0, sweep=3.1, tilt_deg=2.0, width=52, intensity=1.4)
            bg_vfx = draw_crescent_slash(bg_vfx, cx=340, cy=275, radius=220, y_squash=0.50,
                                         start_angle=-2.4, sweep=2.5, tilt_deg=38.0, width=46, intensity=1.3)
            fg_vfx = draw_crescent_slash(fg_vfx, cx=340, cy=295, radius=245, y_squash=0.40,
                                         start_angle=-0.6, sweep=1.0, tilt_deg=2.0, width=52, intensity=1.3)
            fg_vfx = draw_sword_star_glint(fg_vfx, gx=500, gy=280, size=36, intensity=1.6)
            fg_vfx = draw_ink_flecks_and_sparks(fg_vfx, cx=500, cy=280, count=28, radius=120, spread_angle=(-1.2, 1.2), intensity=1.4, seed=55)
            
        elif idx == 6:
            # F6: attack-6 (双手重重下劈沉剑) —— 剑尖重插于地，笔锋顿止！地面撕裂出直线青墨剑劲
            fg_vfx = draw_ground_sword_shock(fg_vfx, tip_x=450, tip_y=434, intensity=1.3)
            fg_vfx = draw_sword_star_glint(fg_vfx, gx=450, gy=433, size=26, intensity=1.4)
            
        elif idx == 7:
            # F7: attack-12 (手腕翻转挽花) —— 身侧 8 字形水墨剑花翻卷收式
            fg_vfx = draw_crescent_slash(fg_vfx, cx=370, cy=290, radius=85, y_squash=0.7,
                                         start_angle=-1.5, sweep=2.4, tilt_deg=-15.0, width=22, intensity=0.85, add_ink_tail=False)
            fg_vfx = draw_sword_star_glint(fg_vfx, gx=380, gy=260, size=18, intensity=1.0)
            fg_vfx = draw_ink_flecks_and_sparks(fg_vfx, cx=380, cy=270, count=8, radius=50, spread_angle=(-1.0, 1.0), intensity=0.7, seed=77)
            
        elif idx == 8:
            # F8: attack-4 (双手持剑从容回纳) —— 剑身收敛寒光，秋水敛锋入鞘，自然衔接待机
            fg_vfx = draw_sword_star_glint(fg_vfx, gx=360, gy=290, size=14, intensity=0.8)

        # Composite: Background VFX -> Body -> Foreground VFX
        body = align_body_to_canvas(src_path, target_feet_y=TARGET_FEET_Y, center_x=CENTER_X)
        composite = Image.alpha_composite(bg_vfx, body)
        final_frame = Image.alpha_composite(composite, fg_vfx)
        
        generated_frames.append((idx, cname, final_frame))
        
        # Save individual PNGs
        fn_std = f"huifengwu-{idx}.png"
        fn_named = f"{cname}.png"
        fn_aligned = f"aligned_{cname}.png"
        
        final_frame.save(os.path.join(UNITY_DIR, fn_std))
        final_frame.save(os.path.join(UNITY_DIR, fn_named))
        final_frame.save(os.path.join(CLEAN_DIR, fn_std))
        final_frame.save(os.path.join(CLEAN_DIR, fn_named))
        final_frame.save(os.path.join(CLEAN_DIR, fn_aligned))
        final_frame.save(os.path.join(SKILL_DIR, fn_std))
        final_frame.save(os.path.join(SKILL_DIR, fn_named))

    # Build Sequence Strip (5440 x 480)
    strip_w = CANVAS_W * len(generated_frames)
    strip = Image.new('RGBA', (strip_w, CANVAS_H), (0, 0, 0, 0))
    for idx, cname, fr in generated_frames:
        strip.paste(fr, ((idx - 1) * CANVAS_W, 0), fr)
        
    strip.save(os.path.join(UNITY_DIR, "huifengwu-sequence.png"))
    strip.save(os.path.join(SKILL_DIR, "huifengwu-sequence.png"))
    strip.save(os.path.join(CLEAN_DIR, "huifengwu-sequence.png"))
    print(f"Sequence strip updated: {strip.size}")

    # Build Transparent Animated GIF
    durations = [70, 85, 70, 50, 70, 85, 85, 100]
    gif_frames = []
    for idx, cname, fr in generated_frames:
        c_data = np.array(fr)
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

    for gpath in [os.path.join(UNITY_DIR, "huifengwu-animation.gif"),
                  os.path.join(SKILL_DIR, "huifengwu-animation.gif"),
                  os.path.join(CLEAN_DIR, "huifengwu-animation.gif")]:
        gif_frames[0].save(
            gpath,
            save_all=True,
            append_images=gif_frames[1:],
            duration=durations,
            loop=0,
            transparency=255,
            disposal=2
        )
    print("=== All 8 V3 Huifengwu frames successfully generated! ===")

if __name__ == '__main__':
    build_all_frames_v3()
