"""
cdr_analyser.py
Fork C: Telecom CDR, IPDR & Tower Azimuth Geo-Correlator

Parses raw CDR/IPDR CSV dumps (Airtel/Jio/Vi format), maps cell IDs to
known Chandigarh-area sectors, and cross-references suspect phone
presence against dead-drop delivery timestamps mined from Telegram /
darknet chat evidence already sitting in storage.py's `entity_mentions`
table - surfacing high-confidence "physical co-location" leads.

No external dependencies - stdlib csv + sqlite3 only, consistent with
the project's air-gap / zero-npm ground rules.
"""

import csv
import io
import sqlite3
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# 1. Cell ID -> Chandigarh sector lookup
#
#    Fill this in with your actual tower dataset (telcos will usually
#    supply a cell-ID-to-lat/long or cell-ID-to-site-name mapping
#    alongside the CDR dump, or it can be sourced from the DoT database
#    if permitted). This is a placeholder skeleton for the demo.
# ---------------------------------------------------------------------------
CELL_ID_TO_SECTOR = {
    # "cell_id": ("Sector name", latitude, longitude)
    "10234": ("Sector 17, Chandigarh", 30.7410, 76.7822),
    "10891": ("Sector 22, Chandigarh", 30.7295, 76.7684),
    "11207": ("Sector 26, Chandigarh (Grain Market)", 30.7217, 76.8064),
    "12045": ("Sector 43, Chandigarh (ISBT)", 30.7194, 76.7645),
    "13390": ("Aroma Hotel, Sector 22, Chandigarh", 30.7401, 76.7823),
    "14502": ("Mohali Phase 7", 30.7046, 76.7179),
}


def lookup_tower(cell_id):
    """Return (sector_name, lat, lon) for a cell ID, or None if unknown."""
    return CELL_ID_TO_SECTOR.get(str(cell_id).strip())


# ---------------------------------------------------------------------------
# 2. CDR CSV parsing
# ---------------------------------------------------------------------------

# Common column name variants across Indian telco CDR export formats.
COLUMN_ALIASES = {
    "calling_no": ["Calling_No", "A_PARTY", "Calling Number", "MSISDN"],
    "called_no": ["Called_No", "B_PARTY", "Called Number"],
    "date": ["Date", "Call_Date", "CALL_DATE"],
    "time": ["Time", "Call_Time", "CALL_TIME"],
    "duration": ["Duration", "Call_Duration", "DUR"],
    "first_cell_id": ["First_Cell_ID", "FIRST_CELL_ID", "Cell_ID_Start"],
    "last_cell_id": ["Last_Cell_ID", "LAST_CELL_ID", "Cell_ID_End"],
    "imei": ["IMEI", "Imei"],
    "imsi": ["IMSI", "Imsi"],
}


def _resolve_columns(fieldnames):
    """Map this file's actual column names onto our canonical field names."""
    resolved = {}
    lower_fields = {f.lower(): f for f in fieldnames}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias.lower() in lower_fields:
                resolved[canonical] = lower_fields[alias.lower()]
                break
    return resolved


def parse_cdr_csv(file_bytes, case_id):
    """
    Parse a raw CDR/IPDR CSV dump into a list of normalized call records:

        {
          "case_id", "calling_no", "called_no", "timestamp" (datetime),
          "duration_sec", "first_cell_id", "last_cell_id",
          "first_tower", "last_tower", "imei", "imsi"
        }

    Unknown/malformed rows are skipped rather than raising, since real
    telco dumps commonly have a handful of ragged rows.
    """
    text = file_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    cols = _resolve_columns(reader.fieldnames or [])

    required = {"calling_no", "date", "time"}
    if not required.issubset(cols):
        raise ValueError(
            f"CDR file missing required columns. Found headers: {reader.fieldnames}. "
            f"Resolved: {cols}. Expected at least: {required}"
        )

    records = []
    for row in reader:
        try:
            calling_no = row[cols["calling_no"]].strip()
            called_no = row.get(cols.get("called_no", ""), "").strip()
            date_str = row[cols["date"]].strip()
            time_str = row[cols["time"]].strip()
            timestamp = _parse_datetime(date_str, time_str)

            duration_raw = row.get(cols.get("duration", ""), "0")
            duration_sec = _parse_duration(duration_raw)

            first_cell_id = row.get(cols.get("first_cell_id", ""), "").strip()
            last_cell_id = row.get(cols.get("last_cell_id", ""), "").strip() or first_cell_id

            first_tower = lookup_tower(first_cell_id)
            last_tower = lookup_tower(last_cell_id)

            records.append(
                {
                    "case_id": case_id,
                    "calling_no": calling_no,
                    "called_no": called_no,
                    "timestamp": timestamp,
                    "duration_sec": duration_sec,
                    "first_cell_id": first_cell_id,
                    "last_cell_id": last_cell_id,
                    "first_tower": first_tower[0] if first_tower else None,
                    "last_tower": last_tower[0] if last_tower else None,
                    "first_lat": first_tower[1] if first_tower else None,
                    "first_lon": first_tower[2] if first_tower else None,
                    "imei": row.get(cols.get("imei", ""), "").strip(),
                    "imsi": row.get(cols.get("imsi", ""), "").strip(),
                }
            )
        except (KeyError, ValueError):
            continue  # skip malformed row

    return records


