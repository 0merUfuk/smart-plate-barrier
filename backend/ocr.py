"""Model-independent OCR interface and adapters for license plate recognition.

This module provides a unified interface for plate recognition engines,
enforcing clean separation between raw model output and authorization logic.
OCR engines return text, confidence, and quality indicators, NEVER access decisions.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import time
from typing import Any, Sequence

import cv2
import numpy as np

from .domain import normalize_plate, CONFIDENCE_THRESHOLD


@dataclasses.dataclass(frozen=True)
class OCRResult:
    """Unified result contract for any license plate OCR engine."""
    status: str  # "ok", "unreadable", "error"
    raw_text: str
    normalized_text: str
    confidence: float
    score_definition: str
    roi: list[int] | None
    crop_size: dict[str, int]
    engine: str
    model_name: str
    latency_ms: float
    country_hint: str | None = None
    country_prob: float | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def decode_image_input(source: bytes | str | Path | np.ndarray) -> np.ndarray:
    """Safely decode image input from bytes, file path, or numpy array to BGR image."""
    if isinstance(source, np.ndarray):
        if source.size == 0 or len(source.shape) < 2:
            raise ValueError("empty or invalid numpy array")
        if len(source.shape) == 2:
            return cv2.cvtColor(source, cv2.COLOR_GRAY2BGR)
        return source.copy()

    if isinstance(source, (str, Path)):
        p = Path(source)
        if not p.is_file():
            raise FileNotFoundError(f"image file not found: {p}")
        raw = p.read_bytes()
    elif isinstance(source, (bytes, bytearray)):
        raw = bytes(source)
    else:
        raise TypeError(f"unsupported image input type: {type(source)}")

    if len(raw) == 0:
        raise ValueError("empty image payload (0 bytes)")

    img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("failed to decode image data into valid image matrix")
    return img


class BasePlateOCR:
    """Abstract base adapter for license plate OCR models."""

    def recognize(
        self,
        source: bytes | str | Path | np.ndarray,
        roi: Sequence[int] | None = None,
    ) -> OCRResult:
        raise NotImplementedError


class FastPlateOCRAdapter(BasePlateOCR):
    """ONNX-based license plate recognizer using fast-plate-ocr."""

    def __init__(
        self,
        onnx_model_path: str | Path | None = None,
        plate_config_path: str | Path | None = None,
        device: str = "cpu",
    ):
        from fast_plate_ocr import LicensePlateRecognizer

        # Use project models directory by default if present
        repo_root = Path(__file__).resolve().parents[1]
        default_onnx = repo_root / "data" / "models" / "cct_s_v2_global.onnx"
        default_cfg = repo_root / "data" / "models" / "cct_s_v2_global_plate_config.yaml"

        if onnx_model_path is None and default_onnx.is_file():
            onnx_model_path = default_onnx
        if plate_config_path is None and default_cfg.is_file():
            plate_config_path = default_cfg

        self.model_name = "cct-s-v2-global-model"
        self.engine_name = "fast-plate-ocr"
        self.onnx_model_path = str(onnx_model_path) if onnx_model_path else None
        self.plate_config_path = str(plate_config_path) if plate_config_path else None

        if self.onnx_model_path and self.plate_config_path:
            self._recognizer = LicensePlateRecognizer(
                onnx_model_path=self.onnx_model_path,
                plate_config_path=self.plate_config_path,
                device=device,
            )
        else:
            self._recognizer = LicensePlateRecognizer(
                hub_ocr_model=self.model_name,
                device=device,
            )

    def recognize(
        self,
        source: bytes | str | Path | np.ndarray,
        roi: Sequence[int] | None = None,
    ) -> OCRResult:
        start_t = time.perf_counter()
        box_roi = [int(v) for v in roi] if roi is not None else None

        try:
            image = decode_image_input(source)
            h, w = image.shape[:2]

            if box_roi is not None:
                if len(box_roi) != 4:
                    raise ValueError(f"box must have 4 coordinates, got {len(box_roi)}")
                xmin, ymin, xmax, ymax = box_roi
                if xmin < 0 or ymin < 0 or xmin >= xmax or ymin >= ymax or xmax > w or ymax > h:
                    raise ValueError(f"invalid ROI coordinates {box_roi} for image size {w}x{h}")
                crop = image[ymin:ymax, xmin:xmax]
            else:
                crop = image

            crop_h, crop_w = crop.shape[:2]
            if crop_h < 8 or crop_w < 16:
                latency = (time.perf_counter() - start_t) * 1000.0
                return OCRResult(
                    status="unreadable",
                    raw_text="",
                    normalized_text="",
                    confidence=0.0,
                    score_definition="char_prob_mean_without_padding",
                    roi=box_roi,
                    crop_size={"width": crop_w, "height": crop_h},
                    engine=self.engine_name,
                    model_name=self.model_name,
                    latency_ms=round(latency, 2),
                    error="crop_too_small",
                )

            # Convert BGR to RGB for inference
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            predictions = self._recognizer.run(crop_rgb, return_confidence=True)
            latency = (time.perf_counter() - start_t) * 1000.0

            if not predictions:
                return OCRResult(
                    status="unreadable",
                    raw_text="",
                    normalized_text="",
                    confidence=0.0,
                    score_definition="char_prob_mean_without_padding",
                    roi=box_roi,
                    crop_size={"width": crop_w, "height": crop_h},
                    engine=self.engine_name,
                    model_name=self.model_name,
                    latency_ms=round(latency, 2),
                    error="no_prediction",
                )

            pred = predictions[0]
            raw_text = pred.plate or ""
            normalized = normalize_plate(raw_text) if raw_text else ""

            # Exclude padding character probabilities from the confidence score
            plate_len = len(raw_text)
            if plate_len > 0 and pred.char_probs is not None and len(pred.char_probs) >= plate_len:
                char_probs_active = pred.char_probs[:plate_len]
                confidence = float(np.mean(char_probs_active))
            else:
                confidence = 0.0

            confidence = max(0.0, min(1.0, float(confidence)))

            status = "ok" if (len(normalized) >= 4 and confidence >= 0.5) else "unreadable"

            return OCRResult(
                status=status,
                raw_text=raw_text,
                normalized_text=normalized,
                confidence=round(confidence, 4),
                score_definition="char_prob_mean_without_padding",
                roi=box_roi,
                crop_size={"width": crop_w, "height": crop_h},
                engine=self.engine_name,
                model_name=self.model_name,
                latency_ms=round(latency, 2),
                country_hint=pred.region if pred.region and pred.region != "Unknown" else None,
                country_prob=round(float(pred.region_prob), 4) if pred.region_prob is not None else None,
            )

        except Exception as exc:
            latency = (time.perf_counter() - start_t) * 1000.0
            return OCRResult(
                status="error",
                raw_text="",
                normalized_text="",
                confidence=0.0,
                score_definition="char_prob_mean_without_padding",
                roi=box_roi,
                crop_size={"width": 0, "height": 0},
                engine=self.engine_name,
                model_name=self.model_name,
                latency_ms=round(latency, 2),
                error=str(exc),
            )


class EasyOCRAdapter(BasePlateOCR):
    """EasyOCR backend comparison adapter."""

    def __init__(self, languages: list[str] | None = None, gpu: bool = False):
        import easyocr

        self.model_name = "easyocr-craft-crnn"
        self.engine_name = "easyocr"
        self._reader = easyocr.Reader(languages or ["en"], gpu=gpu)

    def recognize(
        self,
        source: bytes | str | Path | np.ndarray,
        roi: Sequence[int] | None = None,
    ) -> OCRResult:
        start_t = time.perf_counter()
        box_roi = [int(v) for v in roi] if roi is not None else None

        try:
            image = decode_image_input(source)
            h, w = image.shape[:2]

            if box_roi is not None:
                if len(box_roi) != 4:
                    raise ValueError(f"box must have 4 coordinates, got {len(box_roi)}")
                xmin, ymin, xmax, ymax = box_roi
                if xmin < 0 or ymin < 0 or xmin >= xmax or ymin >= ymax or xmax > w or ymax > h:
                    raise ValueError(f"invalid ROI coordinates {box_roi} for image size {w}x{h}")
                crop = image[ymin:ymax, xmin:xmax]
            else:
                crop = image

            crop_h, crop_w = crop.shape[:2]
            if crop_h < 8 or crop_w < 16:
                latency = (time.perf_counter() - start_t) * 1000.0
                return OCRResult(
                    status="unreadable",
                    raw_text="",
                    normalized_text="",
                    confidence=0.0,
                    score_definition="easyocr_confidence_mean",
                    roi=box_roi,
                    crop_size={"width": crop_w, "height": crop_h},
                    engine=self.engine_name,
                    model_name=self.model_name,
                    latency_ms=round(latency, 2),
                    error="crop_too_small",
                )

            # EasyOCR expects RGB
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            results = self._reader.readtext(crop_rgb)
            latency = (time.perf_counter() - start_t) * 1000.0

            if not results:
                return OCRResult(
                    status="unreadable",
                    raw_text="",
                    normalized_text="",
                    confidence=0.0,
                    score_definition="easyocr_confidence_mean",
                    roi=box_roi,
                    crop_size={"width": crop_w, "height": crop_h},
                    engine=self.engine_name,
                    model_name=self.model_name,
                    latency_ms=round(latency, 2),
                    error="no_text_detected",
                )

            # Concatenate all detected text pieces sorted left-to-right
            results_sorted = sorted(results, key=lambda r: r[0][0][0])
            raw_parts = [r[1] for r in results_sorted]
            conf_parts = [float(r[2]) for r in results_sorted]

            raw_text = "".join(raw_parts)
            normalized = normalize_plate(raw_text) if raw_text else ""
            confidence = float(np.mean(conf_parts)) if conf_parts else 0.0

            status = "ok" if (len(normalized) >= 4 and confidence >= 0.5) else "unreadable"

            return OCRResult(
                status=status,
                raw_text=raw_text,
                normalized_text=normalized,
                confidence=round(confidence, 4),
                score_definition="easyocr_confidence_mean",
                roi=box_roi,
                crop_size={"width": crop_w, "height": crop_h},
                engine=self.engine_name,
                model_name=self.model_name,
                latency_ms=round(latency, 2),
            )

        except Exception as exc:
            latency = (time.perf_counter() - start_t) * 1000.0
            return OCRResult(
                status="error",
                raw_text="",
                normalized_text="",
                confidence=0.0,
                score_definition="easyocr_confidence_mean",
                roi=box_roi,
                crop_size={"width": 0, "height": 0},
                engine=self.engine_name,
                model_name=self.model_name,
                latency_ms=round(latency, 2),
                error=str(exc),
            )


def get_ocr_engine(engine_name: str = "fast-plate-ocr", **kwargs) -> BasePlateOCR:
    """Factory for obtaining a configured OCR engine instance."""
    if engine_name == "fast-plate-ocr":
        return FastPlateOCRAdapter(**kwargs)
    elif engine_name == "easyocr":
        return EasyOCRAdapter(**kwargs)
    else:
        raise ValueError(f"unsupported OCR engine: {engine_name}")
