import os
from PIL import Image
import numpy as np

def clean_sprite_sheet(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    raw = Image.open(input_path).convert('RGB')
    arr = np.array(raw, dtype=np.float32)

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    # Calculate magenta strength
    # Pure magenta is (255, 0, 255)
    # Magenta distance in color space
    dist_to_magenta = np.sqrt((r - 255.0)**2 + (g - 0.0)**2 + (b - 255.0)**2)
    
    # Also evaluate magenta dominance: how much R and B exceed G
    min_rb = np.minimum(r, b)
    mag_dominance = min_rb - g  # High for magenta/pink/purple, low for neutral/cyan/black/white
    
    # Normalized color channels
    sum_rgb = r + g + b + 1e-5
    norm_g = g / sum_rgb
    norm_r = r / sum_rgb
    norm_b = b / sum_rgb

    # 1. Compute Alpha Matte
    # If dist_to_magenta is small OR (mag_dominance > 40 and norm_g < 0.22), it's background
    alpha = np.ones_like(r)
    
    # Definite background
    bg_mask = (dist_to_magenta < 160.0) | ((mag_dominance > 35.0) & (norm_g < 0.25))
    
    # Smooth alpha falloff near boundaries
    # Transition zone between dist 140 and 220
    alpha = np.clip((dist_to_magenta - 90.0) / 110.0, 0.0, 1.0)
    # Hard zero for definite background
    alpha[bg_mask & (dist_to_magenta < 170.0)] = 0.0
    alpha[mag_dominance > 75.0] = 0.0

    # 2. Despill: aggressively strip any magenta / pink hue from foreground edges!
    # Foreground should NEVER have high R and high B with very low G unless it's pure white
    # In Qingfeng (blue robes, black ink, cyan glowing sword):
    # If a pixel has mag_dominance > 0, suppress R and B towards G or Cyan
    clean_r = r.copy()
    clean_g = g.copy()
    clean_b = b.copy()

    # Detect edge/semi-transparent pixels with magenta contamination
    spill = np.maximum(0.0, mag_dominance)
    
    # Suppress magenta: bring R and B closer to G
    # For sword energy (cyan: G and B are high, R is low), do not suppress B if G is high!
    # Cyan check: g > 100 and b > 100 and r < g
    is_cyan = (g > 80.0) & (b > 80.0) & (r < g + 30.0)
    
    # For non-cyan pixels with magenta spill, suppress both R and B
    non_cyan_spill = spill * (~is_cyan)
    clean_r -= non_cyan_spill * 1.2
    clean_b -= non_cyan_spill * 0.8
    
    # Clamp
    clean_r = np.clip(clean_r, 0.0, 255.0)
    clean_g = np.clip(clean_g, 0.0, 255.0)
    clean_b = np.clip(clean_b, 0.0, 255.0)

    # Threshold alpha cleanly: anything with alpha < 0.2 is made 0
    alpha[alpha < 0.2] = 0.0
    # Remap remaining alpha to full range [0, 1]
    alpha = np.clip((alpha - 0.2) / 0.8, 0.0, 1.0)
    
    # Remove small floating noise islands
    from scipy.ndimage import binary_opening, binary_closing
    solid = alpha > 0.1
    # Clean tiny 1-2px noise
    solid = binary_opening(solid, structure=np.ones((2, 2)))
    alpha[~solid] = 0.0

    rgba = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
    rgba[:, :, 0] = clean_r.astype(np.uint8)
    rgba[:, :, 1] = clean_g.astype(np.uint8)
    rgba[:, :, 2] = clean_b.astype(np.uint8)
    rgba[:, :, 3] = (alpha * 255.0).astype(np.uint8)

    sheet_img = Image.fromarray(rgba, 'RGBA')
    sheet_img.save(os.path.join(output_dir, 'sheet-transparent-clean.png'))
    print('Saved ultra-clean transparent sheet!')

    # The 7 sequential poses
    crops = [
        ('01_起势引线', (20, 55, 455, 305)),
        ('02_聚势风套', (455, 55, 875, 305)),
        ('03_蹬射冲刺', (880, 55, 1220, 305)),
        ('04_爆发贯穿', (30, 320, 715, 575)),
        ('05_收束流线', (690, 335, 1240, 575)),
        ('06_抽剑回腕', (540, 580, 860, 835)),
        ('07_散尘归位', (930, 540, 1190, 835))
    ]

    canvas_w, canvas_h = 680, 480
    target_feet_y = 437
    aligned_frames = []

    for name, box in crops:
        cropped = sheet_img.crop(box)
        # Inner clean: trim completely empty borders of the crop
        bbox = cropped.getbbox()
        if bbox:
            cropped_tight = cropped.crop(bbox)
        else:
            cropped_tight = cropped
            
        cropped.save(os.path.join(output_dir, f'{name}.png'))
        
        # Calculate feet placement
        c_arr = np.array(cropped)
        a_chan = c_arr[:, :, 3]
        ys, xs = np.where(a_chan > 50)
        feet_y = np.max(ys) if len(ys) > 0 else cropped.height - 1
        
        if '贯穿' in name or '引线' in name or '流线' in name or '风套' in name:
            body_x = int(np.percentile(xs, 30))
        else:
            body_x = int(np.mean(xs))
            
        canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
        paste_y = target_feet_y - feet_y
        paste_x = 240 - body_x
        canvas.paste(cropped, (paste_x, paste_y), cropped)
        canvas.save(os.path.join(output_dir, f'aligned_{name}.png'))
        aligned_frames.append(canvas)

    # Save Strip
    strip_w = canvas_w * len(aligned_frames)
    strip = Image.new('RGBA', (strip_w, canvas_h), (0, 0, 0, 0))
    for idx, fr in enumerate(aligned_frames):
        strip.paste(fr, (idx * canvas_w, 0), fr)
    strip.save(os.path.join(output_dir, 'pokongci-sequence.png'))

    # Build High Quality Transparent GIF without magenta fringing!
    # In PIL, creating GIF with transparency often leaves magenta halos if palette is naive.
    # Convert frames to RGBA with a solid dark ink background matte OR quantize with explicit transparent color:
    gif_frames = []
    for fr in aligned_frames:
        # Quantize to 255 colors with 1 color reserved for transparency
        fr_arr = np.array(fr)
        # Hard clean alpha for GIF 1-bit transparency:
        # Pixels with alpha < 128 become completely (0,0,0,0)
        # Pixels with alpha >= 128 become fully opaque (a=255)
        clean_gif_fr = fr.copy()
        c_data = np.array(clean_gif_fr)
        trans_mask = c_data[:, :, 3] < 100
        c_data[trans_mask] = [0, 0, 0, 0]
        c_data[~trans_mask, 3] = 255
        p_img = Image.fromarray(c_data, 'RGBA').convert('RGBA')
        
        # Convert to P mode with transparency
        alpha_channel = p_img.split()[3]
        p_img_rgb = p_img.convert('RGB')
        # Quantize
        p_img_p = p_img_rgb.quantize(colors=255, method=Image.MEDIANCUT)
        # Set transparent index to 255
        p_data = np.array(p_img_p)
        p_data[np.array(alpha_channel) == 0] = 255
        
        final_fr = Image.fromarray(p_data, mode='P')
        # Set palette with index 255 as transparent
        palette = p_img_p.getpalette()
        while len(palette) < 256 * 3:
            palette.extend([0, 0, 0])
        final_fr.putpalette(palette)
        final_fr.info['transparency'] = 255
        gif_frames.append(final_fr)

    durations = [120, 100, 80, 150, 120, 100, 180]
    gif_frames[0].save(
        os.path.join(output_dir, 'pokongci-animation.gif'),
        save_all=True,
        append_images=gif_frames[1:],
        duration=durations,
        loop=0,
        transparency=255,
        disposal=2
    )
    print('Generated perfectly keyed frames, strip and halo-free GIF!')

if __name__ == '__main__':
    clean_sprite_sheet(
        '设计/青锋技能帧序列/01_破空刺/generated_sheet/raw-sheet.jpg',
        '设计/青锋技能帧序列/01_破空刺/processed_sprites'
    )