def _parse_datetime(date_str, time_str):
    for date_fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y"):
        for time_fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(f"{date_str} {time_str}", f"{date_fmt} {time_fmt}")
            except ValueError:
                continue
    raise ValueError(f"Unrecognized date/time format: {date_str} {time_str}")


def _parse_duration(raw):
    raw = str(raw).strip()
    if not raw:
        return 0
    if ":" in raw:  # HH:MM:SS or MM:SS
        parts = [int(p) for p in raw.split(":")]
        while len(parts) < 3:
            parts.insert(0, 0)
        h, m, s = parts
        return h * 3600 + m * 60 + s
    try:
        return int(float(raw))
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# 3. Geo-temporal co-location matching against chat/darknet evidence
# ---------------------------------------------------------------------------

def fetch_dead_drop_events(db_path, case_id):
    """
    Pull candidate "dead-drop" timestamps + locations from existing chat
    evidence in storage.py's schema. This assumes entity_mentions/entities
    already captured location-tagged lines; adjust the query to match
    your actual `entities` table's `entity_type` values (e.g. 'location').
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        """
        SELECT em.line_number, er.timestamp AS raw_timestamp, er.raw_text,
               e.value AS location_value
        FROM entity_mentions em
        JOIN entities e ON e.id = em.entity_id
        JOIN evidence_records er ON er.file_id = em.file_id AND er.line_number = em.line_number
        WHERE e.entity_type = 'location' AND em.case_id = ?
        """,
        (case_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def find_colocation_matches(cdr_records, dead_drop_events, window_minutes=30):
    """
    Cross-reference CDR tower presence against chat-evidence dead-drop
    events. A match is flagged when a suspect's phone was registered at
    a tower whose mapped sector name matches (substring match) a
    location mentioned in a chat line, within `window_minutes` of the
    message's timestamp.

    Returns a list of "Physical Co-Location" alert dicts, ready to drop
    straight into Panel 2 alongside the existing triage leads.
    """
    alerts = []
    window = timedelta(minutes=window_minutes)

    for event in dead_drop_events:
        event_location = (event.get("location_value") or "").lower()
        event_ts_raw = event.get("raw_timestamp")
        if not event_location or not event_ts_raw:
            continue
        try:
            event_ts = datetime.fromisoformat(event_ts_raw)
        except (ValueError, TypeError):
            continue

        for cdr in cdr_records:
            tower_name = (cdr.get("first_tower") or "").lower()
            if not tower_name:
                continue
            if event_location in tower_name or tower_name.split(",")[0] in event_location:
                if abs((cdr["timestamp"] - event_ts)) <= window:
                    alerts.append(
                        {
                            "type": "physical_colocation",
                            "confidence": "high" if abs((cdr["timestamp"] - event_ts)) <= timedelta(minutes=10) else "medium",
                            "phone": cdr["calling_no"],
                            "tower": cdr["first_tower"],
                            "cdr_timestamp": cdr["timestamp"].isoformat(),
                            "chat_line_number": event["line_number"],
                            "chat_text_excerpt": (event.get("raw_text") or "")[:120],
                            "chat_timestamp": event_ts.isoformat(),
                            "minutes_apart": round(abs((cdr["timestamp"] - event_ts)).total_seconds() / 60, 1),
                        }
                    )
    return alerts


# ---------------------------------------------------------------------------
# server.py integration - paste inside do_POST()/do_GET() dispatch
# ---------------------------------------------------------------------------
"""
elif self.path == "/api/upload_cdr":
    from urllib.parse import parse_qs, urlparse
    import storage
    from cdr_analyser import parse_cdr_csv, fetch_dead_drop_events, find_colocation_matches

    qs = parse_qs(urlparse(self.path).query)
    case_id = qs.get("case_id", ["default"])[0]

    length = int(self.headers.get("Content-Length", 0))
    file_bytes = self.rfile.read(length)

    records = parse_cdr_csv(file_bytes, case_id)
    dead_drops = fetch_dead_drop_events(storage.DB_PATH, case_id)
    alerts = find_colocation_matches(records, dead_drops)

    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps({
        "records_parsed": len(records),
        "colocation_alerts": alerts,
    }, default=str).encode())
"""


if __name__ == "__main__":
    # Smoke test with a tiny synthetic CDR CSV.
    sample_csv = (
        "Calling_No,Called_No,Date,Time,Duration,First_Cell_ID,Last_Cell_ID,IMEI,IMSI\n"
        "9812345670,9998887776,05-09-2026,14:32:10,125,11207,11207,352099001761481,404450123456789\n"
        "9812345670,9998887776,05-09-2026,18:05:00,60,10234,10234,352099001761481,404450123456789\n"
    ).encode("utf-8")

    records = parse_cdr_csv(sample_csv, case_id="CASE-2026-0091")
    for r in records:
        print(r["calling_no"], r["timestamp"], "->", r["first_tower"])
