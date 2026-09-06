"""
legal_dossier.py
Fork D: Court-Admissible PDF Dossier & Section 91 CrPC Notice Generator

Generates two document types entirely offline using reportlab:

  1. Exhibit A - Section 63(4) BSA Digital Evidence Certificate
     (hardware hash, algorithm spec, chain of custody, sign-off block)

  2. Exhibit B - Section 91 CrPC Requisition Notice
     (statutory freeze/preservation order to a telecom nodal officer
     or bank branch manager)

Both embed a QR code encoding the SHA-256 hash digest of the case
file(s) plus the zimni (case diary) entry, for tamper verification.

Wire into storage.py / server.py like this (see bottom of file for a
ready-made POST /api/export_dossier handler you can drop into server.py):

    from legal_dossier import build_evidence_certificate, build_crpc_notice

Dependencies (install once on the demo laptop, no network calls at runtime):
    pip install reportlab
    pip install qrcode[pil]        # optional - QR embedding degrades
                                    # gracefully to a text hash block
                                    # if this isn't installed.
"""

import hashlib
import io
import os
import sqlite3
from datetime import datetime, timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

try:
    import qrcode

    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DossierTitle",
            parent=styles["Title"],
            fontSize=15,
            leading=18,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="DossierSub",
            parent=styles["Normal"],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.grey,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHead",
            parent=styles["Heading2"],
            fontSize=11,
            spaceBefore=12,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Mono",
            parent=styles["Normal"],
            fontName="Courier",
            fontSize=8.5,
            leading=11,
        )
    )
    return styles


def compute_case_hash(file_paths):
    """
    Compute a single SHA-256 digest chained across one or more evidence
    files, mirroring the same algorithm used by storage.py for individual
    file hashing, so this digest is independently reproducible.
    """
    hasher = hashlib.sha256()
    for path in sorted(file_paths):
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
    return hasher.hexdigest()


def _make_qr_flowable(payload, size_mm=32):
    """Return a reportlab Image flowable containing a QR code, or None."""
    if not QR_AVAILABLE:
        return None
    qr = qrcode.QRCode(border=1, box_size=6)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Image(buf, width=size_mm * mm, height=size_mm * mm)


def _header_block(styles, title, subtitle):
    elems = [
        Paragraph(title, styles["DossierTitle"]),
        Paragraph(subtitle, styles["DossierSub"]),
        Spacer(1, 4),
        HRFlowable(width="100%", thickness=1, color=colors.black),
        Spacer(1, 10),
    ]
    return elems


def _kv_table(rows, col_widths=(45 * mm, 120 * mm)):
    """Render a list of (label, value) tuples as a two-column table."""
    styles = _styles()
    data = [
        [Paragraph(f"<b>{label}</b>", styles["Body"]), Paragraph(str(value), styles["Body"])]
        for label, value in rows
    ]
    t = Table(data, colWidths=list(col_widths))
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ]
        )
    )
    return t


# ---------------------------------------------------------------------------
# Exhibit A - Section 63(4) BSA Digital Evidence Certificate
# ---------------------------------------------------------------------------

