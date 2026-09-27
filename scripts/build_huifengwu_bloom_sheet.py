#!/usr/bin/env python3
"""
Generate Cinematic VFX Master Blueprint Sheet for Sword Intent Bloom: Whirling Wind Dance
(刀影江湖 · 青锋剑派【剑意绽放·回风舞（青鸾风暴 QF-2E）】电影级特效全案设计图)

Output:
- 1920x1080 Full HD Master Cinematic Production Board
- Multi-zone layout:
  * Zone 1: Main Cinematic Concept Key Visual (青鸾凌虚·双月绝杀·黑洞剑域)
  * Zone 2: 6-Pass Layer Breakdown Panels (六大特效通道解构)
  * Zone 3: 60 FPS Frame Timeline & Combat Data (时序曲线与战斗数值)
  * Zone 4: Color Palette & Shader Directives (色彩规范与渲染参数)
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CANVAS_W = 1920
CANVAS_H = 1080

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_SKILL_DIR = os.path.join(PROJECT_ROOT, "设计", "青锋技能帧序列", "02_回风舞")
OUT_UNITY_DIR = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Skills", "Huifengwu")
os.makedirs(OUT_SKILL_DIR, exist_ok=True)
os.makedirs(OUT_UNITY_DIR, exist_ok=True)

# Fonts
FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 32)
FONT_SUBTITLE = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
FONT_SECTION = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
FONT_BODY = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 12)
FONT_NUM = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)

def draw_rounded_rect(draw, box, radius=8, fill=(16, 24, 32, 220), outline=(46, 229, 212, 120), width=1):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)

def draw_starburst(draw, cx, cy, size=30, intensity=1.0, color=(255, 255, 255)):
    hl = size * 1.6
    vl = size * 1.1
    # Main rays
    draw.line([(cx - hl, cy), (cx + hl, cy)], fill=(color[0], color[1], color[2], int(255 * intensity)), width=2)
    draw.line([(cx, cy - vl), (cx, cy + vl)], fill=(color[0], color[1], color[2], int(255 * intensity)), width=2)
    # Diag rays
    dl = size * 0.7
    draw.line([(cx - dl, cy - dl), (cx + dl, cy + dl)], fill=(46, 229, 212, int(200 * intensity)), width=1)
    draw.line([(cx - dl, cy + dl), (cx + dl, cy - dl)], fill=(46, 229, 212, int(200 * intensity)), width=1)
    # Diamond core
    cr = size * 0.35
    draw.polygon([(cx - cr, cy), (cx, cy - cr), (cx + cr, cy), (cx, cy + cr)], fill=(255, 255, 255, 255))

def draw_crescent(draw, cx, cy, radius, y_squash=0.45, start_angle=-2.8, sweep=3.0, width=36, color=(46, 229, 212, 220)):
    steps = 40
    angles = np.linspace(start_angle, start_angle + sweep, steps)
    pts_out = []
    pts_in = []
    for a in angles:
        t = (a - angles[0]) / (angles[-1] - angles[0])
        w = (math.sin(t * math.pi) ** 0.75) * width
        ro = radius + w * 0.35
        ri = radius - w * 0.65
        pts_out.append((cx + ro * math.cos(a), cy + ro * math.sin(a) * y_squash))
        pts_in.append((cx + ri * math.cos(a), cy + ri * math.sin(a) * y_squash))
    poly = pts_out + pts_in[::-1]
    if len(poly) > 3:
        draw.polygon(poly, fill=color)

def draw_phoenix_wing(canvas, origin_x, origin_y, is_right=False, scale=1.0):
    """Draw an ethereal glowing Cyan Phoenix wing with layered feathers."""
    overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    dir_x = 1.0 if is_right else -1.0
    
    # 8 Primary blade feathers
    for i in range(8):
        t = i / 7.0
        angle = -0.3 + t * 0.95
        feather_len = (180 + math.sin(t * math.pi) * 140) * scale
        
        # Feather root & tip
        rx = origin_x + dir_x * (t * 60 * scale)
        ry = origin_y + (t * 40 * scale)
        tx = rx + dir_x * math.cos(angle) * feather_len
        ty = ry - math.sin(angle) * feather_len * 0.8
        
        # Draw feather blade polygon
        cx1 = rx + dir_x * math.cos(angle + 0.15) * (feather_len * 0.5)
        cy1 = ry - math.sin(angle + 0.15) * (feather_len * 0.5 * 0.8) + 12
        cx2 = rx + dir_x * math.cos(angle - 0.15) * (feather_len * 0.5)
        cy2 = ry - math.sin(angle - 0.15) * (feather_len * 0.5 * 0.8) - 12
        
        feather_poly = [(rx, ry), (cx1, cy1), (tx, ty), (cx2, cy2)]
        
        # Outer cyan glow
        draw.polygon(feather_poly, fill=(46, 229, 212, 130))
        # Inner white/gold spine
        draw.line([(rx, ry), (tx, ty)], fill=(255, 235, 150, 220), width=2)
        # Tip starlet
        draw.ellipse([(tx - 3, ty - 3), (tx + 3, ty + 3)], fill=(255, 255, 255, 255))
        
    glow = overlay.filter(ImageFilter.GaussianBlur(3.5))
    res = Image.alpha_composite(canvas, glow)
    res = Image.alpha_composite(res, overlay)
    return res

def build_master_sheet():
    print("=== Generating Cinematic VFX Master Blueprint (1920x1080) ===")
    
    # Base dark cinematic background with subtle gradient
    bg = Image.new('RGBA', (CANVAS_W, CANVAS_H), (10, 15, 20, 255))
    draw = ImageDraw.Draw(bg)
    
    # 1. Subtle radial gradient spotlight on left main visual
    spotlight = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(spotlight)
    sdraw.ellipse([(150, 150), (1050, 950)], fill=(16, 52, 64, 90))
    spotlight = spotlight.filter(ImageFilter.GaussianBlur(60))
    bg = Image.alpha_composite(bg, spotlight)
    draw = ImageDraw.Draw(bg)
    
    # Tech grid lines (subtle blueprint background)
    for x in range(0, CANVAS_W, 60):
        draw.line([(x, 0), (x, CANVAS_H)], fill=(25, 38, 48, 40), width=1)
    for y in range(0, CANVAS_H, 60):
        draw.line([(0, y), (CANVAS_W, y)], fill=(25, 38, 48, 40), width=1)
        
    # =========================================================================
    # HEADER BANNER (Top: 0 ~ 90px)
    # =========================================================================
    draw.rectangle([(0, 0), (CANVAS_W, 80)], fill=(8, 14, 18, 240))
    draw.line([(0, 80), (CANVAS_W, 80)], fill=(46, 229, 212, 180), width=2)
    
    # Title & tags
    draw.text((36, 16), "刀影江湖 · 青锋剑派【剑意绽放 · 回风舞（青鸾风暴 QF-2E）】电影级特效全案设计图", fill=(255, 255, 255), font=FONT_TITLE)
    draw.text((38, 54), "CINEMATIC VFX MASTER BLUEPRINT · SWORD INTENT BLOOM · WHIRLING WIND DANCE · CYAN PHOENIX STORM", fill=(46, 229, 212), font=FONT_SUBTITLE)
    
    # Right badge
    draw_rounded_rect(draw, (CANVAS_W - 280, 18, CANVAS_W - 36, 62), radius=6, fill=(18, 38, 46, 240), outline=(255, 223, 120, 200), width=1)
    draw.text((CANVAS_W - 262, 28), "★ 终极剑意绽放形态 5.5x", fill=(255, 223, 120), font=FONT_SECTION)
    
    # =========================================================================
    # ZONE 1: MAIN CINEMATIC CONCEPT KEY VISUAL (Left Area: x 36..1180, y 100..740)
    # =========================================================================
    main_box = (36, 100, 1200, 750)
    draw_rounded_rect(draw, main_box, radius=12, fill=(12, 18, 24, 220), outline=(46, 229, 212, 100), width=1)
    
    # Tag
    draw.rectangle([(36, 100), (280, 134)], fill=(18, 40, 48, 240))
    draw.text((48, 106), "主视觉概念核心 (KEY VISUAL)", fill=(46, 229, 212), font=FONT_SECTION)
    draw.text((300, 108), "意象：青鸾凌虚 · 双月绝杀 · 黑洞引力剑域 (直径 4.4m)", fill=(180, 205, 215), font=FONT_BODY)
    
    # Center of character in main visual
    mc_x, mc_y = 600, 440
    
    # Pass 0: Ground Taiji ink domain (flat ellipse at feet)
    feet_y = 620
    for r in range(40, 280, 20):
        alpha = int(90 * (1.0 - r / 280.0))
        draw.arc([(mc_x - r, feet_y - int(r * 0.28)), (mc_x + r, feet_y + int(r * 0.28))],
                 start=0, end=360, fill=(18, 52, 64, alpha), width=3)
    # Concentric runes
    draw.ellipse([(mc_x - 220, feet_y - 60), (mc_x + 220, feet_y + 60)], outline=(46, 229, 212, 140), width=2)
    draw.ellipse([(mc_x - 140, feet_y - 38), (mc_x + 140, feet_y + 38)], outline=(255, 223, 120, 160), width=2)
    draw.text((mc_x - 110, feet_y + 40), "[Pass 0: 乾坤太极青鸾磨盘阵 · 直径 4.4m 绝对掌控]", fill=(46, 229, 212), font=FONT_SMALL)
    
    # Pass 1: Suction Core (Black Hole Vortex)
    draw.ellipse([(mc_x - 55, mc_y - 10), (mc_x + 55, mc_y + 100)], fill=(6, 10, 14, 230), outline=(46, 229, 212, 180), width=2)
    # Suction rays
    for i in range(12):
        ang = i * (math.pi / 6)
        r_in = 60
        r_out = 200
        sx = mc_x + math.cos(ang) * r_out
        sy = mc_y + 45 + math.sin(ang) * (r_out * 0.45)
        ex = mc_x + math.cos(ang + 0.3) * r_in
        ey = mc_y + 45 + math.sin(ang + 0.3) * (r_in * 0.45)
        draw.line([(sx, sy), (ex, ey)], fill=(46, 229, 212, 100), width=2)
    draw.text((mc_x - 85, mc_y + 105), "[Pass 1: 6.0m/s 引力黑洞核心]", fill=(200, 230, 240), font=FONT_SMALL)
    
    # Pass 3: Draw Ethereal Phoenix Wings behind swordsman
    bg = draw_phoenix_wing(bg, origin_x=mc_x - 50, origin_y=mc_y - 20, is_right=False, scale=1.3)
    bg = draw_phoenix_wing(bg, origin_x=mc_x + 50, origin_y=mc_y - 20, is_right=True, scale=1.3)
    draw = ImageDraw.Draw(bg)
    draw.text((mc_x - 120, mc_y - 190), "【Pass 3: 青鸾神鸟法相 · 翼展 4.4m 剑意凌虚】", fill=(255, 235, 140), font=FONT_SECTION)
    
    # Draw Swordsman Character Pose (Attack 11 high-res crop)
    player_src_path = os.path.join(PROJECT_ROOT, "New Tuanjie Project", "Assets", "Sprites", "Player", "Attack", "attack-11.png")
    if os.path.exists(player_src_path):
        p_img = Image.open(player_src_path).convert('RGBA')
        # Scale to fit nicely
        pw, ph = p_img.size
        target_pw = 460
        target_ph = int(ph * (target_pw / pw))
        p_resized = p_img.resize((target_pw, target_ph), Image.Resampling.LANCZOS)
        # Paste onto character center
        bg.paste(p_resized, (mc_x - target_pw // 2 + 10, feet_y - int(target_ph * 0.88)), p_resized)
        draw = ImageDraw.Draw(bg)
        
    # Pass 2: Foreground Double Crescent Cross-Slashes
    # Slash A: Massive Horizontal Crescent
    vfx_overlay = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vfx_overlay)
    draw_crescent(vdraw, cx=mc_x, cy=mc_y + 35, radius=290, y_squash=0.38, start_angle=-3.0, sweep=3.1, width=58, color=(46, 229, 212, 220))
    # Slash B: Intersecting Diagonal Crescent
    draw_crescent(vdraw, cx=mc_x, cy=mc_y + 15, radius=260, y_squash=0.48, start_angle=-2.4, sweep=2.6, width=52, color=(255, 223, 120, 230))
    # Rotate Slash B
    vfx_overlay = vfx_overlay.rotate(36, center=(mc_x, mc_y + 20), resample=Image.BICUBIC)
    vdraw = ImageDraw.Draw(vfx_overlay)
    
    # Intersection Burst Starburst
    draw_starburst(vdraw, mc_x + 130, mc_y + 30, size=52, intensity=1.8, color=(255, 255, 255))
    
    # Radiating Blade Petals (青鸾剑羽)
    for i in range(24):
        ang = i * (math.pi / 12) + 0.15
        dist = 180 + (i % 3) * 65
        px = mc_x + math.cos(ang) * dist
        py = mc_y + math.sin(ang) * (dist * 0.55)
        # Petal diamond
        p_color = (255, 235, 140, 240) if i % 2 == 0 else (46, 229, 212, 240)
        vdraw.polygon([(px - 4, py), (px, py - 9), (px + 4, py), (px, py + 9)], fill=p_color)
        
    glow_vfx = vfx_overlay.filter(ImageFilter.GaussianBlur(3.0))
    bg = Image.alpha_composite(bg, glow_vfx)
    bg = Image.alpha_composite(bg, vfx_overlay)
    draw = ImageDraw.Draw(bg)
    
    # Callout labels on main visual
    def draw_callout(start_pt, end_pt, text_val, sub_val=""):
        draw.line([start_pt, (end_pt[0], start_pt[1]), end_pt], fill=(46, 229, 212, 200), width=1)
        draw.ellipse([(start_pt[0] - 3, start_pt[1] - 3), (start_pt[0] + 3, start_pt[1] + 3)], fill=(255, 223, 120, 255))
        draw_rounded_rect(draw, (end_pt[0] - 8, end_pt[1] - 14, end_pt[0] + 240, end_pt[1] + 28), radius=4, fill=(10, 20, 28, 230), outline=(46, 229, 212, 140))
        draw.text((end_pt[0] + 4, end_pt[1] - 10), text_val, fill=(255, 255, 255), font=FONT_BODY)
        if sub_val:
            draw.text((end_pt[0] + 4, end_pt[1] + 8), sub_val, fill=(46, 229, 212), font=FONT_SMALL)

    draw_callout((mc_x + 130, mc_y + 30), (mc_x + 320, mc_y - 30), "双重残月交叉绝杀核心", "Pass 2: 1.4x+8破韧 / 0.04s 强顿帧")
    draw_callout((mc_x - 220, mc_y - 80), (mc_x - 490, mc_y - 120), "神禽青鸾神羽法相", "Pass 3: 翼展4.4m / 24枚破空飞羽")
    draw_callout((mc_x - 120, feet_y), (mc_x - 390, feet_y + 30), "空间引力黑洞磨盘阵", "Pass 0+1: 6.0m/s 引力真空强聚怪")

    # =========================================================================
    # ZONE 2: 6-PASS CINEMATIC LAYER BREAKDOWN (Right Column: x 1230..1884, y 100..1044)
    # =========================================================================
    side_box = (1230, 100, 1884, 1044)
    draw_rounded_rect(draw, side_box, radius=12, fill=(12, 18, 24, 220), outline=(46, 229, 212, 100), width=1)
    
    draw.rectangle([(1230, 100), (1500, 134)], fill=(18, 40, 48, 240))
    draw.text((1245, 106), "六大电影级特效通道解构", fill=(46, 229, 212), font=FONT_SECTION)
    
    passes = [
        ("Pass 0: 乾坤太极青鸾磨盘阵 (Ground Domain)",
         "半径 2.2m (直径 4.4m) 双层太极阴阳水墨地贴，地面裂痕泵送青金地气脉冲。",
         "Shader: Decal AlphaBlend | Normal Perturb | 60 FPS 贴地旋转"),
        
        ("Pass 1: 6.0m/s 引力真空黑洞 (Vortex Core)",
         "中心 0.8m 暗核空间塌缩，全角度产生折射热浪透镜扭曲，强行牵引杂兵入阵。",
         "Shader: GrabPass Screen Refraction | Multi-Target Velocity Force"),
         
        ("Pass 2: 五重狂草残月斩幕 (5-Hit Slash Curtain)",
         "五道独立轨迹两端锐利渐缩月牙刀浪：横扫 -> 挑空 -> 怒劈 -> 飞旋 -> 交叉绝杀。",
         "Shader: Additive Core + Multiply Ink Plume | 0.04s Chrono Hitstop"),
         
        ("Pass 3: 青鸾神鸟法相与飞羽剑雨 (Phoenix Avatar)",
         "F4~F5 腾空 +0.22m 时身后展开 4.4m 半透青鸾羽翼，向下倾泻 24 枚离心剑羽飞刃。",
         "Shader: Ethereal Fresnel Glow | Mesh Particle Blade Rain"),
         
        ("Pass 4: 时空碎裂与超新星爆 (Spatial Shatter)",
         "斩击交汇命中时爆发虚空冰裂晶片与四角十字极光星芒，伴随屏幕微色相分离。",
         "Shader: Chromatic Aberration 0.35 | Radial Flare Sprite 256px"),
         
        ("Pass 5: 侧步沉剑定地冲击波 (Ground Cleave Shock)",
         "F6 剑尖重插地面，笔锋顿止！地面裂开 3.0m 直线青墨地缝，环形激波外扩 3.2m。",
         "Shader: Shockwave Ring Expander | Sub-Bass Shake Magnitude 0.28")
    ]
    
    py_start = 145
    p_height = 142
    for p_idx, (p_title, p_desc, p_tech) in enumerate(passes):
        p_box = (1248, py_start + p_idx * p_height, 1866, py_start + (p_idx + 1) * p_height - 12)
        draw_rounded_rect(draw, p_box, radius=6, fill=(16, 26, 34, 230), outline=(46, 229, 212, 70), width=1)
        
        # Mini icon badge
        badge_color = (255, 223, 120) if p_idx in [2, 3] else (46, 229, 212)
        draw.rectangle([(p_box[0] + 8, p_box[1] + 8), (p_box[0] + 14, p_box[1] + 24)], fill=badge_color)
        draw.text((p_box[0] + 20, p_box[1] + 8), p_title, fill=(255, 255, 255), font=FONT_SECTION)
        draw.text((p_box[0] + 20, p_box[1] + 38), p_desc, fill=(190, 215, 225), font=FONT_BODY)
        draw.text((p_box[0] + 20, p_box[1] + 66), p_tech, fill=(46, 229, 212), font=FONT_SMALL)
        
        # Mini schematic visual on right side of pass box
        icon_cx = p_box[2] - 50
        icon_cy = p_box[1] + 45
        if p_idx == 0:
            draw.ellipse([(icon_cx - 24, icon_cy - 12), (icon_cx + 24, icon_cy + 12)], outline=(46, 229, 212), width=2)
            draw.ellipse([(icon_cx - 12, icon_cy - 6), (icon_cx + 12, icon_cy + 6)], outline=(255, 223, 120), width=1)
        elif p_idx == 1:
            draw.ellipse([(icon_cx - 16, icon_cy - 16), (icon_cx + 16, icon_cy + 16)], fill=(6, 12, 16), outline=(46, 229, 212), width=2)
        elif p_idx == 2:
            draw_crescent(draw, icon_cx, icon_cy, radius=26, y_squash=0.6, start_angle=-2.5, sweep=2.5, width=8, color=(46, 229, 212, 255))
        elif p_idx == 3:
            draw.polygon([(icon_cx - 20, icon_cy + 10), (icon_cx, icon_cy - 20), (icon_cx + 20, icon_cy + 10), (icon_cx, icon_cy)], fill=(255, 223, 120, 200))
        elif p_idx == 4:
            draw_starburst(draw, icon_cx, icon_cy, size=18, intensity=1.5, color=(255, 255, 255))
        elif p_idx == 5:
            draw.line([(icon_cx - 25, icon_cy), (icon_cx + 25, icon_cy)], fill=(46, 229, 212), width=3)
            draw.line([(icon_cx - 10, icon_cy - 15), (icon_cx - 10, icon_cy + 15)], fill=(255, 255, 255), width=2)
            
    # =========================================================================
    # ZONE 3: 60 FPS TIMELINE & COMBAT METRICS (Bottom Left: x 36..680, y 765..1044)
    # =========================================================================
    tl_box = (36, 765, 680, 1044)
    draw_rounded_rect(draw, tl_box, radius=12, fill=(12, 18, 24, 220), outline=(46, 229, 212, 100), width=1)
    
    draw.rectangle([(36, 765), (280, 799)], fill=(18, 40, 48, 240))
    draw.text((48, 771), "60 FPS 电影级时序曲线", fill=(46, 229, 212), font=FONT_SECTION)
    
    # 3-Phase timeline bar
    bar_x, bar_y, bar_w, bar_h = 56, 815, 590, 26
    # Startup 10f (10/37 ~ 27%)
    w_start = int(bar_w * (10 / 37.0))
    draw.rectangle([(bar_x, bar_y), (bar_x + w_start, bar_y + bar_h)], fill=(28, 54, 68))
    draw.text((bar_x + 12, bar_y + 4), "起势蓄劲 1~10f (霸体+引力)", fill=(200, 230, 240), font=FONT_SMALL)
    
    # Active 9f (9/37 ~ 24%)
    w_act = int(bar_w * (9 / 37.0))
    draw.rectangle([(bar_x + w_start, bar_y), (bar_x + w_start + w_act, bar_y + bar_h)], fill=(255, 180, 40))
    draw.text((bar_x + w_start + 8, bar_y + 4), "五重残月斩 11~19f", fill=(10, 15, 20), font=FONT_SMALL)
    
    # Recovery 18f (18/37 ~ 49%)
    w_rec = bar_w - w_start - w_act
    draw.rectangle([(bar_x + w_start + w_act, bar_y), (bar_x + bar_w, bar_y + bar_h)], fill=(20, 36, 46))
    draw.text((bar_x + w_start + w_act + 12, bar_y + 4), "沉剑定地 20~24f (可取消) -> 挽花入鞘 25~37f", fill=(180, 205, 215), font=FONT_SMALL)
    
    # Numerical data cards
    metrics = [
        ("伤害倍率", "5.5x", "55点综合伤害 (0.8x*5 + 1.5x爆鸣)"),
        ("破韧击倒", "32 点", "打断一切非霸体杂兵抬手并强力浮空"),
        ("霸体护甲", "完全霸体", "1~22 帧全程霸体，免疫击退硬直"),
        ("黑洞引力", "6.0 m/s", "覆盖 4.4m 直径范围绝对真空牵引")
    ]
    
    for m_idx, (m_lbl, m_val, m_sub) in enumerate(metrics):
        col_x = 56 + (m_idx % 2) * 300
        row_y = 860 + (m_idx // 2) * 85
        draw_rounded_rect(draw, (col_x, row_y, col_x + 285, row_y + 75), radius=6, fill=(16, 26, 34, 230), outline=(46, 229, 212, 70))
        draw.text((col_x + 12, row_y + 8), m_lbl, fill=(160, 185, 195), font=FONT_SMALL)
        draw.text((col_x + 12, row_y + 26), m_val, fill=(255, 223, 120), font=FONT_NUM)
        draw.text((col_x + 12, row_y + 54), m_sub, fill=(46, 229, 212), font=FONT_SMALL)

    # =========================================================================
    # ZONE 4: COLOR PALETTE & SHADER DIRECTIVES (Bottom Middle: x 700..1200, y 765..1044)
    # =========================================================================
    cp_box = (700, 765, 1200, 1044)
    draw_rounded_rect(draw, cp_box, radius=12, fill=(12, 18, 24, 220), outline=(46, 229, 212, 100), width=1)
    
    draw.rectangle([(700, 765), (940, 799)], fill=(18, 40, 48, 240))
    draw.text((712, 771), "色彩规范与渲染着色器", fill=(46, 229, 212), font=FONT_SECTION)
    
    swatches = [
        ("炽白核心", "#FFFFFF", (255, 255, 255), "锋刃白热切割线、星爆核心、虚空裂片"),
        ("青鸾神金", "#FFDF78", (255, 223, 120), "绽放强化色、交叉斩爆发、翎羽高光"),
        ("极光青芒", "#2EE5D4", (46, 229, 212), "月牙斩体波、青鸾羽毛边缘、剑意气旋"),
        ("玄墨青渊", "#18B2DC", (24, 178, 220), "引力黑洞外圈、半透羽翼辉光、水雾"),
        ("焦墨重底", "#0C1217", (12, 18, 23), "挥毫飞白墨尾、太极阴阳底色、重墨")
    ]
    
    for s_idx, (s_name, s_hex, s_rgb, s_role) in enumerate(swatches):
        sy = 815 + s_idx * 44
        # Swatch block
        draw_rounded_rect(draw, (718, sy, 762, sy + 32), radius=4, fill=s_rgb, outline=(255, 255, 255, 120), width=1)
        draw.text((774, sy + 2), f"{s_name} {s_hex}", fill=(255, 255, 255), font=FONT_BODY)
        draw.text((774, sy + 18), s_role, fill=(160, 185, 195), font=FONT_SMALL)
        
    # Technical footer signature
    draw.line([(36, CANVAS_H - 24), (CANVAS_W - 36, CANVAS_H - 24)], fill=(46, 229, 212, 80), width=1)
    draw.text((38, CANVAS_H - 20), "刀影江湖 项目工程部 · 青锋剑派战斗视觉体系标准规范 (VFX SPEC REV 2.4)", fill=(100, 130, 140), font=FONT_SMALL)
    draw.text((CANVAS_W - 380, CANVAS_H - 20), "Strictly Aligned with 60 FPS FrameData & Unity Pipeline", fill=(100, 130, 140), font=FONT_SMALL)
    
    # Save output to skill folder and unity folder
    fn_master = "回风舞-剑意绽放-电影级特效全案设计图.jpg"
    fn_unity = "huifengwu_bloom_vfx_sheet.jpg"
    
    p_master = os.path.join(OUT_SKILL_DIR, fn_master)
    p_unity = os.path.join(OUT_UNITY_DIR, fn_unity)
    
    # Convert RGBA to RGB for clean high-Q JPG
    rgb_final = bg.convert('RGB')
    rgb_final.save(p_master, quality=95)
    rgb_final.save(p_unity, quality=95)
    print(f"Master Blueprint saved successfully to:\n  {p_master}\n  {p_unity}")
    
    # Note: Unity / Tuanjie Editor will automatically generate native .meta with valid GUID.
    print(f"Master blueprint saved to {p_skill} and {p_unity}")

if __name__ == '__main__':
    build_master_sheet()
