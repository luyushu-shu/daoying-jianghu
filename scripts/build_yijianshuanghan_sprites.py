#!/usr/bin/env python3
"""
Generate and Export Qingfeng Swordsman Skill 3: 一剑霜寒 (Frostbound Slash, QF-3)
Non-Enhanced Version (常态版 · 8阶段蓄力破防霜线斩)

Features:
- 8 Distinct, authentic martial-arts swordplay phases:
  - F1: 沉步凝渊 (Grounding & Settle · 1~6f): 侧弓马步沉肩，双掌握剑横胸，脚下初结微霜
  - F2: 霜华引刃 (Frost Influx · 7~14f): 提剑举于肩侧，极寒冻气化作漩涡向剑身汇聚，剑尖点亮极寒冰芒
  - F3: 蓄力凝冰 (Deep Charge · 15~20f): 极度下潜蓄势（可蓄至45f），剑身凝结玄冰琉璃晶层，地表蔓延冰裂，韧体护身
  - F4: 惊雷裂斩 (Thunderous Cleave · 21~24f): 【核心斩击 Active 1】全身扭腰爆发超大弧度水平横斩！纯白极亮寒刃破空
  - F5: 霜线疾行 (Frost Line Ground Surge · 25~28f): 【核心破防 Active 2】贴地狂飙2.6m笔直破空霜线，地表破土拔起整排锐利冰棱
  - F6: 踏雪止势 (Step & Post-Slash Lock · 29~36f): 前弓步踏实地面卸力，双手持剑滞空微震，前方地面留厚重冰带与袅袅冰雾
  - F7: 振刃碎冰 (Flick & Frost Shatter · 37~44f): 手腕轻抖挽剑，剑身微震震碎残余薄冰，冰晶碎片与寒气四溅
  - F8: 拂袖归渊 (Sheathe & Restore · 45~54f): 双手收剑入怀，秋水敛锋入鞘，衣摆自然垂落，地表霜痕淡化，无缝衔接待机
- Strict engine alignment: Canvas 680x480, PPU 214, Feet Anchor Y=437, Center X=340.
- Exports transparent individual PNGs, 5440x480 sequence strip, and transparent looping GIF.
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
SKILL_DIR = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "03_一剑霜寒")
UNITY_DIR = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Yijianshuanghan")
CLEAN_DIR = os.path.join(SKILL_DIR, "pure_clean_sprites")

os.makedirs(SKILL_DIR, exist_ok=True)
os.makedirs(UNITY_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)

# Frost Palette
COLOR_ICE_DEEP = (26, 95, 160)       # 深蓝玄冰
COLOR_FROST_AZURE = (58, 185, 235)   # 极寒青蓝
COLOR_GLACIAL_CYAN = (120, 225, 255) # 琉璃浅冰
COLOR_ICE_WHITE = (240, 252, 255)    # 极光纯白
COLOR_MIST = (200, 240, 255)         # 寒白冰雾
COLOR_INK_ACCENT = (14, 24, 34)      # 水墨煞意衬底


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


def draw_frost_star_glint(canvas, gx, gy, size=24, intensity=1.0, color_glow=COLOR_GLACIAL_CYAN):
    """Draw a blazing crystalline 4-point cross starburst at sword tip or strike core."""
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    hl = size * 1.6
    draw.line([(gx - hl, gy), (gx + hl, gy)], fill=(255, 255, 255, int(255 * intensity)), width=2)
    vl = size * 1.1
    draw.line([(gx, gy - vl), (gx, gy + vl)], fill=(255, 255, 255, int(255 * intensity)), width=2)
    
    dl = size * 0.65
    c_a = int(190 * intensity)
    draw.line([(gx - dl, gy - dl), (gx + dl, gy + dl)], fill=(color_glow[0], color_glow[1], color_glow[2], c_a), width=1)
    draw.line([(gx - dl, gy + dl), (gx + dl, gy - dl)], fill=(color_glow[0], color_glow[1], color_glow[2], c_a), width=1)
    
    cr = size * 0.38
    draw.polygon([(gx - cr, gy), (gx, gy - cr), (gx + cr, gy), (gx, gy + cr)], fill=(255, 255, 255, 255))
    
    glow = overlay.filter(ImageFilter.GaussianBlur(3.2))
    res = Image.alpha_composite(canvas, glow)
    res = Image.alpha_composite(res, overlay)
    return res


def draw_ground_frost_crystals(canvas, cx, ground_y=437, radius=60, count=7, intensity=1.0, seed=1):
    """Draw sharp, crystalline ice spikes and ground frost rime around character's feet."""
    np.random.seed(seed)
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Ground mist base ellipse
    draw.ellipse([(cx - radius * 1.3, ground_y - 8), (cx + radius * 1.3, ground_y + 10)],
                 fill=(COLOR_MIST[0], COLOR_MIST[1], COLOR_MIST[2], int(70 * intensity)))
    
    # Radiating ice shards and cracks
    for i in range(count):
        offset_x = np.random.uniform(-radius, radius)
        spike_x = cx + offset_x
        spike_h = np.random.uniform(10, 28) * intensity
        spike_w = np.random.uniform(4, 9)
        tilt = np.random.uniform(-0.35, 0.35)
        
        pts = [
            (spike_x - spike_w, ground_y + 2),
            (spike_x + spike_w * 0.5, ground_y + 2),
            (spike_x + spike_h * tilt, ground_y - spike_h),
            (spike_x - spike_w * 0.8, ground_y - spike_h * 0.4)
        ]
        
        # Faceted polygon shading
        col_main = COLOR_GLACIAL_CYAN if (i % 2 == 0) else COLOR_FROST_AZURE
        draw.polygon(pts, fill=(col_main[0], col_main[1], col_main[2], int(200 * intensity)),
                     outline=(255, 255, 255, int(240 * intensity)))
        
        # Ground crack line
        crack_end_x = spike_x + np.random.uniform(-20, 20)
        draw.line([(spike_x, ground_y), (crack_end_x, ground_y + np.random.uniform(1, 5))],
                  fill=(COLOR_ICE_DEEP[0], COLOR_ICE_DEEP[1], COLOR_ICE_DEEP[2], int(160 * intensity)), width=1)
        
    glow = overlay.filter(ImageFilter.GaussianBlur(1.8))
    res = Image.alpha_composite(canvas, glow)
    res = Image.alpha_composite(res, overlay)
    return res


