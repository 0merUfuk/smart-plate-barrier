"""Generate authentic European and Turkish license plate test images."""

import json
from pathlib import Path
import cv2
import numpy as np

OUT_DIR = Path("data/test_samples")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def draw_plate(text: str, country_code: str = "TR", bg_color=(250, 250, 250), text_color=(15, 15, 15)):
    # Standard plate dimensions: 520x110 aspect ratio (~4.7:1) -> 440x95 px
    w, h = 440, 95
    plate = np.full((h, w, 3), bg_color, dtype=np.uint8)

    # Black outer border
    cv2.rectangle(plate, (2, 2), (w - 3, h - 3), (20, 20, 20), 3)

    # Left country band (Blue Euro/TR band)
    band_w = 42
    cv2.rectangle(plate, (3, 3), (band_w, h - 4), (180, 80, 0), -1)  # Blue in BGR

    # Country code text (e.g. TR, D, F)
    cv2.putText(
        plate,
        country_code,
        (6, h - 14),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    # Main plate text
    # Calculate text positioning
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.6
    thickness = 4
    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)

    text_x = band_w + int((w - band_w - text_w) / 2)
    text_y = int((h + text_h) / 2) - 4

    cv2.putText(plate, text, (text_x, text_y), font, font_scale, text_color, thickness, cv2.LINE_AA)

    # Add subtle realistic gradient/texture noise
    noise = np.random.normal(0, 3, plate.shape).astype(np.int16)
    noisy_plate = np.clip(plate.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return noisy_plate


def create_all():
    plates_to_create = [
        ("tr_03.jpg", "34 DMO 01", "TR", "Turkish civilian (whitelist demo)"),
        ("tr_04.jpg", "06 TST 02", "TR", "Turkish civilian (whitelist demo)"),
        ("tr_05.jpg", "34 XYZ 99", "TR", "Turkish civilian (not in whitelist)"),
        ("untr_01_de.jpg", "B MW 1234", "D", "German DIN/Euro plate"),
        ("untr_03_fr.jpg", "AB 123 CD", "F", "French SIV plate"),
        ("untr_05_uk.jpg", "GB21 XYZ", "UK", "UK yellow plate", (40, 210, 245), (10, 10, 10)),
    ]

    for item in plates_to_create:
        filename, text, country, desc = item[:4]
        bg_col = item[4] if len(item) > 4 else (250, 250, 250)
        fg_col = item[5] if len(item) > 5 else (15, 15, 15)

        img = draw_plate(text, country, bg_color=bg_col, text_color=fg_col)
        out_path = OUT_DIR / filename
        cv2.imwrite(str(out_path), img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        print(f"Created {filename}: {text} ({country}) -> {out_path.stat().st_size} bytes")


if __name__ == "__main__":
    create_all()
