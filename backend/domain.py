"""Decision and virtual barrier logic, independent of HTTP and OCR libraries."""
import math
import re

PLATE = re.compile(r"(?:0[1-9]|[1-7][0-9]|8[01])[A-Z]{1,3}[0-9]{2,5}\Z")
CONFIDENCE_THRESHOLD = 0.85  # Initial proposal; not calibrated on a real dataset.


def normalize_plate(text):
    if not isinstance(text, str) or len(text) > 32:
        raise ValueError("plate must be a string of at most 32 characters")
    # Deliberately do not substitute O/0, I/1 or remove arbitrary punctuation.
    return "".join(text.upper().split())


def validate_observation(data):
    if not isinstance(data, dict):
        raise ValueError("JSON object required")
    request_id = data.get("request_id")
    if not isinstance(request_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", request_id):
        raise ValueError("request_id must contain 1-64 letters, digits, underscores or hyphens")
    plate = normalize_plate(data.get("plate", ""))
    confidence = data.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ValueError("confidence must be a finite number between 0 and 1")
    if not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError("confidence must be a finite number between 0 and 1")
    fault = data.get("fault", "none")
    if fault not in ("none", "ocr_error", "network_timeout"):
        raise ValueError("unknown fault scenario")
    return request_id, plate, float(confidence), fault


def decide(plate, confidence, fault, allowed):
    if fault != "none":
        return "error", fault
    if not PLATE.fullmatch(plate):
        return "unreadable", "invalid_plate_format"
    if confidence < CONFIDENCE_THRESHOLD:
        return "unreadable", "low_confidence"
    if plate not in allowed:
        return "deny", "not_in_allowlist"
    return "allow", "exact_match"


def barrier_transition(state, event):
    """Only a new grant may open. Only explicit clear confirmation may close."""
    if event == "grant" and state == "closed":
        return "open_waiting_clear", "open"
    if event == "clear" and state == "open_waiting_clear":
        return "closed", "close"
    return state, "none"
