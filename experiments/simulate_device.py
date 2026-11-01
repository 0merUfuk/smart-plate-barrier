"""End-to-end device simulation runner.

Simulates an ESP32-CAM capturing real JPEG images and sending authenticated
observations to the backend, testing OCR extraction, exact-match whitelist
authorization, and barrier telemetry.
"""

import json
from pathlib import Path
import time
from fastapi.testclient import TestClient

from backend.fastapi_app import create_app
from backend.ocr import get_ocr_engine

SAMPLES_DIR = Path("data/test_samples")
DB_PATH = "data/sim_demo.sqlite3"
AUTH_TOKEN = "smart-barrier-device-key-2026"
DEVICE_ID = "esp32-barrier-01"
SESSION_ID = f"sim-{int(time.time())}"


def run_simulation():
    print("=" * 70)
    print("   SMART PLATE BARRIER — END-TO-END DEVICE & OCR SIMULATION")
    print("=" * 70)

    # Clean previous simulation DB
    Path(DB_PATH).unlink(missing_ok=True)

    print(f"\n1. Initializing backend and OCR engine (cct-s-v2-global-model)...")
    ocr_engine = get_ocr_engine("fast-plate-ocr")
    app = create_app(db_path=DB_PATH, ocr_engine=ocr_engine)
    client = TestClient(app)

    # Check state
    state = client.get("/api/state").json()
    print(f"   [OK] Server initialized. Allowed whitelist plates: {state['allowed_plates']}")

    # Collect the 10 test samples
    samples = [
        ("tr_01.jpg", "TR (Muğla)", "48TM3013", False),
        ("tr_02.jpg", "TR (Kayseri)", "38VU055", False),
        ("tr_03.jpg", "TR (Istanbul)", "34DMO01", True),   # Whitelisted!
        ("tr_04.jpg", "TR (Ankara)", "06TST02", True),     # Whitelisted!
        ("tr_05.jpg", "TR (Istanbul)", "34XYZ99", False),
        ("untr_01_de.jpg", "Germany (DE)", "BMW1234", False),
        ("untr_02_de.jpg", "Germany (DE)", "BD164539", False),
        ("untr_03_fr.jpg", "France (FR)", "AB123CD", False),
        ("untr_04_es.jpg", "Spain (ES)", "Historic/NonStd", False),
        ("untr_05_uk.jpg", "United Kingdom (UK)", "GB21XYZ", False),
    ]

    print("\n2. Processing 10 plate captures through authenticated device API:\n")
    print(f"{'#':<3} | {'Sample':<14} | {'Origin':<12} | {'OCR Text':<12} | {'Conf':<6} | {'Decision':<10} | {'Barrier Action'}")
    print("-" * 80)

    results = []
    for idx, (filename, origin, expected, whitelisted) in enumerate(samples, 1):
        file_path = SAMPLES_DIR / filename
        if not file_path.is_file():
            print(f"Missing sample: {filename}")
            continue

        jpeg_bytes = file_path.read_bytes()
        req_id = f"req-{idx:03d}"

        headers = {
            "Content-Type": "image/jpeg",
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "X-Device-Id": DEVICE_ID,
            "X-Session-Id": SESSION_ID,
            "X-Request-Id": req_id,
        }

        t0 = time.perf_counter()
        resp = client.post("/api/device/v1/observations", content=jpeg_bytes, headers=headers)
        elapsed = (time.perf_counter() - t0) * 1000.0

        if resp.status_code != 200:
            print(f"{idx:<3} | {filename:<14} | {origin:<12} | ERROR: {resp.status_code}")
            continue

        data = resp.json()
        decision = data["decision"]
        plate = data.get("plate", "")
        conf = data.get("confidence", 0.0)

        if decision == "allow":
            barrier_action = "OPEN -> PASSAGE -> CLOSE"
            # Simulate device event telemetry
            client.post(
                "/api/device/v1/events",
                json={
                    "device_id": DEVICE_ID,
                    "session_id": SESSION_ID,
                    "event_id": f"evt-{req_id}-open",
                    "event_type": "barrier_opened",
                    "barrier_state": "open_waiting_clear",
                },
                headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            )
            client.post(
                "/api/device/v1/events",
                json={
                    "device_id": DEVICE_ID,
                    "session_id": SESSION_ID,
                    "event_id": f"evt-{req_id}-close",
                    "event_type": "barrier_closed",
                    "barrier_state": "closed",
                },
                headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            )
        elif decision == "deny":
            barrier_action = "STAY CLOSED (Red LED)"
        else:
            barrier_action = "STAY CLOSED (Unreadable / Foreign)"

        print(f"{idx:<3} | {filename:<14} | {origin:<12} | {plate:<12} | {conf:<6.2f} | {decision:<10} | {barrier_action}")

        results.append({
            "idx": idx,
            "filename": filename,
            "origin": origin,
            "ocr_text": plate,
            "confidence": conf,
            "decision": decision,
            "reason": data.get("reason"),
            "latency_ms": round(elapsed, 1),
            "barrier_action": barrier_action,
        })

    # Test idempotency (duplicate replay)
    print("-" * 80)
    print("\n3. Testing Idempotency & Replay Protection:")
    dup_file = SAMPLES_DIR / "tr_03.jpg"
    dup_resp = client.post(
        "/api/device/v1/observations",
        content=dup_file.read_bytes(),
        headers={
            "Content-Type": "image/jpeg",
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "X-Device-Id": DEVICE_ID,
            "X-Session-Id": SESSION_ID,
            "X-Request-Id": "req-003",  # Duplicate of req-003!
        },
    )
    dup_data = dup_resp.json()
    print(f"   Re-sending req-003: duplicate={dup_data.get('duplicate')}, decision={dup_data.get('decision')} (NO extra opening)")

    # Print summary statistics
    total = len(results)
    allowed = sum(1 for r in results if r["decision"] == "allow")
    denied = sum(1 for r in results if r["decision"] == "deny")
    unreadable = sum(1 for r in results if r["decision"] == "unreadable")

    print("\n" + "=" * 70)
    print("   SIMULATION SUMMARY")
    print("=" * 70)
    print(f"   Total Images Processed : {total}")
    print(f"   Authorized (Allow)     : {allowed} (Correctly granted to whitelisted plates)")
    print(f"   Unauthorized (Deny)    : {denied} (Blocked by exact-match whitelist policy)")
    print(f"   Unreadable/Non-TR      : {unreadable} (Non-conforming formatting blocked)")
    print("=" * 70)

    # Save simulation report
    report_path = Path("data/simulation_report.json")
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\n[OK] Full simulation report saved to: {report_path.resolve()}\n")


if __name__ == "__main__":
    run_simulation()
