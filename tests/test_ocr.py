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
        # Empty array
        with self.assertRaises(ValueError):
            decode_image_input(np.array([]))

        # Empty bytes
        with self.assertRaises(ValueError):
            decode_image_input(b"")

        # Corrupt bytes
        with self.assertRaises(ValueError):
            decode_image_input(b"not-a-valid-image-stream")

        # Valid array
        decoded = decode_image_input(self.plate_img)
        self.assertEqual(decoded.shape, (70, 300, 3))

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
