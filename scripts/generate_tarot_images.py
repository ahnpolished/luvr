"""Generate Major Arcana tarot card images for Telegram.

Creates stylized card images with the Major Arcana names, numbers,
and simple symbolic colors. Also generates a card-back image.

Output: assets/tarot/{major_arcana,card_back}.png
Size: ~800×1400px, ≤5MB each — optimized for Telegram photo display.
License: Generated in-house, no external copyright.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path("assets/tarot")
CARD_WIDTH = 800
CARD_HEIGHT = 1400
BORDER_RADIUS = 40
FONT_SIZE_TITLE = 48
FONT_SIZE_NUMBER = 36
FONT_SIZE_MEANING = 28

# Card color palette per arcana group (based on traditional associations)
ARCANA_COLORS: dict[str, tuple[int, int, int]] = {
    "fool": (240, 248, 255),  # alice blue — innocence
    "magician": (255, 215, 0),  # gold — mastery
    "high_priestess": (216, 191, 216),  # thistle — mystery
    "empress": (152, 251, 152),  # pale green — nature
    "emperor": (220, 20, 60),  # crimson — authority
    "hierophant": (139, 69, 19),  # saddle brown — tradition
    "lovers": (255, 182, 193),  # light pink — love
    "chariot": (192, 192, 192),  # silver — momentum
    "strength": (255, 140, 0),  # dark orange — courage
    "hermit": (70, 130, 180),  # steel blue — solitude
    "wheel_of_fortune": (218, 165, 32),  # goldenrod — cycles
    "justice": (75, 0, 130),  # indigo — fairness
    "hanged_man": (119, 136, 153),  # slate gray — surrender
    "death": (47, 79, 79),  # dark slate gray — transformation
    "temperance": (255, 160, 122),  # light salmon — balance
    "devil": (178, 34, 34),  # firebrick — bondage
    "tower": (128, 128, 128),  # gray — upheaval
    "star": (255, 255, 224),  # light yellow — hope
    "moon": (25, 25, 112),  # midnight blue — illusion
    "sun": (255, 255, 0),  # yellow — joy
    "judgement": (238, 130, 238),  # violet — reckoning
    "world": (0, 128, 128),  # teal — completion
}

MAJOR_ARCANA: list[dict] = [
    {"number": 0, "slug": "fool", "name": "The Fool", "meaning": "New beginnings, spontaneity, a leap of faith"},
    {"number": 1, "slug": "magician", "name": "The Magician", "meaning": "Willpower, resourcefulness, manifestation"},
    {
        "number": 2,
        "slug": "high_priestess",
        "name": "The High Priestess",
        "meaning": "Intuition, the subconscious, mystery",
    },
    {"number": 3, "slug": "empress", "name": "The Empress", "meaning": "Abundance, nurturing, connection to nature"},
    {"number": 4, "slug": "emperor", "name": "The Emperor", "meaning": "Authority, structure, a commanding presence"},
    {
        "number": 5,
        "slug": "hierophant",
        "name": "The Hierophant",
        "meaning": "Tradition, spiritual wisdom, institutions",
    },
    {"number": 6, "slug": "lovers", "name": "The Lovers", "meaning": "Love, harmony, alignment of values"},
    {
        "number": 7,
        "slug": "chariot",
        "name": "The Chariot",
        "meaning": "Determination, willpower, overcoming obstacles",
    },
    {"number": 8, "slug": "strength", "name": "Strength", "meaning": "Courage, inner power, gentle control"},
    {"number": 9, "slug": "hermit", "name": "The Hermit", "meaning": "Soul-searching, introspection, solitude"},
    {
        "number": 10,
        "slug": "wheel_of_fortune",
        "name": "Wheel of Fortune",
        "meaning": "Cycles, destiny, turning points",
    },
    {"number": 11, "slug": "justice", "name": "Justice", "meaning": "Fairness, truth, cause and effect"},
    {"number": 12, "slug": "hanged_man", "name": "The Hanged Man", "meaning": "Pause, surrender, new perspective"},
    {"number": 13, "slug": "death", "name": "Death", "meaning": "Endings, transformation, letting go"},
    {"number": 14, "slug": "temperance", "name": "Temperance", "meaning": "Balance, moderation, patience"},
    {"number": 15, "slug": "devil", "name": "The Devil", "meaning": "Attachment, shadow self, unhealthy bonds"},
    {"number": 16, "slug": "tower", "name": "The Tower", "meaning": "Sudden change, revelation, awakening"},
    {"number": 17, "slug": "star", "name": "The Star", "meaning": "Hope, inspiration, renewed faith"},
    {"number": 18, "slug": "moon", "name": "The Moon", "meaning": "Illusion, fear, the unconscious"},
    {"number": 19, "slug": "sun", "name": "The Sun", "meaning": "Joy, vitality, success"},
    {"number": 20, "slug": "judgement", "name": "Judgement", "meaning": "Rebirth, inner calling, absolution"},
    {"number": 21, "slug": "world", "name": "The World", "meaning": "Completion, fulfillment, wholeness"},
]

CARD_BACK_COLOR = (30, 74, 58)  # forest green — Luvr brand
CARD_BACK_ACCENT = (94, 196, 160)  # mint — Luvr brand

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _try_load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a reasonable system font, falling back to default."""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        "C:\\Windows\\Fonts\\arial.ttf",  # Windows
    ]
    for path in font_paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _rounded_rectangle(
    draw: ImageDraw.Draw,
    xy: tuple[int, int, int, int],
    radius: int,
    fill: tuple[int, int, int],
) -> None:
    """Draw a filled rounded rectangle."""
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def _draw_text_centered(
    draw: ImageDraw.Draw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int] = (255, 255, 255),
    width: int = CARD_WIDTH,
) -> None:
    """Draw text horizontally centered at y."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    draw.text((x, y), text, fill=fill, font=font)


def _draw_card(
    color: tuple[int, int, int],
    number: int | None,
    name: str,
    meaning: str,
    filename: str,
) -> None:
    """Create a single tarot card image."""
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), color=(20, 20, 30))
    draw = ImageDraw.Draw(img)

    # Card border
    border_margin = 24
    border_color = (255, 255, 255, 60)
    draw.rounded_rectangle(
        (border_margin, border_margin, CARD_WIDTH - border_margin, CARD_HEIGHT - border_margin),
        radius=BORDER_RADIUS,
        outline=border_color,
        width=3,
    )

    # Inner fill
    inner_margin = 48
    _rounded_rectangle(
        draw,
        (inner_margin, inner_margin, CARD_WIDTH - inner_margin, CARD_HEIGHT - inner_margin),
        radius=BORDER_RADIUS,
        fill=color,
    )

    title_font = _try_load_font(FONT_SIZE_TITLE)
    number_font = _try_load_font(FONT_SIZE_NUMBER)
    meaning_font = _try_load_font(FONT_SIZE_MEANING)

    text_color = (20, 20, 30)  # dark text on light/colored background

    # Number (top)
    if number is not None:
        num_str = str(number) if number > 0 else "0"
        _draw_text_centered(draw, num_str, 80, number_font, fill=text_color)

    # Title
    _draw_text_centered(draw, name.upper(), CARD_HEIGHT // 3, title_font, fill=text_color)

    # Divider line
    divider_y = CARD_HEIGHT // 3 + 80
    draw.line(
        [(CARD_WIDTH // 4, divider_y), (3 * CARD_WIDTH // 4, divider_y)],
        fill=text_color,
        width=2,
    )

    # Meaning (wrapped)
    wrapped = textwrap.fill(meaning, width=30)
    lines = wrapped.split("\n")
    start_y = divider_y + 60
    for i, line in enumerate(lines):
        _draw_text_centered(draw, line, start_y + i * 44, meaning_font, fill=text_color)

    # Bottom decoration
    deco_y = CARD_HEIGHT - 200
    deco_text = "✦ ✦ ✦"
    _draw_text_centered(draw, deco_text, deco_y, number_font, fill=text_color)

    img.save(filename, "PNG", optimize=True)
    print(f"  ✓ {filename}")


def _draw_card_back(filename: str) -> None:
    """Create the card-back image."""
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), color=CARD_BACK_COLOR)
    draw = ImageDraw.Draw(img)

    # Diamond pattern
    step = 80
    for row in range(0, CARD_HEIGHT, step):
        offset = (row // step) % 2 * (step // 2)
        for col in range(-step, CARD_WIDTH + step, step):
            x = col + offset
            draw.regular_polygon(
                (x, row, 20),
                n_sides=4,
                rotation=45,
                fill=CARD_BACK_ACCENT,
            )

    # Border
    border_margin = 24
    draw.rounded_rectangle(
        (border_margin, border_margin, CARD_WIDTH - border_margin, CARD_HEIGHT - border_margin),
        radius=BORDER_RADIUS,
        outline=CARD_BACK_ACCENT,
        width=4,
    )

    # Center text
    font = _try_load_font(40)
    _draw_text_centered(draw, "L  U  V  R", CARD_HEIGHT // 2 - 20, font, fill=CARD_BACK_ACCENT)

    img.save(filename, "PNG", optimize=True)
    print(f"  ✓ {filename}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def generate_all() -> None:
    """Generate all Major Arcana cards and the card back."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Generating tarot card images → {OUTPUT_DIR}/")
    print(f"  Size: {CARD_WIDTH}×{CARD_HEIGHT}px")
    print()

    for card in MAJOR_ARCANA:
        slug = card["slug"]
        color = ARCANA_COLORS.get(slug, (200, 200, 200))
        filename = OUTPUT_DIR / f"{slug}.png"
        _draw_card(
            color=color,
            number=card["number"],
            name=card["name"],
            meaning=card["meaning"],
            filename=str(filename),
        )

    print()

    # Card back
    back_filename = OUTPUT_DIR / "card_back.png"
    _draw_card_back(str(back_filename))

    print()
    print(f"Done — {len(MAJOR_ARCANA)} Major Arcana + 1 card back generated.")
    print(f"Output: {OUTPUT_DIR.resolve()}/")


if __name__ == "__main__":
    generate_all()
