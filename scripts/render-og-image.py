"""Render the OG image, favicon.ico, and apple-touch-icon.png in one run.

Reads no external state. Idempotent: running again replaces the outputs.
Committed for reproducibility. Uses Pillow (already installed locally).

Usage:
    python scripts/render-og-image.py

Writes:
    assets/og-image.png         (1200x630, OG/Twitter share card)
    favicon.ico                 (32x32, fallback for old browsers)
    apple-touch-icon.png        (180x180, iOS Add-to-Home-Screen)
"""

from pathlib import Path
import os

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

# Portfolio design tokens (keep in sync with styles.css :root).
BG = (246, 245, 239)
FG = (36, 44, 38)
DIM = (96, 102, 91)
ACCENT = (171, 60, 34)

# Text content shown on the share card. Keep claims in sync with the
# hero in index.html — scripts/verify-site.py cross-checks each
# "·"-separated METRICS phrase against the hero metrics block.
EYEBROW = "COMPUTER ENGINEERING / QUEEN'S UNIVERSITY"
METRICS = "Class of 2027 · Dean's Scholar · Software & automation"

ROOT = Path(__file__).resolve().parent.parent
OG_OUT = ROOT / "assets" / "og-image.png"
ICO_OUT = ROOT / "favicon.ico"
APPLE_OUT = ROOT / "apple-touch-icon.png"


# ---------- font discovery ----------
FONT_PATHS = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/Windows/Fonts/JetBrainsMono-Regular.ttf",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/Windows/Fonts/JetBrainsMono-Bold.ttf",
    Path("C:/Windows/Fonts/JetBrainsMono-Regular.ttf"),
    Path("C:/Windows/Fonts/JetBrainsMono-Bold.ttf"),
    Path("C:/Windows/Fonts/CascadiaMono.ttf"),
    Path("C:/Windows/Fonts/CascadiaCode.ttf"),
    Path("C:/Windows/Fonts/consola.ttf"),     # Consolas
    Path("C:/Windows/Fonts/consolab.ttf"),    # Consolas Bold
]


def find_mono(prefer_bold: bool = False) -> Path | None:
    """Return the first available mono font on this machine, preferring bold."""
    bold_names = ("Bold", "consolab", "CascadiaMono")
    if prefer_bold:
        for p in FONT_PATHS:
            if p.exists() and any(b in p.name for b in bold_names):
                return p
    for p in FONT_PATHS:
        if p.exists():
            return p
    return None


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = find_mono(prefer_bold=bold)
    if path is None:
        print("warning: no JetBrains Mono / Cascadia / Consolas found on disk; using PIL default")
        return ImageFont.load_default()
    return ImageFont.truetype(str(path), size=size)


def display_font(size: int, italic: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        ("C:/Windows/Fonts/georgiai.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf")
        if italic else
        ("C:/Windows/Fonts/segoeuib.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return load_font(size, bold=not italic)


# ---------- OG image (1200x630) ----------
def render_og() -> None:
    W, H = 1200, 630
    PAD = 64

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    d.rectangle((PAD, 50, PAD + 46, 96), fill=ACCENT)
    d.text((PAD + 8, 54), "jh.", font=display_font(28), fill=BG)
    d.text((PAD + 63, 59), "Jake Hoffman", font=display_font(24), fill=FG)
    d.line((PAD, 127, W - PAD, 127), fill=(216, 219, 207), width=2)
    d.text((PAD, 160), EYEBROW, font=load_font(18), fill=DIM)
    d.text((PAD - 4, 205), "Jake", font=display_font(112), fill=FG)
    d.text((PAD - 4, 320), "Hoffman.", font=display_font(110, italic=True), fill=ACCENT)

    # The same focus areas as the profile, never a live-status claim.
    green = (37, 55, 45)
    d.rectangle((800, 170, 1136, 464), fill=green)
    for x in range(814, 1130, 16):
        for y in range(180, 456, 16):
            d.point((x, y), fill=(72, 96, 74))
    d.text((822, 193), "SOFTWARE WITH A PURPOSE", font=load_font(15), fill=(243, 242, 220))
    for index, label in enumerate(("Software", "Automation", "Data tools")):
        y = 235 + index * 65
        fill = (218, 228, 194) if index == 1 else green
        ink = green if index == 1 else (243, 242, 220)
        d.rectangle((822, y, 1114, y + 48), fill=fill, outline=(98, 120, 95))
        d.text((836, y + 12), label, font=load_font(18), fill=ink)

    d.line((PAD, 502, W - PAD, 502), fill=(216, 219, 207), width=2)
    d.text((PAD, 526), METRICS, font=load_font(18), fill=DIM)
    d.text((PAD, 570), "jakethehoffer.github.io/website", font=load_font(16), fill=ACCENT)

    OG_OUT.parent.mkdir(parents=True, exist_ok=True)
    # Provenance chunk: verify-site.py compares this against the METRICS
    # constant above, so a script edit committed without a re-render
    # fails CI instead of shipping a stale share card.
    meta = PngImagePlugin.PngInfo()
    meta.add_text("jh:metrics", METRICS)
    img.save(OG_OUT, "PNG", optimize=True, pnginfo=meta)
    print(f"wrote {OG_OUT}  ({OG_OUT.stat().st_size:,} bytes)")


# ---------- shared icon glyph ----------
def render_jh_glyph(size: int, *, padding_ratio: float = 0.12, with_rim: bool = True) -> Image.Image:
    """Render the same terracotta monogram used in the page header."""
    img = Image.new("RGB", (size, size), ACCENT)
    d = ImageDraw.Draw(img)

    # Glyph
    glyph_size = int(size * (1 - padding_ratio * 2) * 0.7)
    font = display_font(glyph_size)
    text = "jh."
    bbox = d.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2 - bbox[0]
    y = (size - text_h) // 2 - bbox[1]
    d.text((x, y), text, font=font, fill=BG)

    return img


def render_favicon_ico() -> None:
    # Render at 32x32 (the actual final size). We also bake a 16x16 frame
    # so old clients picking the smaller size still look acceptable.
    icon_32 = render_jh_glyph(32, padding_ratio=0.06)
    icon_16 = render_jh_glyph(16, padding_ratio=0.0, with_rim=False)
    icon_32.save(ICO_OUT, format="ICO", sizes=[(16, 16), (32, 32)], append_images=[icon_16])
    print(f"wrote {ICO_OUT}  ({ICO_OUT.stat().st_size:,} bytes)")


def render_apple_touch() -> None:
    img = render_jh_glyph(180, padding_ratio=0.12, with_rim=False)
    img.save(APPLE_OUT, "PNG", optimize=True)
    print(f"wrote {APPLE_OUT}  ({APPLE_OUT.stat().st_size:,} bytes)")


def main() -> None:
    render_og()
    render_favicon_ico()
    render_apple_touch()


if __name__ == "__main__":
    main()
