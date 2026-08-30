import os
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from app.utils.assets import LOGO_PNG
from app.utils.format import format_btcz, format_fiat

BG = (13, 15, 14)
CARD = (26, 31, 28)
ACCENT = (61, 220, 151)
GOLD = (255, 209, 102)
TEXT = (232, 232, 232)
MUTED = (154, 160, 166)
LINE = (43, 51, 46)

BOLD_FONTS = [
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
REGULAR_FONTS = [
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
EMOJI_FONTS = [
    "C:/Windows/Fonts/seguiemj.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
]


def _font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _emoji_font_path():
    for path in EMOJI_FONTS:
        if os.path.exists(path):
            return path
    return None


def _render_emoji(char, target):
    path = _emoji_font_path()
    if not path:
        return None
    native = 109 if path.endswith("NotoColorEmoji.ttf") else target
    try:
        font = ImageFont.truetype(path, native)
    except Exception:
        return None
    layer = Image.new("RGBA", (native * 2, native * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    try:
        draw.text((native // 2, native // 2), char, font=font, embedded_color=True)
    except Exception:
        return None
    bbox = layer.getbbox()
    if not bbox:
        return None
    glyph = layer.crop(bbox)
    ratio = target / max(glyph.size)
    new_size = (max(1, int(glyph.width * ratio)), max(1, int(glyph.height * ratio)))
    return glyph.resize(new_size, Image.Resampling.LANCZOS)


def _text_w(draw, text, font):
    return draw.textlength(text, font=font)


def _fit(draw, text, candidates, max_size, max_w, min_size=30):
    size = max_size
    while size > min_size:
        font = _font(candidates, size)
        if draw.textlength(text, font=font) <= max_w:
            return font
        size -= 3
    return _font(candidates, min_size)


def _rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def _logo(size):
    if LOGO_PNG.exists():
        try:
            return Image.open(LOGO_PNG).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
        except Exception:
            return None
    return None


def _glow(img, center, radius, color, alpha=70):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    cx, cy = center
    steps = 24
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(alpha * (1 - i / steps))
        gdraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (a,))
    img.alpha_composite(glow)


def _stat_labels():
    return {
        "stack": "STACK",
        "value": "VALUE",
        "supply": "SUPPLY SHARE",
        "ratio": "RATIO",
        "rank": "RANK",
        "made": "made with BTCZ Tools",
        "brand": "BitcoinZ Holder",
    }


def _draw_square(data, hide_amounts):
    W = H = 1080
    img = Image.new("RGBA", (W, H), BG)
    draw = ImageDraw.Draw(img)
    lab = _stat_labels()

    f_brand = _font(BOLD_FONTS, 40)
    f_tier = _font(BOLD_FONTS, 86)
    f_label = _font(BOLD_FONTS, 30)
    f_value = _font(BOLD_FONTS, 64)
    f_small = _font(REGULAR_FONTS, 30)
    f_foot = _font(REGULAR_FONTS, 26)

    _rounded(draw, [36, 36, W - 36, H - 36], 40, CARD)
    draw.rounded_rectangle([36, 36, W - 36, H - 36], radius=40, outline=LINE, width=3)

    logo = _logo(84)
    top_y = 92
    if logo is not None:
        img.alpha_composite(logo, (80, top_y - 18))
        brand_x = 184
    else:
        brand_x = 80
    draw.text((brand_x, top_y), "BTCZ TOOLS", font=f_brand, fill=ACCENT)
    pill = lab["brand"]
    pw = _text_w(draw, pill, f_small) + 44
    _rounded(draw, [W - 80 - pw, top_y - 4, W - 80, top_y + 48], 24, BG)
    draw.text((W - 80 - pw + 22, top_y + 6), pill, font=f_small, fill=MUTED)

    _glow(img, (W // 2, 380), 300, ACCENT, alpha=60)
    glyph = _render_emoji(data["emoji"], 275)
    if glyph is not None:
        img.alpha_composite(glyph, ((W - glyph.width) // 2, 380 - glyph.height // 2))

    tier = data["tier"].upper()
    f_tier = _fit(draw, tier, BOLD_FONTS, 86, W - 240)
    tw = _text_w(draw, tier, f_tier)
    draw.text(((W - tw) // 2, 540), tier, font=f_tier, fill=ACCENT)

    draw.line([120, 660, W - 120, 660], fill=LINE, width=3)

    col_w = (W - 240 - 40) // 2
    y = 700
    if not hide_amounts:
        stxt = f"{format_btcz(data['stack'], 0)} BTCZ"
        f_stack = _fit(draw, stxt, BOLD_FONTS, 64, W - 240)
        draw.text((120, y), lab["stack"], font=f_label, fill=MUTED)
        draw.text((120, y + 40), stxt, font=f_stack, fill=TEXT)
        y += 140
        vtxt = format_fiat(data["value"], data.get("sym", "\u20ac"), 0)
        f_v = _fit(draw, vtxt, BOLD_FONTS, 56, col_w)
        draw.text((120, y), lab["value"], font=f_label, fill=MUTED)
        draw.text((120, y + 38), vtxt, font=f_v, fill=GOLD)
        sx = 120 + col_w + 40
        stext = f"{data['supply_pct']:.4f} %"
        f_s = _fit(draw, stext, BOLD_FONTS, 56, col_w)
        draw.text((sx, y), lab["supply"], font=f_label, fill=MUTED)
        draw.text((sx, y + 38), stext, font=f_s, fill=ACCENT)
    else:
        stext = f"{data['supply_pct']:.4f} %"
        f_s = _fit(draw, stext, BOLD_FONTS, 64, W - 240)
        draw.text((120, y), lab["supply"], font=f_label, fill=MUTED)
        draw.text((120, y + 40), stext, font=f_s, fill=ACCENT)
        y += 140
        one = data["one_in"]
        if one > 0:
            draw.text((120, y), lab["ratio"], font=f_label, fill=MUTED)
            draw.text((120, y + 38), f"~1 / {one:,}", font=f_value, fill=TEXT)

    foot = f"{lab['made']}  \u2022  {datetime.now().strftime('%Y-%m-%d')}"
    draw.text((120, H - 96), foot, font=f_foot, fill=MUTED)
    return img.convert("RGB")


def _draw_wide(data, hide_amounts):
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), BG)
    draw = ImageDraw.Draw(img)
    lab = _stat_labels()

    f_brand = _font(BOLD_FONTS, 34)
    f_tier = _font(BOLD_FONTS, 68)
    f_label = _font(BOLD_FONTS, 26)
    f_value = _font(BOLD_FONTS, 52)
    f_small = _font(REGULAR_FONTS, 26)
    f_foot = _font(REGULAR_FONTS, 24)

    _rounded(draw, [28, 28, W - 28, H - 28], 34, CARD)
    draw.rounded_rectangle([28, 28, W - 28, H - 28], radius=34, outline=LINE, width=3)

    _glow(img, (300, H // 2 + 20), 260, ACCENT, alpha=55)
    glyph = _render_emoji(data["emoji"], 240)
    if glyph is not None:
        img.alpha_composite(glyph, (300 - glyph.width // 2, (H - glyph.height) // 2 + 10))

    logo = _logo(64)
    if logo is not None:
        img.alpha_composite(logo, (72, 64))
        bx = 152
    else:
        bx = 72
    draw.text((bx, 78), "BTCZ TOOLS", font=f_brand, fill=ACCENT)

    left = 560
    right_edge = W - 80
    full_w = right_edge - left
    col_w = (full_w - 40) // 2
    col2 = left + col_w + 40

    tier = data["tier"].upper()
    f_tier = _fit(draw, tier, BOLD_FONTS, 68, full_w)
    draw.text((left, 150), tier, font=f_tier, fill=ACCENT)
    draw.line([left, 244, right_edge, 244], fill=LINE, width=3)

    y = 286
    if not hide_amounts:
        stxt = f"{format_btcz(data['stack'], 0)} BTCZ"
        f_stack = _fit(draw, stxt, BOLD_FONTS, 52, full_w)
        draw.text((left, y), lab["stack"], font=f_label, fill=MUTED)
        draw.text((left, y + 34), stxt, font=f_stack, fill=TEXT)
        y += 118
        vtxt = format_fiat(data["value"], data.get("sym", "\u20ac"), 0)
        f_v = _fit(draw, vtxt, BOLD_FONTS, 48, col_w)
        draw.text((left, y), lab["value"], font=f_label, fill=MUTED)
        draw.text((left, y + 34), vtxt, font=f_v, fill=GOLD)
        stext = f"{data['supply_pct']:.4f} %"
        f_s = _fit(draw, stext, BOLD_FONTS, 48, col_w)
        draw.text((col2, y), lab["supply"], font=f_label, fill=MUTED)
        draw.text((col2, y + 34), stext, font=f_s, fill=ACCENT)
    else:
        stext = f"{data['supply_pct']:.4f} %"
        f_s = _fit(draw, stext, BOLD_FONTS, 52, full_w)
        draw.text((left, y), lab["supply"], font=f_label, fill=MUTED)
        draw.text((left, y + 34), stext, font=f_s, fill=ACCENT)
        y += 118
        if data["one_in"] > 0:
            draw.text((left, y), lab["ratio"], font=f_label, fill=MUTED)
            draw.text((left, y + 34), f"~1 / {data['one_in']:,}", font=f_value, fill=TEXT)

    foot = f"{lab['made']}  \u2022  {datetime.now().strftime('%Y-%m-%d')}"
    draw.text((72, H - 78), foot, font=f_foot, fill=MUTED)
    return img.convert("RGB")


def generate_cards(data, out_dir, hide_amounts=False):
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    square = _draw_square(data, hide_amounts)
    p1 = os.path.join(out_dir, "btcz_holder_card_1080.png")
    square.save(p1, "PNG")
    paths.append(p1)
    wide = _draw_wide(data, hide_amounts)
    p2 = os.path.join(out_dir, "btcz_holder_card_1200x630.png")
    wide.save(p2, "PNG")
    paths.append(p2)
    return paths