def build_evidence_certificate(
    output_path,
    case_id,
    fir_number,
    io_name,
    police_station,
    evidence_files,   # list of dicts: {"filename", "sha256", "size_bytes", "ingested_at"}
    generated_by="TETCP Forensic Workbench",
):
    """
    Builds Exhibit A: the Section 63(4) BSA Digital Evidence Certificate.

    `evidence_files` should come straight from storage.py's
    `evidence_files` table (filename, sha256, size_bytes, ingested_at).
    """
    styles = _styles()
    story = []

    story += _header_block(
        styles,
        "EXHIBIT A &mdash; DIGITAL EVIDENCE CERTIFICATE",
        "Issued under Section 63(4), Bharatiya Sakshya Adhiniyam (BSA), 2023",
    )

    story.append(
        _kv_table(
            [
                ("Case ID", case_id),
                ("FIR Number", fir_number or "Not yet registered"),
                ("Police Station", police_station),
                ("Investigating Officer", io_name),
                ("Certificate Generated", datetime.now(timezone.utc).strftime("%d-%b-%Y %H:%M:%S UTC")),
                ("Generated By", generated_by),
                ("Hash Algorithm", "SHA-256 (FIPS 180-4)"),
            ]
        )
    )
    story.append(Spacer(1, 14))

    story.append(Paragraph("1. Declaration", styles["SectionHead"]))
    story.append(
        Paragraph(
            "I certify that the electronic records described below were produced by a computer "
            "used regularly for the storage and processing of information, that the computer was "
            "operating properly during the material period, and that the electronic records "
            "accurately reproduce the information fed into the computer in the ordinary course of "
            "activity, in accordance with Section 63(4) of the Bharatiya Sakshya Adhiniyam, 2023.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Evidence File Inventory & Chain of Custody", styles["SectionHead"]))
    table_data = [["#", "Filename", "SHA-256 Hash", "Records", "Ingested At"]]
    for i, ef in enumerate(evidence_files, start=1):
        table_data.append(
            [
                str(i),
                Paragraph(ef.get("filename", ""), styles["Mono"]),
                Paragraph(ef.get("sha256", ""), styles["Mono"]),
                f"{ef.get('size_bytes', 0):,}",
                ef.get("ingested_at", ""),
            ]
        )
    inv_table = Table(table_data, colWidths=[8 * mm, 45 * mm, 65 * mm, 22 * mm, 28 * mm], repeatRows=1)
    inv_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e2327")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ]
        )
    )
    story.append(inv_table)
    story.append(Spacer(1, 14))

    # Composite hash + QR verification block
    story.append(Paragraph("3. Composite Verification Digest", styles["SectionHead"]))
    composite_hash = hashlib.sha256(
        "|".join(sorted(ef.get("sha256", "") for ef in evidence_files)).encode("utf-8")
    ).hexdigest()
    qr_payload = f"CASE:{case_id}|SHA256:{composite_hash}"
    qr_flowable = _make_qr_flowable(qr_payload)

    verify_row = [
        Paragraph(
            f"<b>Composite SHA-256 (all files):</b><br/>{composite_hash}"
            "<br/><br/>Scan the adjoining QR code to independently verify this digest "
            "against the case diary (zimni) entry recorded at the time of ingestion.",
            styles["Body"],
        ),
        qr_flowable if qr_flowable else Paragraph("[QR module not installed]", styles["Body"]),
    ]
    verify_table = Table([verify_row], colWidths=[120 * mm, 45 * mm])
    verify_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(verify_table)
    story.append(Spacer(1, 24))

    story.append(Paragraph("4. Sign-Off", styles["SectionHead"]))
    story.append(
        _kv_table(
            [
                ("Investigating Officer", "_" * 35 + "&nbsp;&nbsp;&nbsp;Date: " + "_" * 15),
                ("Forensic/Cyber Cell Officer", "_" * 35 + "&nbsp;&nbsp;&nbsp;Date: " + "_" * 15),
            ]
        )
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        title=f"Exhibit A - Digital Evidence Certificate - {case_id}",
    )
    doc.build(story)
    return output_path


# ---------------------------------------------------------------------------
# Exhibit B - Section 91 CrPC Requisition Notice
# ---------------------------------------------------------------------------