def draw_blade_ice_glaze(canvas, tip_x, tip_y, hilt_x, hilt_y, intensity=1.0):
    """Draw a translucent faceted glaze of Xuanbing (玄冰) coating the sword blade."""
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    dx = tip_x - hilt_x
    dy = tip_y - hilt_y
    length = math.hypot(dx, dy)
    if length < 5:
        return canvas
    
    nx = -dy / length
    ny = dx / length
    
    width = 9.0 * intensity
    
    p1 = (hilt_x - nx * width * 0.4, hilt_y - ny * width * 0.4)
    p2 = (hilt_x + nx * width * 0.4, hilt_y + ny * width * 0.4)
    p3 = (tip_x + nx * width * 0.9, tip_y + ny * width * 0.9)
    p4 = (tip_x + dx * 0.15, tip_y + dy * 0.15)  # sharp point extending beyond tip
    p5 = (tip_x - nx * width * 0.9, tip_y - ny * width * 0.9)
    
    # Outer frost glow
    draw.polygon([p1, p2, p3, p4, p5], fill=(COLOR_FROST_AZURE[0], COLOR_FROST_AZURE[1], COLOR_FROST_AZURE[2], int(150 * intensity)),
                 outline=(COLOR_GLACIAL_CYAN[0], COLOR_GLACIAL_CYAN[1], COLOR_GLACIAL_CYAN[2], int(220 * intensity)))
    
    # Sharp white central ridge
    draw.line([(hilt_x, hilt_y), (p4[0], p4[1])], fill=(255, 255, 255, int(240 * intensity)), width=2)
    
    glow = overlay.filter(ImageFilter.GaussianBlur(2.0))
    res = Image.alpha_composite(canvas, glow)
    res = Image.alpha_composite(res, overlay)
    return res


