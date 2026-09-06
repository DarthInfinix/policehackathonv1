"""
ocr_worker.py
Fork A: Offline OCR & Seized Screenshot Harvester

Turns seized screenshots (WhatsApp chats, Telegram channels, UPI payment
receipts) into a plain-text evidence stream that storage.py can ingest
through the existing pipeline - so OCR'd screenshots show up in Panel 1
exactly like any other evidence file, with full trace-to-source support.

Dependencies (install once, offline thereafter):
    pip install pytesseract pillow
    # + the tesseract binary itself:
    #   Debian/Ubuntu: sudo apt-get install tesseract-ocr
    #   macOS:         brew install tesseract

Usage from server.py's upload handler:

    from ocr_worker import process_evidence_image
    import storage

    text_content = process_evidence_image(image_bytes, case_id)
    storage.parse_and_ingest_file(case_id, filename, text_content.encode("utf-8"))
"""

import io
import re
from datetime import datetime

try:
    import pytesseract
    from PIL import Image, ImageOps, ImageFilter

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


# ---------------------------------------------------------------------------
# Regex patterns for common Indian payment-app receipt fields
# ---------------------------------------------------------------------------
RE_UPI_TXN_ID = re.compile(r"\b(?:UPI\s*(?:Ref|Txn)?\.?\s*(?:No\.?|ID)?\s*[:\-]?\s*)(\d{10,14})\b", re.I)
RE_AMOUNT = re.compile(r"(?:₹|Rs\.?|INR)\s?([\d,]+(?:\.\d{1,2})?)")
RE_PHONE = re.compile(r"(?:\+?91[\s\-]?)?[6-9]\d{9}\b")
RE_TIMESTAMP = re.compile(
    r"\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}[,\s]+\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?)\b"
)
RE_VPA = re.compile(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}")


# ---------------------------------------------------------------------------
# Pre-processing
# ---------------------------------------------------------------------------

def _preprocess(pil_image):
    """Greyscale + autocontrast + light sharpen, tuned for phone-screenshot text."""
    img = pil_image.convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img = img.filter(ImageFilter.SHARPEN)
    # Upscale small screenshots - tesseract does better above ~1000px wide.
    if img.width < 1000:
        scale = 1000 / img.width
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    return img


def _ocr_with_boxes(pil_image):
    """
    Run tesseract and return a list of (text, left, top, width, height, conf)
    tuples per detected word, using image_to_data for approximate bounding boxes.
    """
    data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
    words = []
    for i in range(len(data["text"])):
        text = data["text"][i].strip()
        if not text:
            continue
        words.append(
            {
                "text": text,
                "left": data["left"][i],
                "top": data["top"][i],
                "width": data["width"][i],
                "height": data["height"][i],
                "conf": data["conf"][i],
            }
        )
    return words


def _group_words_into_lines(words, line_tolerance_px=12):
    """
    Group OCR words into text lines using their vertical (top) position -
    screenshots are chat bubbles, so a naive top-to-bottom line grouping
    reproduces conversational order well enough for triage purposes.
    """
    if not words:
        return []
    words_sorted = sorted(words, key=lambda w: (w["top"], w["left"]))
    lines = []
    current_line = [words_sorted[0]]
    current_top = words_sorted[0]["top"]

    for w in words_sorted[1:]:
        if abs(w["top"] - current_top) <= line_tolerance_px:
            current_line.append(w)
        else:
            lines.append(current_line)
            current_line = [w]
            current_top = w["top"]
    lines.append(current_line)

    line_texts = []
    for line in lines:
        line_sorted = sorted(line, key=lambda w: w["left"])
        line_texts.append(" ".join(w["text"] for w in line_sorted))
    return line_texts


# ---------------------------------------------------------------------------
# Structured field extraction from OCR'd text
# ---------------------------------------------------------------------------