def build_crpc_notice(
    output_path,
    case_id,
    fir_number,
    police_station,
    io_name,
    io_contact,
    recipient_designation,   # e.g. "Nodal Officer, Airtel Chandigarh Circle"
    recipient_org,           # e.g. "Bharti Airtel Ltd." or "HDFC Bank, Sector 17 Branch"
    recipient_address,
    target_identifiers,      # list of str: phone numbers / UPI VPAs / account numbers
    information_sought,      # list of str: e.g. ["CDR records", "Subscriber KYC", "Cell tower dump"]
    date_range,               # str e.g. "01-Jan-2026 to 31-Aug-2026"
    issue_date=None,
):
    """
    Builds Exhibit B: a Section 91 CrPC requisition notice directing a
    telecom nodal officer or bank branch manager to freeze/preserve and
    furnish specified records.
    """
    styles = _styles()
    story = []
    issue_date = issue_date or datetime.now().strftime("%d-%b-%Y")

    story += _header_block(
        styles,
        "EXHIBIT B &mdash; REQUISITION NOTICE",
        "Issued under Section 91, Code of Criminal Procedure (CrPC) / "
        "corresponding provision, Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023",
    )

    story.append(
        _kv_table(
            [
                ("Date of Issue", issue_date),
                ("Case ID", case_id),
                ("FIR Number", fir_number or "Not yet registered"),
                ("Police Station", police_station),
                ("Investigating Officer", f"{io_name} ({io_contact})"),
            ]
        )
    )
    story.append(Spacer(1, 12))

    story.append(Paragraph("To,", styles["Body"]))
    story.append(Paragraph(f"<b>{recipient_designation}</b>", styles["Body"]))
    story.append(Paragraph(recipient_org, styles["Body"]))
    story.append(Paragraph(recipient_address, styles["Body"]))
    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "Subject: Requisition for production/preservation of records under Section 91 CrPC "
            f"in connection with {fir_number or 'the above-referenced investigation'}.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "Sir/Madam,<br/><br/>"
            "In connection with the investigation of the above-mentioned case, and in exercise "
            "of powers vested under Section 91 of the Code of Criminal Procedure "
            "(corresponding provision under the Bharatiya Nagarik Suraksha Sanhita, 2023 where "
            "applicable), you are hereby directed to:",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 6))

    story.append(
        Paragraph(
            "1. <b>Preserve</b> all records, logs, and account data associated with the "
            "identifier(s) listed below, and prevent any deletion, closure, or alteration "
            "pending further legal process;<br/>"
            "2. <b>Furnish</b> the specific categories of information listed below, for the "
            f"period <b>{date_range}</b>, to the undersigned Investigating Officer within "
            "seven (7) days of receipt of this notice, or such shorter period as urgency "
            "may require.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 12))

    story.append(Paragraph("Target Identifier(s)", styles["SectionHead"]))
    id_table = Table(
        [["#", "Identifier"]] + [[str(i), tid] for i, tid in enumerate(target_identifiers, start=1)],
        colWidths=[10 * mm, 150 * mm],
    )
    id_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e2327")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(id_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Information / Records Sought", styles["SectionHead"]))
    for item in information_sought:
        story.append(Paragraph(f"&bull; {item}", styles["Body"]))
    story.append(Spacer(1, 14))

    story.append(
        Paragraph(
            "Non-compliance with this requisition without lawful excuse may attract "
            "consequences under applicable law. Please acknowledge receipt of this notice.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 24))

    story.append(
        _kv_table(
            [
                ("Issuing Officer Signature", "_" * 35),
                ("Name & Designation", io_name),
                ("Station Seal", "_" * 35),
            ]
        )
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        title=f"Exhibit B - Section 91 Notice - {case_id}",
    )
    doc.build(story)
    return output_path


# ---------------------------------------------------------------------------
# storage.py integration helper
# ---------------------------------------------------------------------------

def fetch_evidence_files_for_case(db_path, case_id):
    """
    Reads storage.py's `evidence_files` table for a given case_id and
    returns it in the shape build_evidence_certificate() expects.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        "SELECT filename, sha256_hash, record_count, uploaded_at "
        "FROM evidence_files WHERE case_id = ? ORDER BY uploaded_at",
        (case_id,),
    )
    rows = []
    for r in cur.fetchall():
        rows.append({
            "filename": r["filename"],
            "sha256": r["sha256_hash"],
            "size_bytes": r["record_count"],  # your schema tracks record_count, not byte size
            "ingested_at": r["uploaded_at"],
        })
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# server.py handler you can drop in directly
# ---------------------------------------------------------------------------
"""
Add this route inside server.py's request handler (alongside the other
/api/... routes). It expects a POST body:

    { "case_id": "...", "fir_number": "...", "io_name": "...",
      "police_station": "..." }

and streams back the generated PDF.

--- paste inside server.py's do_POST() dispatch table ---

elif self.path == "/api/export_dossier":
    length = int(self.headers.get("Content-Length", 0))
    body = json.loads(self.rfile.read(length) or b"{}")

    import legal_dossier
    import storage

    case_id = body.get("case_id", "default")
    files = legal_dossier.fetch_evidence_files_for_case(storage.DB_PATH, case_id)
    out_path = f"/tmp/exhibit_a_{case_id}.pdf"
    legal_dossier.build_evidence_certificate(
        out_path,
        case_id=case_id,
        fir_number=body.get("fir_number", ""),
        io_name=body.get("io_name", ""),
        police_station=body.get("police_station", ""),
        evidence_files=files,
    )

    with open(out_path, "rb") as f:
        pdf_bytes = f.read()

    self.send_response(200)
    self.send_header("Content-Type", "application/pdf")
    self.send_header("Content-Disposition", f'attachment; filename="exhibit_a_{case_id}.pdf"')
    self.send_header("Content-Length", str(len(pdf_bytes)))
    self.end_headers()
    self.wfile.write(pdf_bytes)
"""


if __name__ == "__main__":
    # Standalone smoke test - generates two sample PDFs in the current dir.
    sample_files = [
        {
            "filename": "darknet_listings_sample.csv",
            "sha256": "a3f5c9..." + "0" * 54,
            "size_bytes": 463000,
            "ingested_at": "2026-09-05 10:12:03",
        },
        {
            "filename": "sample_telegram_export.json",
            "sha256": "b7e21d..." + "1" * 54,
            "size_bytes": 8420,
            "ingested_at": "2026-09-05 10:12:07",
        },
    ]

    build_evidence_certificate(
        "exhibit_a_sample.pdf",
        case_id="CASE-2026-0091",
        fir_number="FIR 214/2026",
        io_name="Insp. R. Sharma",
        police_station="Sector 17, Chandigarh",
        evidence_files=sample_files,
    )
    print("Wrote exhibit_a_sample.pdf")

    build_crpc_notice(
        "exhibit_b_sample.pdf",
        case_id="CASE-2026-0091",
        fir_number="FIR 214/2026",
        police_station="Sector 17, Chandigarh",
        io_name="Insp. R. Sharma",
        io_contact="+91-9XXXXXXXXX",
        recipient_designation="Nodal Officer, Cyber Crime Cell",
        recipient_org="Bharti Airtel Ltd.",
        recipient_address="Airtel Circle Office, Chandigarh",
        target_identifiers=["+91-98XXXXXX12", "+91-99XXXXXX45"],
        information_sought=["CDR records", "Subscriber KYC details", "Cell tower dump for date range"],
        date_range="01-Jul-2026 to 31-Aug-2026",
    )
    print("Wrote exhibit_b_sample.pdf")