def draw_frost_cleave_arc(canvas, cx, cy, radius, y_squash=0.38, start_angle=-2.9, sweep=2.8,
                          tilt_deg=0.0, width=44, intensity=1.0):
    """Draw a wide horizontal freezing blade slash with razor-white core and glacial aura."""
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    steps = 50
    tilt_rad = math.radians(tilt_deg)
    cos_t, sin_t = math.cos(tilt_rad), math.sin(tilt_rad)
    
    # Multi-pass: Aura, Cyan blade, Pure white cutting edge
    passes = [
        ("aura", width * 1.5, COLOR_ICE_DEEP, 85, 4.0),
        ("body", width * 0.9, COLOR_FROST_AZURE, 180, 2.0),
        ("inner", width * 0.45, COLOR_GLACIAL_CYAN, 230, 1.0),
        ("edge", max(2, int(width * 0.16)), COLOR_ICE_WHITE, 255, 0.0)
    ]
    
    for pname, pwidth, pcolor, palpha, pblur in passes:
        pass_img = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        pdraw = ImageDraw.Draw(pass_img)
        
        for i in range(steps):
            t0 = i / float(steps)
            t1 = (i + 1) / float(steps)
            
            a0 = start_angle + sweep * t0
            a1 = start_angle + sweep * t1
            
            x0_raw = radius * math.cos(a0)
            y0_raw = radius * math.sin(a0) * y_squash
            x1_raw = radius * math.cos(a1)
            y1_raw = radius * math.sin(a1) * y_squash
            
            px0 = cx + x0_raw * cos_t - y0_raw * sin_t
            py0 = cy + x0_raw * sin_t + y0_raw * cos_t
            px1 = cx + x1_raw * cos_t - y1_raw * sin_t
            py1 = cy + x1_raw * sin_t + y1_raw * cos_t
            
            # Taper profile: thin at start, thick in middle, needle sharp at leading edge
            t_mid = 1.0 - math.pow(abs(t0 - 0.55) * 2.0, 1.8)
            cur_w = max(2, int(pwidth * t_mid * intensity))
            cur_a = int(palpha * math.pow(math.sin(t0 * math.pi), 0.6) * intensity)
            cur_a = min(255, max(0, cur_a))
            
            pdraw.line([(px0, py0), (px1, py1)], fill=(pcolor[0], pcolor[1], pcolor[2], cur_a), width=cur_w)
            
        if pblur > 0.1:
            pass_img = pass_img.filter(ImageFilter.GaussianBlur(pblur))
        overlay = Image.alpha_composite(overlay, pass_img)
        
    return Image.alpha_composite(canvas, overlay)


