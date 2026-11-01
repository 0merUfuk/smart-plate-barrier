import json
import tempfile
import unittest
from pathlib import Path
import cv2
import numpy as np

from experiments.crop_plate import crop_image, process_crop


class CropPlateTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp_dir.name)

        # Create a test synthetic image 480x640 (H=480, W=640)
        self.img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Put colored rectangle at x:100..400, y:200..270
        self.img[200:270, 100:400] = (255, 255, 255)
        self.img_path = self.dir / "test_frame.jpg"
        cv2.imwrite(str(self.img_path), self.img)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_crop_image_valid(self):
        crop = crop_image(self.img, [100, 200, 400, 270])
        self.assertEqual(crop.shape, (70, 300, 3))
        # Ensure values match
        self.assertTrue(np.all(crop == 255))

    def test_crop_image_bounds_validation(self):
        # Negative coords
        with self.assertRaises(ValueError):
            crop_image(self.img, [-1, 0, 100, 100])
        # xmin >= xmax
        with self.assertRaises(ValueError):
            crop_image(self.img, [200, 100, 100, 200])
        # ymin >= ymax
        with self.assertRaises(ValueError):
            crop_image(self.img, [100, 200, 200, 100])
        # Out of bounds x
        with self.assertRaises(ValueError):
            crop_image(self.img, [100, 100, 700, 200])
        # Out of bounds y
        with self.assertRaises(ValueError):
            crop_image(self.img, [100, 100, 300, 500])

    def test_process_crop_end_to_end(self):
        out_crop = self.dir / "crop.png"
        out_meta = self.dir / "crop.json"

        meta = process_crop(self.img_path, [100, 200, 400, 270], out_crop, out_meta)

        self.assertTrue(out_crop.is_file())
        self.assertTrue(out_meta.is_file())
        self.assertEqual(meta["crop_dimensions"], {"width": 300, "height": 70})
        self.assertEqual(meta["source_dimensions"], {"width": 640, "height": 480})
        self.assertEqual(meta["box"], [100, 200, 400, 270])

        # Check saved json
        saved_meta = json.loads(out_meta.read_text())
        self.assertEqual(saved_meta["source_sha256"], meta["source_sha256"])
        self.assertEqual(saved_meta["crop_sha256"], meta["crop_sha256"])


if __name__ == "__main__":
    unittest.main()
