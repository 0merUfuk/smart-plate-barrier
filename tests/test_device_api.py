import io
import json
import tempfile
import unittest
from pathlib import Path

try:
    import cv2
    import numpy as np
    from fastapi.testclient import TestClient
    from backend.fastapi_app import create_app
    from backend.ocr import get_ocr_engine
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

AUTH_HEADER = {"Authorization": "Bearer smart-barrier-device-key-2026"}


@unittest.skipUnless(HAS_DEPS, "FastAPI, TestClient, OpenCV, and NumPy required for device API tests")
class DeviceAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ocr = get_ocr_engine("fast-plate-ocr")

        # Create valid plate JPEG for 34 DMO 01 (allowed demo plate)
        img_allowed = np.ones((70, 300, 3), dtype=np.uint8) * 255
        cv2.putText(img_allowed, "34 DMO 01", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)
        _, enc_allowed = cv2.imencode(".jpg", img_allowed)
        cls.jpeg_allowed = enc_allowed.tobytes()

        # Create plate JPEG for non-allowed plate 34 XYZ 99
        img_denied = np.ones((70, 300, 3), dtype=np.uint8) * 255
        cv2.putText(img_denied, "34 XYZ 99", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)
        _, enc_denied = cv2.imencode(".jpg", img_denied)
        cls.jpeg_denied = enc_denied.tobytes()

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
        self.tmp.close()
        self.db_path = self.tmp.name
        self.app = create_app(db_path=self.db_path, ocr_engine=self.ocr)
        self.client = TestClient(self.app)

    def tearDown(self):
        self.client.close()
        Path(self.db_path).unlink(missing_ok=True)

    def test_health_and_state(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

        resp = self.client.get("/api/state")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("34DMO01", resp.json()["allowed_plates"])

    def test_device_auth_required(self):
        # Missing token
        resp = self.client.post(
            "/api/device/v1/observations",
            content=self.jpeg_allowed,
            headers={
                "Content-Type": "image/jpeg",
                "X-Device-Id": "dev-1",
                "X-Session-Id": "sess-1",
                "X-Request-Id": "req-1",
            },
        )
        self.assertEqual(resp.status_code, 401)

        # Invalid token
        resp = self.client.post(
            "/api/device/v1/observations",
            content=self.jpeg_allowed,
            headers={
                "Content-Type": "image/jpeg",
                "Authorization": "Bearer wrong-token",
                "X-Device-Id": "dev-1",
                "X-Session-Id": "sess-1",
                "X-Request-Id": "req-1",
            },
        )
        self.assertEqual(resp.status_code, 401)

    def test_authenticated_allowed_raw_jpeg(self):
        headers = {
            "Content-Type": "image/jpeg",
            "X-Device-Id": "dev-1",
            "X-Session-Id": "sess-1",
            "X-Request-Id": "req-1",
            **AUTH_HEADER,
        }
        resp = self.client.post("/api/device/v1/observations", content=self.jpeg_allowed, headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["decision"], "allow")
        self.assertEqual(data["reason"], "exact_match")
        self.assertEqual(data["duplicate"], False)
        self.assertEqual(data["plate"], "34DMO01")
        self.assertIn("ocr", data)
        self.assertGreater(data["ocr"]["latency_ms"], 0)

    def test_authenticated_denied_raw_jpeg(self):
        headers = {
            "Content-Type": "image/jpeg",
            "X-Device-Id": "dev-1",
            "X-Session-Id": "sess-1",
            "X-Request-Id": "req-denied-1",
            **AUTH_HEADER,
        }
        resp = self.client.post("/api/device/v1/observations", content=self.jpeg_denied, headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["decision"], "deny")
        self.assertEqual(data["reason"], "not_in_allowlist")

    def test_idempotent_duplicate_observation(self):
        headers = {
            "Content-Type": "image/jpeg",
            "X-Device-Id": "dev-1",
            "X-Session-Id": "sess-1",
            "X-Request-Id": "req-dup-1",
            **AUTH_HEADER,
        }
        resp1 = self.client.post("/api/device/v1/observations", content=self.jpeg_allowed, headers=headers)
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp1.json()["duplicate"], False)

        # Send same request again with exact same image
        resp2 = self.client.post("/api/device/v1/observations", content=self.jpeg_allowed, headers=headers)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json()["duplicate"], True)
        self.assertEqual(resp2.json()["decision"], resp1.json()["decision"])

    def test_conflicting_request_different_image(self):
        headers = {
            "Content-Type": "image/jpeg",
            "X-Device-Id": "dev-1",
            "X-Session-Id": "sess-1",
            "X-Request-Id": "req-conflict-1",
            **AUTH_HEADER,
        }
        # First request with allowed plate
        resp1 = self.client.post("/api/device/v1/observations", content=self.jpeg_allowed, headers=headers)
        self.assertEqual(resp1.status_code, 200)

        # Second request with SAME request_id but DIFFERENT image payload
        resp2 = self.client.post("/api/device/v1/observations", content=self.jpeg_denied, headers=headers)
        self.assertEqual(resp2.status_code, 409)

    def test_multipart_form_observation(self):
        meta = {
            "device_id": "dev-form",
            "session_id": "sess-form",
            "request_id": "req-form-1",
        }
        files = {
            "metadata": (None, json.dumps(meta), "application/json"),
            "image": ("capture.jpg", io.BytesIO(self.jpeg_allowed), "image/jpeg"),
        }
        resp = self.client.post("/api/device/v1/observations", files=files, headers=AUTH_HEADER)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["decision"], "allow")
        self.assertEqual(data["device_id"], "dev-form")

    def test_oversized_image_rejected(self):
        oversized = b"X" * (512_000 + 10)
        headers = {
            "Content-Type": "image/jpeg",
            "X-Device-Id": "dev-1",
            "X-Session-Id": "sess-1",
            "X-Request-Id": "req-large",
            **AUTH_HEADER,
        }
        resp = self.client.post("/api/device/v1/observations", content=oversized, headers=headers)
        self.assertEqual(resp.status_code, 413)

    def test_device_event_telemetry(self):
        payload = {
            "device_id": "dev-1",
            "session_id": "sess-1",
            "event_id": "evt-001",
            "event_type": "barrier_opened",
            "barrier_state": "open",
            "details": {"duration_ms": 1200},
        }
        resp = self.client.post("/api/device/v1/events", json=payload, headers=AUTH_HEADER)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["duplicate"], False)

        # Repeating event
        resp_dup = self.client.post("/api/device/v1/events", json=payload, headers=AUTH_HEADER)
        self.assertEqual(resp_dup.status_code, 200)
        self.assertEqual(resp_dup.json()["duplicate"], True)

    def test_device_auth_x_token_header(self):
        headers = {
            "Content-Type": "image/jpeg",
            "X-Device-Id": "dev-token-test",
            "X-Session-Id": "sess-token",
            "X-Request-Id": "req-token-1",
            "X-Device-Token": "smart-barrier-device-key-2026",
        }
        resp = self.client.post("/api/device/v1/observations", content=self.jpeg_allowed, headers=headers)
        self.assertEqual(resp.status_code, 200)

    def test_raw_jpeg_missing_headers(self):
        headers = {
            "Content-Type": "image/jpeg",
            "X-Device-Id": "dev-1",
            # Missing X-Session-Id and X-Request-Id
            **AUTH_HEADER,
        }
        resp = self.client.post("/api/device/v1/observations", content=self.jpeg_allowed, headers=headers)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("missing required headers", resp.json()["detail"])

    def test_empty_image_payload(self):
        headers = {
            "Content-Type": "image/jpeg",
            "X-Device-Id": "dev-1",
            "X-Session-Id": "sess-1",
            "X-Request-Id": "req-empty-1",
            **AUTH_HEADER,
        }
        resp = self.client.post("/api/device/v1/observations", content=b"", headers=headers)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("empty image payload", resp.json()["detail"])

    def test_unsupported_media_type(self):
        headers = {
            "Content-Type": "application/json",
            **AUTH_HEADER,
        }
        resp = self.client.post("/api/device/v1/observations", content=b"{}", headers=headers)
        self.assertEqual(resp.status_code, 415)

    def test_multipart_missing_fields(self):
        files = {
            "metadata": (None, json.dumps({"device_id": "d", "session_id": "s", "request_id": "r"}), "application/json"),
            # Missing image field
        }
        resp = self.client.post("/api/device/v1/observations", files=files, headers=AUTH_HEADER)
        self.assertEqual(resp.status_code, 400)

    def test_multipart_invalid_metadata(self):
        files = {
            "metadata": (None, "not-valid-json", "application/json"),
            "image": ("test.jpg", io.BytesIO(self.jpeg_allowed), "image/jpeg"),
        }
        resp = self.client.post("/api/device/v1/observations", files=files, headers=AUTH_HEADER)
        self.assertEqual(resp.status_code, 400)

    def test_fastapi_demo_endpoints(self):
        # Demo scan
        scan_payload = {"request_id": "demo-fastapi-1", "plate": "34 DMO 01", "confidence": 0.95}
        resp = self.client.post("/api/demo/scan", json=scan_payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["decision"], "allow")

        # Duplicate scan with different payload -> 409 Conflict
        conflicting_payload = {"request_id": "demo-fastapi-1", "plate": "35 ABC 99", "confidence": 0.95}
        resp_conflict = self.client.post("/api/demo/scan", json=conflicting_payload)
        self.assertEqual(resp_conflict.status_code, 409)

        # Bad scan request -> 400
        resp_bad = self.client.post("/api/demo/scan", json={"bad": "payload"})
        self.assertEqual(resp_bad.status_code, 400)

        # Demo clear
        resp_clear = self.client.post("/api/demo/clear")
        self.assertEqual(resp_clear.status_code, 200)
        self.assertEqual(resp_clear.json()["barrier"], "closed")

        # Add plate
        resp_add = self.client.post("/api/plates/add", json={"plate": "06 ANK 06"})
        self.assertEqual(resp_add.status_code, 200)
        self.assertEqual(resp_add.json()["plate"], "06ANK06")

        # Add plate with invalid format -> 400
        resp_add_bad = self.client.post("/api/plates/add", json={"plate": "INVALID@@@"})
        self.assertEqual(resp_add_bad.status_code, 400)

        # Remove plate
        resp_rem = self.client.post("/api/plates/remove", json={"plate": "06 ANK 06"})
        self.assertEqual(resp_rem.status_code, 200)
        self.assertFalse(resp_rem.json()["added"])

        # Remove plate with invalid format -> 400
        resp_rem_bad = self.client.post("/api/plates/remove", json={"plate": "INVALID@@@"})
        self.assertEqual(resp_rem_bad.status_code, 400)

    def test_ocr_decision_branches_in_store(self):
        from backend.store import Store
        from backend.ocr import OCRResult

        test_store = Store(self.db_path)

        # 1. OCR error
        res_error = OCRResult(
            status="error",
            raw_text="",
            normalized_text="",
            confidence=0.0,
            score_definition="none",
            roi=None,
            crop_size={"width": 0, "height": 0},
            engine="test",
            model_name="test",
            latency_ms=1.0,
            error="camera_sensor_offline",
        )
        rec1 = test_store.record_device_observation("d", "s", "req-err-1", "sha1", res_error)
        self.assertEqual(rec1["decision"], "error")
        self.assertEqual(rec1["reason"], "camera_sensor_offline")

        # 2. OCR unreadable
        res_unreadable = OCRResult(
            status="unreadable",
            raw_text="???",
            normalized_text="",
            confidence=0.0,
            score_definition="none",
            roi=None,
            crop_size={"width": 50, "height": 20},
            engine="test",
            model_name="test",
            latency_ms=1.0,
        )
        rec2 = test_store.record_device_observation("d", "s", "req-unread-1", "sha2", res_unreadable)
        self.assertEqual(rec2["decision"], "unreadable")

        # 3. Invalid plate format
        res_bad_fmt = OCRResult(
            status="ok",
            raw_text="NOTAPLATEFORMAT123",
            normalized_text="NOTAPLATEFORMAT123",
            confidence=0.99,
            score_definition="none",
            roi=None,
            crop_size={"width": 200, "height": 50},
            engine="test",
            model_name="test",
            latency_ms=1.0,
        )
        rec3 = test_store.record_device_observation("d", "s", "req-fmt-1", "sha3", res_bad_fmt)
        self.assertEqual(rec3["decision"], "unreadable")
        self.assertEqual(rec3["reason"], "invalid_plate_format")

        # 4. Low confidence
        res_low_conf = OCRResult(
            status="ok",
            raw_text="34 DMO 01",
            normalized_text="34DMO01",
            confidence=0.60,  # Below CONFIDENCE_THRESHOLD (0.85)
            score_definition="none",
            roi=None,
            crop_size={"width": 200, "height": 50},
            engine="test",
            model_name="test",
            latency_ms=1.0,
        )
        rec4 = test_store.record_device_observation("d", "s", "req-low-1", "sha4", res_low_conf)
        self.assertEqual(rec4["decision"], "unreadable")
        self.assertEqual(rec4["reason"], "low_confidence")


if __name__ == "__main__":
    unittest.main()
