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

# v2 design tokens (keep in sync with styles.css :root)
BG = (10, 14, 20)            # #0a0e14
FG = (214, 222, 230)         # #d6dee6
DIM = (118, 130, 143)        # #76828f (--text-mute, AA-adjusted)
ACCENT = (245, 179, 66)      # #f5b342

# Text content shown on the share card. Keep claims in sync with the
# hero in index.html — scripts/verify-site.py cross-checks each
# "·"-separated METRICS phrase against the hero metrics block.
EYEBROW = "computer engineering @ queen's · class of 2027"
BODY_LINES = [
    "> i build software that runs unattended.",
    "> trading agents, arbitrage daemons,",
    "> and ML pipelines.",
]
METRICS = "//  3 unattended systems  ·  10 bookmakers  ·  dean's scholar"

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


# ---------- OG image (1200x630) ----------
def render_og() -> None:
    W, H = 1200, 630
    PAD = 80

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    name_font = load_font(76, bold=True)
    eyebrow_font = load_font(26, bold=False)
    prompt_font = load_font(28, bold=True)
    body_font = load_font(28, bold=False)
    metrics_font = load_font(22, bold=False)
    url_font = load_font(20, bold=False)

    # Name
    d.text((PAD, PAD), "JAKE HOFFMAN", font=name_font, fill=FG)

    # Status dot in the right margin, aligned to the name's baseline
    dot_r = 9
    dot_cx = W - PAD - 14
    dot_cy = PAD + 76 // 2 + 4
    d.ellipse((dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r), fill=ACCENT)
    d.text((dot_cx - dot_r - 110, dot_cy - 13), "ACTIVE", font=eyebrow_font, fill=DIM)

    # Eyebrow
    d.text((PAD, PAD + 92), EYEBROW, font=eyebrow_font, fill=DIM)

    # Terminal-flavored body
    y = PAD + 92 + 50
    d.text((PAD, y), "$ whoami", font=prompt_font, fill=ACCENT)
    y += 50
    for line in BODY_LINES:
        d.text((PAD, y), line, font=body_font, fill=FG)
        y += 42

    # Metrics
    y += 28
    d.text((PAD, y), METRICS, font=metrics_font, fill=DIM)

    # Footer URL (bottom-right)
    url = "jakethehoffer.github.io/website"
    bbox = d.textbbox((0, 0), url, font=url_font)
    url_w = bbox[2] - bbox[0]
    d.text((W - PAD - url_w, H - PAD - 20), url, font=url_font, fill=DIM)

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
    """Render the JH glyph centered in a near-black rounded square."""
    img = Image.new("RGB", (size, size), BG)
    d = ImageDraw.Draw(img)

    if with_rim:
        rim_width = max(1, size // 32)
        rim_color = (int(ACCENT[0] * 0.45), int(ACCENT[1] * 0.45), int(ACCENT[2] * 0.45))
        d.rectangle((rim_width, rim_width, size - rim_width, size - rim_width), outline=rim_color, width=rim_width)

    # Glyph
    glyph_size = int(size * (1 - padding_ratio * 2) * 0.7)
    font = load_font(glyph_size, bold=True)
    text = "JH"
    bbox = d.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2 - bbox[0]
    y = (size - text_h) // 2 - bbox[1]
    d.text((x, y), text, font=font, fill=ACCENT)

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
