"""一次性工具：把生成图的玫瑰红背景替换成纯品红 #FF00FF，供 generate2dsprite 管线识别。
只替换与四角背景色距离 < 95 的像素，主体颜色不受影响。"""
import sys
import numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
img = Image.open(src).convert("RGB")
a = np.asarray(img).astype(np.int16)
h, w, _ = a.shape

# 取四角 20x20 的均值作为背景色
corners = np.concatenate([
    a[:20, :20].reshape(-1, 3), a[:20, -20:].reshape(-1, 3),
    a[-20:, :20].reshape(-1, 3), a[-20:, -20:].reshape(-1, 3),
])
bg = corners.mean(axis=0)
print("detected bg:", bg)

dist = np.sqrt(((a - bg) ** 2).sum(axis=2))
mask = dist < 95
print("bg pixels:", mask.mean().round(3))

out = a.copy()
out[mask] = [255, 0, 255]
Image.fromarray(out.astype(np.uint8)).save(dst)
print("saved:", dst)
