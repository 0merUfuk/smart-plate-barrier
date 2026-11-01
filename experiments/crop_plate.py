"""Manual plate ROI cropping utility.

Extracts a bounding box from an image, writes the cropped patch,
and records coordinate and provenance metadata.
"""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence
import cv2
import numpy as np


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def crop_image(
    image: np.ndarray,
    box: Sequence[int],
) -> np.ndarray:
    """Crop an image using [xmin, ymin, xmax, ymax] coordinates.

    Coordinates must be non-negative integers where xmin < xmax and ymin < ymax,
    and must not exceed the image boundaries.
    """
    if len(box) != 4:
        raise ValueError(f"box must contain 4 values [xmin, ymin, xmax, ymax], got {len(box)}")

    xmin, ymin, xmax, ymax = [int(v) for v in box]
    h, w = image.shape[:2]

    if xmin < 0 or ymin < 0:
        raise ValueError(f"coordinates cannot be negative: box={[xmin, ymin, xmax, ymax]}")
    if xmin >= xmax:
        raise ValueError(f"xmin ({xmin}) must be strictly less than xmax ({xmax})")
    if ymin >= ymax:
        raise ValueError(f"ymin ({ymin}) must be strictly less than ymax ({ymax})")
    if xmax > w:
        raise ValueError(f"xmax ({xmax}) exceeds image width ({w})")
    if ymax > h:
        raise ValueError(f"ymax ({ymax}) exceeds image height ({h})")

    return image[ymin:ymax, xmin:xmax].copy()


def process_crop(
    input_path: str | Path,
    box: Sequence[int],
    output_path: str | Path,
    metadata_path: str | Path | None = None,
) -> dict:
    input_path = Path(input_path)
    if not input_path.is_file():
        raise FileNotFoundError(f"input image not found: {input_path}")

    raw_bytes = input_path.read_bytes()
    image = cv2.imdecode(np.frombuffer(raw_bytes, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"failed to decode image: {input_path}")

    orig_h, orig_w = image.shape[:2]
    crop = crop_image(image, box)
    crop_h, crop_w = crop.shape[:2]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Encode and save cropped image
    ext = output_path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        success, encoded = cv2.imencode(".jpg", crop, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    elif ext == ".png":
        success, encoded = cv2.imencode(".png", crop)
    else:
        success, encoded = cv2.imencode(".png", crop)

    if not success:
        raise RuntimeError("failed to encode cropped image")

    crop_bytes = encoded.tobytes()
    output_path.write_bytes(crop_bytes)

    metadata = {
        "source_image": str(input_path.resolve()),
        "source_sha256": compute_sha256(raw_bytes),
        "source_dimensions": {"width": orig_w, "height": orig_h},
        "box": [int(v) for v in box],
        "box_format": "xmin_ymin_xmax_ymax",
        "crop_dimensions": {"width": crop_w, "height": crop_h},
        "crop_image": str(output_path.resolve()),
        "crop_sha256": compute_sha256(crop_bytes),
    }

    if metadata_path:
        meta_p = Path(metadata_path)
        meta_p.parent.mkdir(parents=True, exist_ok=True)
        meta_p.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")

    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to input full image")
    parser.add_argument(
        "--box",
        nargs=4,
        type=int,
        required=True,
        metavar=("XMIN", "YMIN", "XMAX", "YMAX"),
        help="Bounding box coordinates: xmin ymin xmax ymax",
    )
    parser.add_argument("--output", "-o", required=True, help="Path for cropped output image")
    parser.add_argument("--metadata", "-m", help="Path for output JSON metadata file")
    args = parser.parse_args()

    meta = process_crop(args.input, args.box, args.output, args.metadata)
    print(f"Cropped {meta['crop_dimensions']['width']}x{meta['crop_dimensions']['height']} -> {args.output}")


if __name__ == "__main__":
    main()