def extract_receipt_fields(text):
    """Pull UPI txn IDs, amounts, phone numbers, VPAs, and timestamps out of OCR text."""
    return {
        "upi_txn_ids": RE_UPI_TXN_ID.findall(text),
        "amounts": RE_AMOUNT.findall(text),
        "phones": list(set(RE_PHONE.findall(text))),
        "vpas": list(set(RE_VPA.findall(text))),
        "timestamps": RE_TIMESTAMP.findall(text),
    }


# ---------------------------------------------------------------------------
# Main entry point - matches the Fork A spec in the README
# ---------------------------------------------------------------------------

def process_evidence_image(image_path_or_bytes, case_id, source_label=None):
    """
    Process a single seized screenshot and return a plain-text evidence
    stream formatted so storage.parse_and_ingest_file() can consume it
    line-by-line, exactly like a chat export or CSV.

    Each output line is prefixed with an [OCR] tag and, where detected,
    inline field annotations - so downstream entity extraction in
    storage.py still finds phones/UPI handles/amounts automatically
    without needing storage.py itself to change.

    Returns: str (newline-joined text content)
    """
    if not OCR_AVAILABLE:
        raise RuntimeError(
            "OCR dependencies not installed. Run: "
            "pip install pytesseract pillow  (and install the tesseract binary)"
        )

    if isinstance(image_path_or_bytes, (bytes, bytearray)):
        pil_image = Image.open(io.BytesIO(image_path_or_bytes))
    else:
        pil_image = Image.open(image_path_or_bytes)

    processed = _preprocess(pil_image)
    words = _ocr_with_boxes(processed)
    lines = _group_words_into_lines(words)
    full_text = "\n".join(lines)
    fields = extract_receipt_fields(full_text)

    label = source_label or f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_lines = [f"# OCR SOURCE: {label} | case_id={case_id}"]

    if fields["upi_txn_ids"]:
        output_lines.append(f"# DETECTED UPI_TXN_ID: {', '.join(fields['upi_txn_ids'])}")
    if fields["amounts"]:
        output_lines.append(f"# DETECTED AMOUNT: {', '.join(fields['amounts'])}")
    if fields["phones"]:
        output_lines.append(f"# DETECTED PHONE: {', '.join(fields['phones'])}")
    if fields["vpas"]:
        output_lines.append(f"# DETECTED VPA: {', '.join(fields['vpas'])}")
    if fields["timestamps"]:
        output_lines.append(f"# DETECTED TIMESTAMP: {', '.join(fields['timestamps'])}")

    output_lines.append("---")
    output_lines.extend(f"[OCR] {line}" for line in lines)

    return "\n".join(output_lines)


def process_evidence_image_batch(images, case_id):
    """Convenience wrapper: process a list of (label, image_bytes) tuples."""
    results = {}
    for label, image_bytes in images:
        try:
            results[label] = process_evidence_image(image_bytes, case_id, source_label=label)
        except Exception as e:  # noqa: BLE001 - surface per-file failure, keep batch going
            results[label] = f"# OCR FAILED for {label}: {e}"
    return results


# ---------------------------------------------------------------------------
# server.py integration - paste inside do_POST() dispatch
# ---------------------------------------------------------------------------
"""
elif self.path.startswith("/api/upload_screenshot"):
    from urllib.parse import parse_qs, urlparse
    import storage
    from ocr_worker import process_evidence_image

    qs = parse_qs(urlparse(self.path).query)
    case_id = qs.get("case_id", ["default"])[0]
    filename = qs.get("filename", ["screenshot.png"])[0]

    length = int(self.headers.get("Content-Length", 0))
    image_bytes = self.rfile.read(length)

    text_content = process_evidence_image(image_bytes, case_id, source_label=filename)
    storage.parse_and_ingest_file(case_id, filename.rsplit(".", 1)[0] + "_ocr.txt", text_content.encode("utf-8"))

    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps({"status": "ok", "filename": filename}).encode())
"""


if __name__ == "__main__":
    if not OCR_AVAILABLE:
        print("pytesseract/PIL not installed - install with:")
        print("  pip install pytesseract pillow")
        print("  (and the tesseract-ocr system binary)")
    else:
        print("OCR worker ready. Call process_evidence_image(path_or_bytes, case_id).")