def draw_frost_ground_fissure_line(canvas, start_x, ground_y=437, end_x=660, intensity=1.0, seed=42):
    """
    Draw a devastating straight frost fissure line tearing across the floor (Active 2).
    Features ground-cracking ink line, upward crystal ice pillars, razor needles, and freezing mist.
    """
    np.random.seed(seed)
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    length = end_x - start_x
    if length <= 10:
        return canvas
        
    # 1. Base Ground Frost Path & Mist Ellipse
    draw.ellipse([(start_x - 10, ground_y - 12), (end_x + 15, ground_y + 12)],
                 fill=(COLOR_MIST[0], COLOR_MIST[1], COLOR_MIST[2], int(80 * intensity)))
    
    # 2. Main Ground Rupture Laser Line
    draw.line([(start_x, ground_y), (end_x, ground_y)],
              fill=(COLOR_GLACIAL_CYAN[0], COLOR_GLACIAL_CYAN[1], COLOR_GLACIAL_CYAN[2], int(240 * intensity)), width=5)
    draw.line([(start_x, ground_y), (end_x, ground_y)],
              fill=(255, 255, 255, int(255 * intensity)), width=2)
    
    # 3. Jagged Ice Spikes popping up along the line
    num_spikes = int(length / 28)
    for i in range(num_spikes):
        t = (i + np.random.uniform(0.1, 0.9)) / float(num_spikes)
        sp_x = start_x + t * length
        # Progressively larger spikes towards the target
        scale_t = 0.6 + 0.8 * math.sin(t * math.pi * 0.85)
        h = np.random.uniform(25, 58) * scale_t * intensity
        w = np.random.uniform(8, 16) * scale_t
        tilt = np.random.uniform(-0.25, 0.4)
        
        pts_left = [
            (sp_x - w, ground_y + 3),
            (sp_x, ground_y + 3),
            (sp_x + h * tilt, ground_y - h),
            (sp_x - w * 0.6, ground_y - h * 0.5)
        ]
        pts_right = [
            (sp_x, ground_y + 3),
            (sp_x + w, ground_y + 3),
            (sp_x + h * tilt + 2, ground_y - h),
            (sp_x + w * 0.5, ground_y - h * 0.4)
        ]
        
        # Faceted crystal rendering (shadow side & bright lit side)
        draw.polygon(pts_left, fill=(COLOR_ICE_DEEP[0], COLOR_ICE_DEEP[1], COLOR_ICE_DEEP[2], int(210 * intensity)),
                     outline=(COLOR_GLACIAL_CYAN[0], COLOR_GLACIAL_CYAN[1], COLOR_GLACIAL_CYAN[2], int(240 * intensity)))
        draw.polygon(pts_right, fill=(COLOR_GLACIAL_CYAN[0], COLOR_GLACIAL_CYAN[1], COLOR_GLACIAL_CYAN[2], int(220 * intensity)),
                     outline=(255, 255, 255, int(250 * intensity)))
        
        # Leading edge bright sparkle on top of largest spikes
        if h > 35 * intensity:
            draw.line([(sp_x + h * tilt - 4, ground_y - h), (sp_x + h * tilt + 4, ground_y - h)], fill=(255, 255, 255, 255), width=2)
            draw.line([(sp_x + h * tilt, ground_y - h - 4), (sp_x + h * tilt, ground_y - h + 4)], fill=(255, 255, 255, 255), width=2)
            
    # 4. Jagged ink fracture lines on bottom edge
    for i in range(12):
        fx = start_x + np.random.uniform(0, length)
        draw.line([(fx, ground_y), (fx + np.random.uniform(-15, 25), ground_y + np.random.uniform(3, 8))],
                  fill=(COLOR_INK_ACCENT[0], COLOR_INK_ACCENT[1], COLOR_INK_ACCENT[2], int(180 * intensity)), width=2)
                  
    glow = overlay.filter(ImageFilter.GaussianBlur(2.5))
    res = Image.alpha_composite(canvas, glow)
    res = Image.alpha_composite(res, overlay)
    return res


def draw_frost_shards_and_mist(canvas, cx, cy, count=18, radius=70, intensity=1.0, seed=7):
    """Draw flying diamond ice crystal shards and frost vapor."""
    np.random.seed(seed)
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    for i in range(count):
        dist = np.random.uniform(10, radius)
        ang = np.random.uniform(0, 2 * math.pi)
        px = cx + dist * math.cos(ang)
        py = cy + dist * math.sin(ang)
        
        sz = np.random.uniform(2, 6) * intensity
        # Diamond shape
        draw.polygon([(px - sz, py), (px, py - sz * 1.4), (px + sz, py), (px, py + sz * 1.4)],
                     fill=(COLOR_ICE_WHITE[0], COLOR_ICE_WHITE[1], COLOR_ICE_WHITE[2], int(230 * intensity)),
                     outline=(COLOR_GLACIAL_CYAN[0], COLOR_GLACIAL_CYAN[1], COLOR_GLACIAL_CYAN[2], int(180 * intensity)))
                     
    glow = overlay.filter(ImageFilter.GaussianBlur(1.5))
    res = Image.alpha_composite(canvas, glow)
    res = Image.alpha_composite(res, overlay)
    return res


