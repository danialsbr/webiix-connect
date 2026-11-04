#!/usr/bin/env python3
"""Generate Webiix Connect icon/logo assets from branding masters."""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "branding"
RES = ROOT / "res"
FLUTTER_ASSETS = ROOT / "flutter" / "assets"
ANDROID_RES = ROOT / "flutter" / "android" / "app" / "src" / "main" / "res"

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
    'viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M12 12c-2-2.67-4-4-6-4a4 4 0 1 0 0 8c2 0 4-1.33 6-4Zm0 0'
    'c2 2.67 4 4 6 4a4 4 0 0 0 0-8c-2 0-4 1.33-6 4Z"/></svg>'
)


def main() -> None:
    master = Image.open(BRAND / "icon_ai.png").convert("RGBA")

    def resize(size: int) -> Image.Image:
        return master.resize((size, size), Image.Resampling.LANCZOS)

    for size in (16, 32, 64, 128, 256, 512, 1024):
        resize(size).save(BRAND / f"icon_{size}.png")

    resize(32).save(RES / "32x32.png")
    resize(64).save(RES / "64x64.png")
    resize(128).save(RES / "128x128.png")
    resize(256).save(RES / "128x128@2x.png")
    resize(256).save(RES / "icon.png")
    resize(512).save(RES / "mac-icon.png")

    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    ico_images = [resize(s) for s in ico_sizes]
    ico_images[0].save(
        RES / "icon.ico",
        format="ICO",
        sizes=[(s, s) for s in ico_sizes],
    )
    ico_images[0].save(
        RES / "tray-icon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (64, 64)],
    )

    resize(256).save(FLUTTER_ASSETS / "icon.png")

    logo = Image.open(BRAND / "logo.png").convert("RGBA")
    lw, lh = logo.size
    scale = min(300 / lw, 60 / lh, 1.0)
    nl = logo.resize(
        (max(1, int(lw * scale)), max(1, int(lh * scale))),
        Image.Resampling.LANCZOS,
    )
    for name in ("logo.png", "logo_light.png", "logo_dark.png"):
        nl.save(FLUTTER_ASSETS / name)

    portable_label = ROOT / "libs" / "portable" / "src" / "res" / "label.png"
    portable_label.parent.mkdir(parents=True, exist_ok=True)
    nl.save(portable_label)

    (FLUTTER_ASSETS / "icon.svg").write_text(SVG, encoding="utf-8")
    (RES / "logo.svg").write_text(SVG, encoding="utf-8")
    (RES / "scalable.svg").write_text(SVG, encoding="utf-8")

    android_sizes = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }
    for folder, size in android_sizes.items():
        d = ANDROID_RES / folder
        d.mkdir(parents=True, exist_ok=True)
        im = resize(size)
        im.save(d / "ic_launcher.png")
        im.save(d / "ic_launcher_round.png")
        im.save(d / "ic_launcher_foreground.png")
        resize(max(24, size // 2)).save(d / "ic_stat_logo.png")

    print("Webiix Connect assets generated")


if __name__ == "__main__":
    main()
