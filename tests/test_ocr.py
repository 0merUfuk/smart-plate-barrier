import unittest

try:
    import numpy as np
    import cv2
    from backend.ocr import (
        decode_image_input,
        get_ocr_engine,
        FastPlateOCRAdapter,
        OCRResult,
    )
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False


@unittest.skipUnless(HAS_DEPS, "OpenCV, NumPy, and fast-plate-ocr required for OCR tests")
class OCRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize model once for testing
        cls.engine = get_ocr_engine("fast-plate-ocr")

        # Create a synthetic plate crop with clear text '34DMO01'
        cls.plate_img = np.ones((70, 300, 3), dtype=np.uint8) * 255
        cv2.putText(
            cls.plate_img,
            "34 DMO 01",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 0, 0),
            3,
        )

    def test_decode_image_input_validation(self):
        import tempfile
        from pathlib import Path
        from backend.ocr import BasePlateOCR

        # Empty array
        with self.assertRaises(ValueError):
            decode_image_input(np.array([]))

        # Empty bytes
        with self.assertRaises(ValueError):
            decode_image_input(b"")

        # Corrupt bytes
        with self.assertRaises(ValueError):
            decode_image_input(b"not-a-valid-image-stream")

        # Unsupported type
        with self.assertRaises(TypeError):
            decode_image_input(12345)

        # Non-existent file
        with self.assertRaises(FileNotFoundError):
            decode_image_input("non_existent_file_path_xyz.jpg")

        # Valid array
        decoded = decode_image_input(self.plate_img)
        self.assertEqual(decoded.shape, (70, 300, 3))

        # Grayscale 2D array
        gray = cv2.cvtColor(self.plate_img, cv2.COLOR_BGR2GRAY)
        decoded_gray = decode_image_input(gray)
        self.assertEqual(decoded_gray.shape, (70, 300, 3))

        # From file path (Path and str)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            cv2.imwrite(f.name, self.plate_img)
            temp_path = f.name

        try:
            d_str = decode_image_input(temp_path)
            self.assertEqual(d_str.shape, (70, 300, 3))
            d_path = decode_image_input(Path(temp_path))
            self.assertEqual(d_path.shape, (70, 300, 3))
        finally:
            Path(temp_path).unlink(missing_ok=True)

        # BasePlateOCR abstract method
        with self.assertRaises(NotImplementedError):
            BasePlateOCR().recognize(self.plate_img)

    def test_ocr_result_to_dict(self):
        result = self.engine.recognize(self.plate_img)
        d = result.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["normalized_text"], "34DMO01")
        self.assertEqual(d["status"], "ok")

    def test_fast_plate_ocr_crop_edge_cases(self):
        # Invalid ROI length != 4
        res_bad_len = self.engine.recognize(self.plate_img, roi=[10, 20])
        self.assertEqual(res_bad_len.status, "error")

        # Tiny crop (< 8 height or < 16 width)
        tiny = np.zeros((5, 10, 3), dtype=np.uint8)
        res_tiny = self.engine.recognize(tiny)
        self.assertEqual(res_tiny.status, "unreadable")
        self.assertEqual(res_tiny.error, "crop_too_small")

    def test_get_ocr_engine_unsupported(self):
        with self.assertRaises(ValueError):
            get_ocr_engine("invalid_engine_name")

    def test_easyocr_adapter_mocked_results(self):
        from unittest.mock import MagicMock
        from backend.ocr import EasyOCRAdapter

        adapter = EasyOCRAdapter.__new__(EasyOCRAdapter)
        adapter.model_name = "easyocr-craft-crnn"
        adapter.engine_name = "easyocr"

        # Mock reader returning bounding box, text, confidence
        # Format: [([[x1,y1], [x2,y2], [x3,y3], [x4,y4]], "34 DMO 01", 0.95)]
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 30], [0, 30]], "34 DMO 01", 0.95)
        ]
        adapter._reader = mock_reader

        res = adapter.recognize(self.plate_img)
        self.assertEqual(res.status, "ok")
        self.assertEqual(res.normalized_text, "34DMO01")
        self.assertEqual(res.engine, "easyocr")

        # Mock reader returning empty list (no text detected)
        mock_reader.readtext.return_value = []
        res_empty = adapter.recognize(self.plate_img)
        self.assertEqual(res_empty.status, "unreadable")
        self.assertEqual(res_empty.error, "no_text_detected")

        # Tiny crop on easyocr
        tiny = np.zeros((4, 4, 3), dtype=np.uint8)
        res_tiny = adapter.recognize(tiny)
        self.assertEqual(res_tiny.status, "unreadable")
        self.assertEqual(res_tiny.error, "crop_too_small")

    def test_fast_plate_ocr_recognition(self):
        result = self.engine.recognize(self.plate_img)

        self.assertIsInstance(result, OCRResult)
        self.assertEqual(result.engine, "fast-plate-ocr")
        self.assertIn("34DMO01", result.normalized_text)
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
        self.assertEqual(result.score_definition, "char_prob_mean_without_padding")
        self.assertGreater(result.latency_ms, 0.0)
        self.assertIsNone(result.error)

    def test_fast_plate_ocr_with_roi(self):
        # Embed the plate into a 480x640 frame at (100, 200, 400, 270)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[200:270, 100:400] = self.plate_img

        result = self.engine.recognize(frame, roi=[100, 200, 400, 270])
        self.assertIsInstance(result, OCRResult)
        self.assertIn("34DMO01", result.normalized_text)
        self.assertEqual(result.roi, [100, 200, 400, 270])
        self.assertEqual(result.crop_size, {"width": 300, "height": 70})

    def test_fast_plate_ocr_invalid_roi_returns_error(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # roi exceeding bounds
        result = self.engine.recognize(frame, roi=[100, 200, 800, 270])
        self.assertEqual(result.status, "error")
        self.assertIsNotNone(result.error)

    def test_fast_plate_ocr_blank_image(self):
        # A completely black image should not crash
        blank = np.zeros((70, 300, 3), dtype=np.uint8)
        result = self.engine.recognize(blank)
        self.assertIsInstance(result, OCRResult)
        self.assertEqual(result.status, "unreadable")

    def test_fast_plate_ocr_corrupt_bytes_returns_error(self):
        result = self.engine.recognize(b"corrupt-data")
        self.assertEqual(result.status, "error")
        self.assertIsNotNone(result.error)


if __name__ == "__main__":
    unittest.main()
