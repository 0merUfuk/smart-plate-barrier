import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from .domain import barrier_transition, decide, normalize_plate, PLATE, validate_observation, CONFIDENCE_THRESHOLD

DEMO_PLATES = ("34DMO01", "06TST02")


class Conflict(Exception):
    pass


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS allowed (plate TEXT PRIMARY KEY);
                CREATE TABLE IF NOT EXISTS events (
                    request_id TEXT PRIMARY KEY, payload TEXT NOT NULL,
                    response TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                INSERT OR IGNORE INTO settings VALUES ('barrier', 'closed');
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY, action TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS device_observations (
                    device_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    image_sha256 TEXT NOT NULL,
                    raw_text TEXT NOT NULL,
                    normalized_text TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    decision TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    response_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (device_id, session_id, request_id));
                CREATE TABLE IF NOT EXISTS device_events (
                    device_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TEXT NOT NULL);
            """)
            # Seed only a brand new database. Deleted demo plates stay deleted on restart.
            if not db.execute("SELECT 1 FROM settings WHERE key='seeded'").fetchone():
                db.executemany("INSERT OR IGNORE INTO allowed VALUES (?)", [(p,) for p in DEMO_PLATES])
                db.execute("INSERT INTO settings VALUES ('seeded', 'yes')")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def snapshot(self):
        with self.connect() as db:
            events = db.execute("SELECT response FROM events ORDER BY rowid DESC LIMIT 50").fetchall()
            return {
                "mode": "simulation", "real_ocr": False, "physical_hardware": False,
                "barrier": db.execute("SELECT value FROM settings WHERE key='barrier'").fetchone()[0],
                "allowed_plates": [r[0] for r in db.execute("SELECT plate FROM allowed ORDER BY plate")],
                "events": [json.loads(r[0]) for r in events],
                "actions": [dict(r) for r in db.execute("SELECT * FROM actions ORDER BY id DESC LIMIT 20")],
            }

    def scan(self, data):
        request_id, plate, confidence, fault = validate_observation(data)
        payload = json.dumps([plate, confidence, fault], separators=(",", ":"))
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            previous = db.execute("SELECT payload,response FROM events WHERE request_id=?", (request_id,)).fetchone()
            if previous:
                if previous["payload"] != payload:
                    raise Conflict("request_id already used for a different observation")
                result = json.loads(previous["response"])
                result.update(duplicate=True, barrier_action="none")
                result["barrier"] = db.execute("SELECT value FROM settings WHERE key='barrier'").fetchone()[0]
                return result
            allowed = {r[0] for r in db.execute("SELECT plate FROM allowed")}
            decision, reason = decide(plate, confidence, fault, allowed)
            state = db.execute("SELECT value FROM settings WHERE key='barrier'").fetchone()[0]
            new_state, action = barrier_transition(state, "grant" if decision == "allow" else "no_grant")
            stamp = self.now()
            result = dict(request_id=request_id, plate=plate, confidence=confidence,
                          decision=decision, reason=reason, duplicate=False,
                          barrier=new_state, barrier_action=action, mode="simulation", created_at=stamp)
            db.execute("UPDATE settings SET value=? WHERE key='barrier'", (new_state,))
            db.execute("INSERT INTO events VALUES (?,?,?,?)", (request_id, payload, json.dumps(result), stamp))
            if action != "none":
                db.execute("INSERT INTO actions(action,created_at) VALUES (?,?)", (action, stamp))
            return result

    def clear(self):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            state = db.execute("SELECT value FROM settings WHERE key='barrier'").fetchone()[0]
            state, action = barrier_transition(state, "clear")
            db.execute("UPDATE settings SET value=? WHERE key='barrier'", (state,))
            if action != "none":
                db.execute("INSERT INTO actions(action,created_at) VALUES (?,?)", (action, self.now()))
            return dict(barrier=state, barrier_action=action, mode="simulation")

    def change_plate(self, text, add=True):
        plate = normalize_plate(text)
        if not PLATE.fullmatch(plate):
            raise ValueError("unsupported plate format")
        with self.connect() as db:
            if add:
                db.execute("INSERT OR IGNORE INTO allowed VALUES (?)", (plate,))
            else:
                db.execute("DELETE FROM allowed WHERE plate=?", (plate,))
        return {"plate": plate, "added": add}

    def record_device_observation(self, device_id, session_id, request_id, image_sha256, ocr_result):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prev = db.execute(
                "SELECT image_sha256, response_json FROM device_observations WHERE device_id=? AND session_id=? AND request_id=?",
                (device_id, session_id, request_id),
            ).fetchone()
            if prev:
                if prev["image_sha256"] != image_sha256:
                    raise Conflict("request_id already used with different image payload")
                res = json.loads(prev["response_json"])
                res["duplicate"] = True
                return res

            raw_text = getattr(ocr_result, "raw_text", "")
            norm_text = getattr(ocr_result, "normalized_text", "")
            confidence = float(getattr(ocr_result, "confidence", 0.0))
            ocr_status = getattr(ocr_result, "status", "unreadable")
            ocr_error = getattr(ocr_result, "error", None)

            if ocr_status == "error":
                decision, reason = "error", ocr_error or "ocr_error"
            elif ocr_status == "unreadable" or not norm_text:
                decision, reason = "unreadable", ocr_error or "unreadable"
            elif not PLATE.fullmatch(norm_text):
                decision, reason = "unreadable", "invalid_plate_format"
            elif confidence < CONFIDENCE_THRESHOLD:
                decision, reason = "unreadable", "low_confidence"
            else:
                allowed = {r[0] for r in db.execute("SELECT plate FROM allowed")}
                if norm_text not in allowed:
                    decision, reason = "deny", "not_in_allowlist"
                else:
                    decision, reason = "allow", "exact_match"

            stamp = self.now()
            res = {
                "protocol_version": "1.0",
                "device_id": device_id,
                "session_id": session_id,
                "request_id": request_id,
                "decision": decision,
                "reason": reason,
                "plate": norm_text,
                "confidence": confidence,
                "duplicate": False,
                "server_time": stamp,
            }

            db.execute(
                """
                INSERT INTO device_observations (
                    device_id, session_id, request_id, image_sha256,
                    raw_text, normalized_text, confidence, decision, reason,
                    response_json, created_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    device_id, session_id, request_id, image_sha256,
                    raw_text, norm_text, confidence, decision, reason,
                    json.dumps(res), stamp,
                ),
            )
            return res

    def record_device_event(self, device_id, session_id, event_id, event_type, details=None):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prev = db.execute("SELECT 1 FROM device_events WHERE event_id=?", (event_id,)).fetchone()
            if prev:
                return {"event_id": event_id, "duplicate": True}
            stamp = self.now()
            details_str = json.dumps(details or {}) if isinstance(details, dict) else str(details or "")
            db.execute(
                "INSERT INTO device_events (device_id, session_id, event_id, event_type, details, created_at) VALUES (?,?,?,?,?,?)",
                (device_id, session_id, event_id, event_type, details_str, stamp),
            )
            return {"event_id": event_id, "duplicate": False, "recorded_at": stamp}