def build_yijianshuanghan_sprites():
    """Main production pipeline for non-enhanced Yijianshuanghan (一剑霜寒 QF-3)."""
    print("=================================================================")
    print("Crafting Qingfeng Skill 3: 一剑霜寒 (QF-3) 8-Phase Sprites")
    print("=================================================================")
    
    # 8-Phase Definition
    frame_defs = [
        (1, "01_沉步凝渊", "Grounding & Settle",
         os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Block", "block-1.png")),
        (2, "02_霜华引刃", "Frost Influx",
         os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Attack", "attack-5.png")),
        (3, "03_蓄力凝冰", "Deep Charge",
         os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "HeavyThrust", "heavy-1.png")),
        (4, "04_惊雷裂斩", "Thunderous Cleave",
         os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Attack", "attack-3.png")),
        (5, "05_霜线疾行", "Frost Line Surge",
         os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "HeavyThrust", "heavy-4.png")),
        (6, "06_踏雪止势", "Step & Lock",
         os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "HeavyThrust", "heavy-7.png")),
        (7, "07_振刃碎冰", "Flick & Shatter",
         os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Attack", "attack-12.png")),
        (8, "08_拂袖归渊", "Sheathe & Restore",
         os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Attack", "attack-4.png")),
    ]
    
    generated_frames = []
    
    for idx, cname, ename, src_path in frame_defs:
        print(f"Crafting Frame {idx}: {cname} ({ename}) from {os.path.basename(src_path)}...")
        
        # 1. Base Body Aligned to 680x480, Feet Y=437, Center X=340
        body = align_body_to_canvas(src_path, target_feet_y=TARGET_FEET_Y, center_x=CENTER_X)
        
        bg_vfx = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        fg_vfx = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        
        if idx == 1:
            # F1: 沉步凝渊 (block-1) - 坚固下沉马步，双手抱剑横胸，立地生根
            # 地表初结微霜与细碎冰晶
            bg_vfx = draw_ground_frost_crystals(bg_vfx, cx=335, ground_y=437, radius=55, count=6, intensity=0.85, seed=101)
            fg_vfx = draw_frost_star_glint(fg_vfx, gx=365, gy=265, size=16, intensity=0.9)
            fg_vfx = draw_frost_shards_and_mist(fg_vfx, cx=340, cy=380, count=8, radius=45, intensity=0.7, seed=111)
            
        elif idx == 2:
            # F2: 霜华引刃 (attack-5) - 双手提剑举于肩侧，极寒冻气化作漩涡向剑身汇聚
            bg_vfx = draw_ground_frost_crystals(bg_vfx, cx=350, ground_y=437, radius=75, count=9, intensity=1.05, seed=202)
            # 剑刃覆薄冰
            fg_vfx = draw_blade_ice_glaze(fg_vfx, tip_x=475, tip_y=230, hilt_x=380, hilt_y=305, intensity=0.9)
            fg_vfx = draw_frost_star_glint(fg_vfx, gx=475, gy=230, size=22, intensity=1.15)
            fg_vfx = draw_frost_shards_and_mist(fg_vfx, cx=440, cy=250, count=14, radius=65, intensity=0.9, seed=222)
            
        elif idx == 3:
            # F3: 蓄力凝冰 (heavy-1) - 极度下潜蓄势（可蓄至45f），剑身凝结玄冰琉璃晶层，地表蔓延冰裂，韧体护身
            bg_vfx = draw_ground_frost_crystals(bg_vfx, cx=340, ground_y=437, radius=110, count=14, intensity=1.35, seed=303)
            fg_vfx = draw_blade_ice_glaze(fg_vfx, tip_x=530, tip_y=270, hilt_x=350, hilt_y=310, intensity=1.4)
            fg_vfx = draw_frost_star_glint(fg_vfx, gx=530, gy=270, size=30, intensity=1.5)
            fg_vfx = draw_frost_shards_and_mist(fg_vfx, cx=450, cy=300, count=22, radius=85, intensity=1.2, seed=333)
            
        elif idx == 4:
            # F4: 惊雷裂斩 (attack-3) - 【核心斩击 Active 1】全身扭腰爆发超大弧度水平横斩！纯白极亮寒刃破空
            # 超宽幅水平横斩寒刃
            bg_vfx = draw_frost_cleave_arc(bg_vfx, cx=340, cy=290, radius=245, y_squash=0.38,
                                           start_angle=-2.9, sweep=2.9, tilt_deg=-2.0, width=54, intensity=1.4)
            fg_vfx = draw_frost_cleave_arc(fg_vfx, cx=340, cy=290, radius=245, y_squash=0.38,
                                           start_angle=-0.7, sweep=0.9, tilt_deg=-2.0, width=54, intensity=1.3)
            fg_vfx = draw_frost_star_glint(fg_vfx, gx=565, gy=285, size=34, intensity=1.6)
            fg_vfx = draw_frost_shards_and_mist(fg_vfx, cx=530, cy=285, count=28, radius=110, intensity=1.4, seed=444)
            
        elif idx == 5:
            # F5: 霜线疾行 (heavy-4) - 【核心破防 Active 2】贴地狂飙2.6m笔直破空霜线，地表破土拔起整排锐利冰棱
            # 贴地向前撕裂延伸的长直线冰棱与裂纹
            bg_vfx = draw_frost_ground_fissure_line(bg_vfx, start_x=260, ground_y=437, end_x=665, intensity=1.45, seed=505)
            fg_vfx = draw_blade_ice_glaze(fg_vfx, tip_x=590, tip_y=295, hilt_x=340, hilt_y=300, intensity=1.2)
            fg_vfx = draw_frost_star_glint(fg_vfx, gx=610, gy=295, size=32, intensity=1.5)
            fg_vfx = draw_frost_shards_and_mist(fg_vfx, cx=500, cy=410, count=25, radius=100, intensity=1.3, seed=555)
            
        elif idx == 6:
            # F6: 踏雪止势 (heavy-7) - 前弓步踏实地面卸力，双手持剑滞空微震，前方地面留厚重冰带与袅袅冰雾
            bg_vfx = draw_ground_frost_crystals(bg_vfx, cx=350, ground_y=437, radius=95, count=10, intensity=1.1, seed=606)
            fg_vfx = draw_blade_ice_glaze(fg_vfx, tip_x=440, tip_y=285, hilt_x=320, hilt_y=310, intensity=0.9)
            fg_vfx = draw_frost_star_glint(fg_vfx, gx=440, gy=285, size=20, intensity=1.1)
            fg_vfx = draw_frost_shards_and_mist(fg_vfx, cx=380, cy=350, count=14, radius=60, intensity=0.85, seed=666)
            
        elif idx == 7:
            # F7: 振刃碎冰 (attack-12) - 手腕轻抖挽剑，剑身微震震碎残余薄冰，冰晶碎片与寒气四溅
            fg_vfx = draw_frost_cleave_arc(fg_vfx, cx=365, cy=290, radius=80, y_squash=0.7,
                                           start_angle=-1.5, sweep=2.4, tilt_deg=-15.0, width=22, intensity=0.85)
            fg_vfx = draw_frost_star_glint(fg_vfx, gx=380, gy=260, size=18, intensity=1.0)
            fg_vfx = draw_frost_shards_and_mist(fg_vfx, cx=380, cy=270, count=18, radius=65, intensity=1.15, seed=777)
            
        elif idx == 8:
            # F8: 拂袖归渊 (attack-4) - 双手收剑入怀，秋水敛锋入鞘，衣摆自然垂落，地表霜痕淡化，无缝衔接待机
            fg_vfx = draw_frost_star_glint(fg_vfx, gx=360, gy=290, size=14, intensity=0.8)
            fg_vfx = draw_frost_shards_and_mist(fg_vfx, cx=350, cy=360, count=6, radius=40, intensity=0.6, seed=888)
            
        # Composite layers: BG VFX -> Body -> FG VFX
        final_frame = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        final_frame = Image.alpha_composite(final_frame, bg_vfx)
        final_frame = Image.alpha_composite(final_frame, body)
        final_frame = Image.alpha_composite(final_frame, fg_vfx)
        
        generated_frames.append((idx, cname, final_frame))
        
        # Save individual standard and named frames
        fn_std = f"yijianshuanghan-{idx}.png"
        fn_named = f"{cname}.png"
        fn_aligned = f"aligned_{cname}.png"
        
        final_frame.save(os.path.join(UNITY_DIR, fn_std))
        final_frame.save(os.path.join(CLEAN_DIR, fn_std))
        final_frame.save(os.path.join(CLEAN_DIR, fn_named))
        final_frame.save(os.path.join(CLEAN_DIR, fn_aligned))
        final_frame.save(os.path.join(SKILL_DIR, fn_std))
        final_frame.save(os.path.join(SKILL_DIR, fn_named))
        
    print(f"Saved 8 individual frames to {UNITY_DIR} and {SKILL_DIR}")
    
    # Build 5440x480 Sequence Strip
    strip = Image.new('RGBA', (CANVAS_W * 8, CANVAS_H), (0, 0, 0, 0))
    for idx, cname, fr in generated_frames:
        strip.paste(fr, ((idx - 1) * CANVAS_W, 0), fr)
        
    strip.save(os.path.join(UNITY_DIR, "yijianshuanghan-sequence.png"))
    strip.save(os.path.join(SKILL_DIR, "yijianshuanghan-sequence.png"))
    strip.save(os.path.join(CLEAN_DIR, "yijianshuanghan-sequence.png"))
    print(f"Sequence strip updated: {strip.size}")
    
    # Build Dark BG Preview for easy inspection
    dark_strip = Image.new('RGB', (CANVAS_W * 8, CANVAS_H), (10, 16, 22))
    dark_strip.paste(strip, (0, 0), strip)
    dark_strip.save(os.path.join(SKILL_DIR, "yijianshuanghan-darkbg-preview.png"))
    
    # Build Transparent Animated GIF (60 FPS feel, durations per frame)
    # Timings: F1=100ms, F2=120ms, F3=150ms (charge), F4=80ms (explosive cleave),
    #          F5=100ms (frost surge), F6=120ms, F7=120ms, F8=150ms
    frame_durations = [100, 120, 150, 80, 100, 120, 120, 150]
    
    gif_frames = []
    for (idx, cname, fr), dur in zip(generated_frames, frame_durations):
        # Convert RGBA to P with alpha transparency mask
        alpha = fr.split()[3]
        mask = Image.eval(alpha, lambda a: 255 if a > 30 else 0)
        p_frame = fr.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        
        final_gif_fr = Image.new('P', p_frame.size, 255)
        final_gif_fr.paste(p_frame, (0, 0), mask)
        final_gif_fr.info['transparency'] = 255
        gif_frames.append(final_gif_fr)
        
    for gpath in [os.path.join(UNITY_DIR, "yijianshuanghan-animation.gif"),
                  os.path.join(SKILL_DIR, "yijianshuanghan-animation.gif"),
                  os.path.join(CLEAN_DIR, "yijianshuanghan-animation.gif"),
                  os.path.join(SKILL_DIR, "animation.gif")]:
        gif_frames[0].save(
            gpath,
            save_all=True,
            append_images=gif_frames[1:],
            duration=frame_durations,
            loop=0,
            disposal=2,
            transparency=255
        )
    print(f"Animated GIF updated successfully.")

if __name__ == '__main__':
    build_yijianshuanghan_sprites()
