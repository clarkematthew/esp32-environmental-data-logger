"""Render the latest environmental data as an Inky/e-paper dashboard.

This module can run on a Raspberry Pi with Inky hardware attached, or on a
development machine where it writes only a preview PNG.
"""

import argparse
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

try:
    from inky.auto import auto
except ImportError:  # Allows local previewing on non-Pi machines.
    auto = None


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
DATA_FILE = DATA_DIR / "data.csv"
DEFAULT_PREVIEW = DATA_DIR / "display_preview.png"
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 480
BACKGROUND = "#f6f1e8"
PANEL = "#fffaf1"
TEXT = "#111111"
MUTED = "#4f4a45"
ACCENT_WARM = "#d85a3a"
ACCENT_COOL = "#3e6b7f"
ACCENT_GOLD = "#d7a42b"
GRID = "#d8ccbb"

FONT_CANDIDATES = {
    "title": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ],
    "body": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ],
    "mono": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ],
}


def load_font(kind, size):
    """Load the first available font for a display role, or PIL's default."""
    for candidate in FONT_CANDIDATES[kind]:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def load_data():
    """Read data.csv and return readings sorted by valid timestamp."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"{DATA_FILE} was not found.")

    df = pd.read_csv(DATA_FILE)
    if df.empty:
        raise ValueError("data.csv does not contain any readings yet.")

    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    df = df.dropna(subset=["Time"]).sort_values("Time")
    if df.empty:
        raise ValueError("No readable timestamps were found in data.csv.")

    return df


def format_delta(current, previous, unit, decimals=1):
    """Format the signed change between the latest and previous reading."""
    delta = current - previous
    sign = "+" if delta >= 0 else "-"
    return f"{sign}{abs(delta):.{decimals}f}{unit}"


def metric_block(draw, xy, size, label, value, unit, delta=None, accent=ACCENT_WARM):
    """Draw one dashboard metric tile with an optional change badge."""
    x, y = xy
    w, h = size
    draw.rounded_rectangle((x, y, x + w, y + h), radius=18, fill=PANEL, outline=GRID, width=2)

    label_font = load_font("body", 20)
    value_font = load_font("title", 32)
    delta_font = load_font("mono", 16)

    draw.text((x + 18, y + 14), label, font=label_font, fill=MUTED)
    draw.text((x + 18, y + 44), f"{value}{unit}", font=value_font, fill=TEXT)
    if delta is not None:
        delta_box_top = y + h - 34
        delta_box_bottom = y + h - 10
        draw.rounded_rectangle((x + 18, delta_box_top, x + 136, delta_box_bottom), radius=10, fill=accent)
        draw.text((x + 28, delta_box_top + 3), delta, font=delta_font, fill="white")


def render_dashboard(df, width, height):
    """Create a dashboard image from the latest readings."""
    latest = df.iloc[-1]
    previous = df.iloc[-2] if len(df) > 1 else latest

    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)

    title_font = load_font("title", 42)
    body_font = load_font("body", 22)
    mono_font = load_font("mono", 20)

    draw.rounded_rectangle((20, 20, width - 20, height - 20), radius=28, outline=GRID, width=3, fill=BACKGROUND)
    draw.text((38, 32), "Indoor Climate", font=title_font, fill=TEXT)
    draw.text((40, 86), "BME680 live from the ESP32", font=body_font, fill=MUTED)

    updated_label = latest["Time"].strftime("%b %d, %Y  %I:%M %p")
    draw.rounded_rectangle((width - 270, 30, width - 40, 92), radius=18, fill=PANEL, outline=GRID, width=2)
    draw.text((width - 250, 46), "LAST UPDATE", font=mono_font, fill=MUTED)
    draw.text((width - 250, 66), updated_label, font=load_font("body", 19), fill=TEXT)

    metric_block(
        draw,
        (38, 126),
        (230, 112),
        "Temperature",
        f"{latest['Temperature (F)']:.1f}",
        " F",
        format_delta(latest["Temperature (F)"], previous["Temperature (F)"], " F"),
        ACCENT_WARM,
    )
    metric_block(
        draw,
        (286, 126),
        (230, 112),
        "Humidity",
        f"{latest['Humidity (%)']:.1f}",
        " %",
        format_delta(latest["Humidity (%)"], previous["Humidity (%)"], "%"),
        ACCENT_COOL,
    )
    metric_block(
        draw,
        (534, 126),
        (228, 112),
        "Pressure",
        f"{latest['Pressure (hPa)']:.1f}",
        " hPa",
        format_delta(latest["Pressure (hPa)"], previous["Pressure (hPa)"], " hPa"),
        ACCENT_GOLD,
    )

    metric_block(
        draw,
        (38, 264),
        (230, 112),
        "Gas Resistance",
        f"{latest['Gas (KOhms)']:.1f}",
        " kOhm",
        format_delta(latest["Gas (KOhms)"], previous["Gas (KOhms)"], " k"),
        ACCENT_COOL,
    )
    metric_block(
        draw,
        (286, 264),
        (230, 112),
        "Altitude",
        f"{latest['Altitude (ft)']:.1f}",
        " ft",
        None,
        ACCENT_GOLD,
    )

    recent = df.tail(24)
    temp_min = recent["Temperature (F)"].min()
    temp_max = recent["Temperature (F)"].max()
    humidity_avg = recent["Humidity (%)"].mean()
    pressure_avg = recent["Pressure (hPa)"].mean()

    draw.rounded_rectangle((534, 264, 762, 438), radius=18, fill=PANEL, outline=GRID, width=2)
    draw.text((552, 282), "Daily Snapshot", font=load_font("body", 20), fill=MUTED)
    draw.text((552, 316), f"Temp range", font=load_font("body", 18), fill=MUTED)
    draw.text((552, 338), f"{temp_min:.1f} to {temp_max:.1f} F", font=load_font("title", 24), fill=TEXT)
    draw.text((552, 372), f"Humidity avg {humidity_avg:.1f} %", font=load_font("body", 20), fill=TEXT)
    draw.text((552, 400), f"Pressure avg {pressure_avg:.1f} hPa", font=load_font("body", 20), fill=TEXT)

    return image


def update_display(preview=None, no_hardware=False):
    """Render the dashboard, update Inky when available, and save a preview."""
    df = load_data()

    if auto is not None and not no_hardware:
        display = auto()
        width, height = display.resolution
        image = render_dashboard(df, width, height)
        display.set_image(image)
        display.show()
        print(f"Updated Inky display at {width}x{height}.")
    else:
        width, height = DEFAULT_WIDTH, DEFAULT_HEIGHT
        image = render_dashboard(df, width, height)

    preview_path = Path(preview) if preview is not None else DEFAULT_PREVIEW
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(preview_path)
    print(f"Saved preview to {preview_path}.")


def main():
    """Parse CLI flags and render the dashboard."""
    parser = argparse.ArgumentParser(description="Render the latest environmental data to an Inky display.")
    parser.add_argument("--preview", default=str(DEFAULT_PREVIEW), help="Preview image output path.")
    parser.add_argument("--no-hardware", action="store_true", help="Skip the physical display update.")
    args = parser.parse_args()

    update_display(preview=args.preview, no_hardware=args.no_hardware)


if __name__ == "__main__":
    main()
