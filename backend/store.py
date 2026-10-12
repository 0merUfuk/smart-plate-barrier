import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from .domain import barrier_transition, decide, normalize_plate, PLATE, validate_observation

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
            """)
            # Seed only a brand new database. Deleted demo plates stay deleted on restart.
            if not db.execute("SELECT 1 FROM settings WHERE key='seeded'").fetchone():
                db.executemany("INSERT OR IGNORE INTO allowed VALUES (?)", [(p,) for p in DEMO_PLATES])
                db.execute("INSERT INTO settings VALUES ('seeded', 'yes')")

    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

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
