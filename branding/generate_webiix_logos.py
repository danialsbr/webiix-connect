#!/usr/bin/env python3
"""Build icons from Lucide infinity SVG raster + stacked Webiix/connect wordmarks.

Primary mark: branding/icon_transparent.png (rendered from the Lucide path).
Falls back to cropping the user reference if that file is missing.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "branding"
ASSETS = ROOT / "flutter" / "assets"
RES = ROOT / "res"
REF = Path(
    r"C:\Users\dani\.cursor\projects\d-Webiix-Connect\assets\image-a8cd6601-2530-454a-9fed-f9ba6c3866b8.png"
)
SVG_ICON = BRAND / "icon_transparent.png"

BLUE = (8, 107, 232, 255)  # redesign brand blue #086BE8
WHITE = (255, 255, 255, 255)


def font(size: int, bold: bool = False):
    paths = (
        [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
        if bold
        else [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]
    )
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()


def extract_infinity() -> Image.Image:
    if SVG_ICON.exists():
        return Image.open(SVG_ICON).convert("RGBA")

    img = Image.open(REF).convert("RGBA")
    w, h = img.size
    left = img.crop((0, 0, int(w * 0.42), h))
    px = left.load()
    for y in range(left.height):
        for x in range(left.width):
            r, g, b, a = px[x, y]
            if b > r + 20 and b > g + 10 and (r + g + b) < 650 and b > 120:
                continue
            px[x, y] = (255, 255, 255, 0)
    bbox = left.getbbox()
    if bbox:
        left = left.crop(bbox)
    side = max(left.size)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(left, ((side - left.width) // 2, (side - left.height) // 2), left)
    return sq


def on_white(im: Image.Image, size: int) -> Image.Image:
    pad = int(size * 0.12)
    content = im.resize((size - pad * 2, size - pad * 2), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (size, size), WHITE)
    out.paste(content, (pad, pad), content)
    return out


def wordmark(icon: Image.Image, dark: bool) -> Image.Image:
    ih = 56
    ic = icon.resize((ih, ih), Image.Resampling.LANCZOS)
    title_f = font(28, bold=True)
    sub_f = font(20, bold=False)
    title_c = WHITE if dark else BLUE
    sub_c = (147, 197, 253, 255) if dark else BLUE

    tmp = Image.new("RGBA", (1, 1))
    d = ImageDraw.Draw(tmp)
    tb = d.textbbox((0, 0), "Webiix", font=title_f)
    sb = d.textbbox((0, 0), "connect", font=sub_f)
    tw = max(tb[2] - tb[0], sb[2] - sb[0])
    th = (tb[3] - tb[1]) + 4 + (sb[3] - sb[1])

    gap, pad = 12, 6
    W = pad + ih + gap + tw + pad
    H = max(ih, th) + pad * 2
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.paste(ic, (pad, (H - ih) // 2), ic)
    draw = ImageDraw.Draw(canvas)
    tx = pad + ih + gap
    ty = (H - th) // 2
    draw.text((tx, ty), "Webiix", font=title_f, fill=title_c)
    draw.text((tx, ty + (tb[3] - tb[1]) + 4), "connect", font=sub_f, fill=sub_c)

    scale = min(300 / canvas.width, 60 / canvas.height, 1.0)
    return canvas.resize(
        (max(1, int(canvas.width * scale)), max(1, int(canvas.height * scale))),
        Image.Resampling.LANCZOS,
    )


def main() -> None:
    BRAND.mkdir(exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    infinity = extract_infinity()
    infinity.save(BRAND / "icon_transparent.png")

    master = on_white(infinity, 1024)
    master.save(BRAND / "icon_ai.png")

    for size, name in (
        (256, "icon.png"),
        (32, "32x32.png"),
        (64, "64x64.png"),
        (128, "128x128.png"),
        (256, "128x128@2x.png"),
        (512, "mac-icon.png"),
    ):
        on_white(infinity, size).save(RES / name)

    infinity.resize((256, 256), Image.Resampling.LANCZOS).save(ASSETS / "icon.png")

    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    icos = [on_white(infinity, s) for s in ico_sizes]
    icos[0].save(RES / "icon.ico", format="ICO", sizes=[(s, s) for s in ico_sizes])
    icos[0].save(RES / "tray-icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (64, 64)])

    light = wordmark(infinity, dark=False)
    dark = wordmark(infinity, dark=True)
    light.save(ASSETS / "logo_light.png")
    light.save(ASSETS / "logo.png")
    dark.save(ASSETS / "logo_dark.png")
    light.save(BRAND / "logo.png")
    dark.save(BRAND / "logo_dark.png")

    print("OK: Lucide infinity SVG + stacked Webiix/connect")


if __name__ == "__main__":
    main()
