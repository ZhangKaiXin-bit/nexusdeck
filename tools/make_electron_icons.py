"""从 console-app-icon.png 生成 Electron 用的 icon.icns 与 icon.ico。
- icns: 生成标准 macOS iconset 多尺寸后用 iconutil 合成
- ico: 用 Pillow 写多尺寸 ico（含 256/128/64/48/32/16）
"""
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path("/Users/zhangwentao/WorkBuddy/2026-08-23-18-03-16/nexusdeck")
# 优先用方案 E 的 1024 主图（最高清），回退到仓库 512 图
SRC_1024 = Path.home() / "Desktop/NexusDeck-icons/source-1024.png"
SRC = SRC_1024 if SRC_1024.exists() else ROOT / "static/assets/console-app-icon.png"
ASSETS = ROOT / "electron/assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# macOS iconset 所需尺寸（名称: 边长）
ICONSET_SIZES = {
    "icon_16x16.png": 16,
    "icon_16x16@2x.png": 32,
    "icon_32x32.png": 32,
    "icon_32x32@2x.png": 64,
    "icon_128x128.png": 128,
    "icon_128x128@2x.png": 256,
    "icon_256x256.png": 256,
    "icon_256x256@2x.png": 512,
    "icon_512x512.png": 512,
    "icon_512x512@2x.png": 1024,
}

ICO_SIZES = [256, 128, 64, 48, 32, 16]


def make_iconset(src: Image.Image, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, size in ICONSET_SIZES.items():
        img = src.resize((size, size), Image.LANCZOS)
        img.save(out_dir / name)
    return out_dir


def main():
    src = Image.open(SRC).convert("RGBA")
    # 统一正方形
    if src.width != src.height:
        s = min(src.width, src.height)
        left = (src.width - s) // 2
        src = src.crop((left, (src.height - s) // 2, left + s, (src.height - s) // 2 + s))

    # --- icns ---
    iconset = ASSETS / "nexusdeck.iconset"
    make_iconset(src, iconset)
    icns = ASSETS / "icon.icns"
    subprocess.run(
        ["iconutil", "--convert", "icns", "--output", str(icns), str(iconset)],
        check=True,
    )
    print("icns ->", icns, icns.stat().st_size, "bytes")

    # --- ico ---
    ico = ASSETS / "icon.ico"
    frames = []
    for size in ICO_SIZES:
        img = src.resize((size, size), Image.LANCZOS)
        frames.append(img)
    frames[0].save(ico, sizes=[(f.width, f.height) for f in frames], format="ICO")
    print("ico  ->", ico, ico.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
