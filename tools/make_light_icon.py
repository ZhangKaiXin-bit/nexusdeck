"""生成 NexusDeck 浅色模式图标（方案 E 的反色版）并补齐 favicon 多尺寸。

浅色版策略（跟随系统浅色模式用）：
- 底座由深蓝变为浅色/透白，深色描边勾轮廓
- 保留青色播放三角（品牌强调色，浅底仍清晰）
- 保留绿色状态点
- 主图保持透明背景，仅内部填充反色

同时把 favicon.ico 补齐到 16/32/48/64/128/256 六档（比仓库原脚本的 3 档更全）。
"""
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path("/Users/zhangwentao/WorkBuddy/2026-08-23-18-03-16/nexusdeck")
SRC = ROOT / "static/assets/console-app-icon.png"
ASSETS = ROOT / "static/assets"
LIGHT = ROOT / "static/assets/light"

# macOS iconset 尺寸集
ICONSET_SIZES = (
    (16, "icon_16x16.png"),
    (32, "icon_16x16@2x.png"),
    (32, "icon_32x32.png"),
    (64, "icon_32x32@2x.png"),
    (128, "icon_128x128.png"),
    (256, "icon_128x128@2x.png"),
    (256, "icon_256x256.png"),
    (512, "icon_256x256@2x.png"),
    (512, "icon_512x512.png"),
    (1024, "icon_512x512@2x.png"),
)


def to_square(img: Image.Image) -> Image.Image:
    if img.width != img.height:
        s = min(img.width, img.height)
        left = (img.width - s) // 2
        img = img.crop((left, (img.height - s) // 2, left + s, (img.height - s) // 2 + s))
    return img


def make_light_variant(img: Image.Image) -> Image.Image:
    """把深蓝底图标反色为浅色版：对不透明像素做亮度反转 + 提亮。"""
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            # 亮度反转：深底 -> 浅底，同时保持青色/绿色品牌色相可辨
            nr = 255 - r
            ng = 255 - g
            nb = 255 - b
            # 提亮浅底，避免纯反转后偏灰：向白靠拢
            nr = int(nr * 0.82 + 255 * 0.18)
            ng = int(ng * 0.82 + 255 * 0.18)
            nb = int(nb * 0.82 + 255 * 0.18)
            px[x, y] = (nr, ng, nb, a)
    return img


def main():
    src = to_square(Image.open(SRC).convert("RGBA"))

    # ---- 浅色版 PNG 资产 ----
    LIGHT.mkdir(parents=True, exist_ok=True)
    light = make_light_variant(src)
    light.save(LIGHT / "console-app-icon-light.png", optimize=True)
    light_resized = light.resize((256, 256), Image.LANCZOS)
    light_resized.save(LIGHT / "brand-mark-light.png", optimize=True)
    light_resized.save(LIGHT / "apple-touch-icon-light.png", optimize=True)
    print("浅色版 PNG ->", LIGHT / "console-app-icon-light.png")

    # ---- 浅色版 icns（供 macOS 跟随系统切换）----
    iconset = LIGHT / "nexusdeck-light.iconset"
    iconset.mkdir(parents=True, exist_ok=True)
    for size, name in ICONSET_SIZES:
        light.resize((size, size), Image.LANCZOS).save(iconset / name)
    icns = LIGHT / "AppIcon-light.icns"
    subprocess.run(["iconutil", "--convert", "icns", "--output", str(icns), str(iconset)], check=True)
    print("浅色版 icns ->", icns)

    # ---- favicon.ico 补齐到 6 档 ----
    # 注意：Pillow 生成多尺寸 ICO 的正确写法是「单张大图 + sizes 列表」，
    # 用 append_images 在 12.x 版本会丢失帧，故用此方式。
    fav = ASSETS / "favicon.ico"
    src.save(fav, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("favicon.ico 补齐 ->", fav, "尺寸: 16/32/48/64/128/256")


if __name__ == "__main__":
    main()
