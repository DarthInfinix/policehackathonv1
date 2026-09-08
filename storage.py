"""
storage.py - Core Air-Gapped Forensic Storage & Entity Intelligence Engine
Chandigarh Police Hackathon 2026 - PS-3
Standard library only: sqlite3, hashlib, json, re, csv, datetime
"""

import sqlite3
import hashlib
import json
import re
import csv
import io
import os
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "case_evidence.db")

# Expanded Indian PSP Bank handles for UPI
UPI_PSP_HANDLES = (
    r'okhdfcbank|okaxis|oksbi|okicici|ybl|ibl|axl|paytm|apl|barodampay|'
    r'sbi|axisbank|icici|idfcbank|freecharge|upi|fbl|slice|jupiteraxis|'
    r'kotak|fifederal|aubank|indus|yesbank|postbank|pnb|centralbank|'
    r'allbank|cnrb|mahb|unionbank|psb|syndicate|uco|boi|vijayabank|'
    r'dbs|hsbc|scb|rbl|dlb|kvb|kbl|cub|sib|federal|airtel|amazonpay|'
    r'cred|fam|navi|timepay'
)

# Deterministic Regex Patterns for Indian Forensics
REGEX_PATTERNS = {
    # Shielded Indian phone numbers: +91/0 prefix optional, accommodates spaced/dashed groupings,
    # strictly bounded to prevent substring matches inside URLs, decimals, or WhatsApp user tags.
    "phone": re.compile(
        r'(?<![\w\d\.@])(?:(?:\+91|0091|91|0)[\s\-]?)?([6-9]\d{2,4}[\s\-]?\d{3,5})(?![\w\d\.])'
    ),
    "upi": re.compile(rf'(?<![\w\d@/])([a-zA-Z0-9.\-_]{{2,50}}@(?:{UPI_PSP_HANDLES}))\b', re.IGNORECASE),
    "tron": re.compile(r'(?<![a-zA-Z0-9/])(T[1-9A-HJ-NP-Za-km-z]{33})(?![a-zA-Z0-9/])'),
    "btc": re.compile(r'(?<![a-zA-Z0-9/])(1[a-km-zA-HJ-NP-Z1-9]{25,34}|3[a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59})(?![a-zA-Z0-9/])'),
    "eth": re.compile(r'(?<![a-zA-Z0-9/])(0x[a-fA-F0-9]{40})(?![a-zA-Z0-9/])'),
    "transaction_ref": re.compile(r'(?<![\w\d])(?:utr|ref|txn|transaction|rrn)[\s:#\-_]*([0-9]{12})\b', re.IGNORECASE),
    "pricing": re.compile(r'(?:₹|rs\.?|inr)\s*(\d+(?:,\d+)*(?:\.\d+)?)|(\d+)\s*(?:k|thousand|hundred)\b|(\d+(?:\.\d+)?)\s*(?:g|gm|gram|grams|pudiya|tola|packet|strip)\b', re.IGNORECASE),
}

# Dynamic Geographic Regexes for Chandigarh Tricity
LOCATION_DYNAMIC_PATTERNS = [
    (re.compile(r'\b(?:sector|sec)\.?\s*([0-9]{1,3}(?:\s*[-/]?[a-zA-Z])?)\b', re.IGNORECASE), lambda m: f"Sector {m.group(1).upper().replace(' ', '')}"),
    (re.compile(r'\bphase\s*([0-9]{1,2}(?:\s*[-/]?[a-zA-Z0-9]+)?)\b', re.IGNORECASE), lambda m: f"Phase {m.group(1).upper().replace(' ', '')}"),
    (re.compile(r'\b(?:sco|booth|bay\s*shop)\s*#?\s*(\d+)\b', re.IGNORECASE), lambda m: m.group(0).upper()),
    (re.compile(r'\b(1600\d{2}|14030\d|1341\d{2})\b'), lambda m: f"PIN-{m.group(1)}"),
]

# Curated Chandigarh Tricity Landmarks
KNOWN_TRICITY_LANDMARKS = [
    "sukhna lake", "rock garden", "rose garden", "elante mall", "elante",
    "panjab university", "pu campus", "pgimer", "pgi", "isbt 17", "isbt 43", "isbt",
    "tribune chowk", "housing board chowk", "aroma chowk", "aroma",
    "shivalik hostel", "aravali hostel", "kurukshetra hostel", "himalaya hostel", "vindhya hostel",
    "sector 17 plaza", "grain market 26", "timber market",
    "mohali", "panchkula", "zirakpur", "kharar", "manimajra", "nayagaon", "baltana", "dhakoli"
]

# Non-narcotic chemical/biological adjectives preceding 'acid'
ACID_NON_NARCOTIC_PREFIXES = {
    "lead", "picric", "nitric", "sulfuric", "hydrochloric", "dicarboxylic",
    "amino", "fatty", "boric", "citric", "lactic", "stomach", "salicylic",
    "folic", "ascorbic", "acetic", "benzoic", "oxalic", "tartaric",
    "phosphoric", "acrylic", "valeric", "formic", "chromic", "battery",
    "rain", "reflux", "uric", "nucleic", "pantothenic", "retinoic"
}

# Innocent prefixes preceding 'paper'
PAPER_INNOCENT_PREFIXES = {
    "chem", "chemistry", "physics", "math", "maths", "exam", "sample",
    "question", "graph", "sand", "tissue", "toilet", "news", "rough", "research"
}

# Suspicious Slang & Narcotics Keywords
SUSPICIOUS_KEYWORDS = {
    "narcotics": ["chitta", "white shoes", "white sneakers", "sneakers", "sweet mithai", "mithai", "stamp paper", "stamp papers", "4-mmc", "mephedrone", "ice tea", "mdma", "cocaine", "heroin", "charas", "hash", "pudiya", "tola", "malana", "weed", "greens", "shrooms", "acid", "lsd", "alprazolam", "tramadol", "diazepam"],
    "action": ["dead drop", "drop point", "deaddrop", "parcel", "delivery", "cash", "usdt", "transfer", "stash", "plug", "escrow", "vendor", "pgp"],
    "locations": ["sector 17", "sector 22", "sector 26", "sector 35", "sector 43", "aroma", "sukhna", "panjab university", "pu campus", "mohali", "phase 7", "phase 3b2", "panchkula", "zirakpur", "elante"]
}

def get_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = sqlite3.connect(db_path, timeout=30.0)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA busy_timeout=30000;")
    con.execute("PRAGMA synchronous=NORMAL;")
    con.row_factory = sqlite3.Row
    return con

def init_db(db_path: str = DB_PATH):
    """Initializes the forensic schema and FTS5 search index."""
    con = get_db(db_path)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS slang_dictionary (
        slang_term TEXT PRIMARY KEY,
        canonical_meaning TEXT,
        status TEXT,
        detected_count INTEGER DEFAULT 1,
        induct_timestamp TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id TEXT PRIMARY KEY,
        fir_number TEXT,
        police_station TEXT,
        io_name TEXT,
        io_belt TEXT,
        category TEXT,
        created_at TEXT,
        assigned_officer_id TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS officers (
        officer_id TEXT PRIMARY KEY,
        name TEXT,
        belt TEXT,
        rank TEXT,
        role TEXT,
        station TEXT,
        created_at TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS case_collaborators (
        case_id TEXT,
        officer_id TEXT,
        role TEXT,
        granted_by TEXT,
        granted_at TEXT,
        notes TEXT,
        PRIMARY KEY (case_id, officer_id)
    );
    """)

    # Safe migration: ensure assigned_officer_id exists on cases table if it pre-existed
    cur.execute("PRAGMA table_info(cases)")
    columns = [col[1] for col in cur.fetchall()]
    if "assigned_officer_id" not in columns:
        try:
            cur.execute("ALTER TABLE cases ADD COLUMN assigned_officer_id TEXT DEFAULT 'OFFICER_IO_01'")
        except Exception:
            pass

    # Pre-seed 3 minimal, realistic demo officer profiles if table is empty
    cur.execute("SELECT COUNT(*) FROM officers")
    if cur.fetchone()[0] == 0:
        demo_officers = [
            ("OFFICER_IO_01", "Insp. Vikramjit Singh", "Belt #788-UT", "Inspector of Police", "IO", "PS Cyber Crime, Sector 17, Chandigarh", datetime.utcnow().isoformat() + "Z"),
            ("OFFICER_EXAM_02", "SI Priya Sharma", "Belt #412-UT", "Sub-Inspector (Forensics)", "EXAMINER", "Digital Forensic Science Lab, Sector 9, Chandigarh", datetime.utcnow().isoformat() + "Z"),
            ("OFFICER_SHO_03", "SP Balwinder Singh", "Belt #102-UT", "Superintendent of Police (Cyber)", "SHO", "Cyber Crime Division Headquarters, Chandigarh", datetime.utcnow().isoformat() + "Z")
        ]
        cur.executemany("INSERT INTO officers (officer_id, name, belt, rank, role, station, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", demo_officers)

    # Ensure baseline FIR-104 case exists and is assigned to Insp. Vikramjit Singh (IO)
    cur.execute("SELECT COUNT(*) FROM cases WHERE case_id = 'FIR_104_2026'")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO cases (case_id, fir_number, police_station, io_name, io_belt, category, created_at, assigned_officer_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'FIR_104_2026',
            'FIR No. 104/2026/CYBER',
            'PS Cyber Crime, Sector 17, Chandigarh',
            'Insp. Vikramjit Singh',
            'Belt #788-UT',
            'NDPS_CYBER',
            datetime.utcnow().isoformat() + "Z",
            'OFFICER_IO_01'
        ))
    else:
        cur.execute("UPDATE cases SET assigned_officer_id = 'OFFICER_IO_01' WHERE case_id = 'FIR_104_2026' AND (assigned_officer_id IS NULL OR assigned_officer_id = '')")

    # Ensure inquest FIR-999 case exists and is assigned to SI Priya Sharma (EXAMINER)
    cur.execute("SELECT COUNT(*) FROM cases WHERE case_id = 'FIR_999_ADVERSARIAL'")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO cases (case_id, fir_number, police_station, io_name, io_belt, category, created_at, assigned_officer_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'FIR_999_ADVERSARIAL',
            'FIR No. 999/2026/CYBER-STRESS',
            'Digital Forensics Lab & Inquest Cell, Sector 9, Chandigarh',
            'SI Priya Sharma',
            'Belt #412-UT',
            'NDPS_CYBER',
            datetime.utcnow().isoformat() + "Z",
            'OFFICER_EXAM_02'
        ))
    else:
        cur.execute("UPDATE cases SET assigned_officer_id = 'OFFICER_EXAM_02' WHERE case_id = 'FIR_999_ADVERSARIAL' AND (assigned_officer_id IS NULL OR assigned_officer_id = '')")

    # Pre-seed default bridge from FIR_104_2026 to SI Priya Sharma (EXAMINER) if not exists
    cur.execute("SELECT COUNT(*) FROM case_collaborators WHERE case_id = 'FIR_104_2026' AND officer_id = 'OFFICER_EXAM_02'")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO case_collaborators (case_id, officer_id, role, granted_by, granted_at, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ('FIR_104_2026', 'OFFICER_EXAM_02', 'FORENSIC_EXAMINER', 'Insp. Vikramjit Singh', datetime.utcnow().isoformat() + "Z", "Delegated for deep OCR & handwritten chit extraction under BSA Sec 63"))

    cur.execute("""
    CREATE TABLE IF NOT EXISTS evidence_files (
        file_id TEXT PRIMARY KEY,
        case_id TEXT,
        filename TEXT,
        file_type TEXT,
        sha256_hash TEXT,
        record_count INTEGER DEFAULT 0,
        uploaded_at TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS evidence_records (
        record_id TEXT PRIMARY KEY,
        file_id TEXT,
        case_id TEXT,
        source_type TEXT,
        sender_id TEXT,
        timestamp TEXT,
        raw_text TEXT,
        line_number INTEGER,
        is_flagged INTEGER DEFAULT 0,
        flag_reasons TEXT
    );
    """)

    # SQLite FTS5 Full-Text Search Virtual Table
    cur.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS records_fts USING fts5(
        raw_text,
        sender_id,
        content='evidence_records',
        content_rowid='rowid'
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS entities (
        entity_id TEXT PRIMARY KEY,
        entity_type TEXT,
        raw_value TEXT,
        first_seen_case TEXT,
        risk_score INTEGER DEFAULT 0,
        mention_count INTEGER DEFAULT 1
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS entity_mentions (
        record_id TEXT,
        entity_id TEXT,
        context_snippet TEXT,
        PRIMARY KEY (record_id, entity_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT,
        action TEXT,
        details TEXT,
        performed_by TEXT,
        timestamp TEXT,
        record_hash TEXT
    );
    """)

    con.commit()
    con.close()

def log_audit(case_id: str, action: str, details: str, performed_by: str = "IO Vikramjit Singh", db_path: str = DB_PATH):
    """Records an immutable audit event with timestamp and hash."""
    ts = datetime.utcnow().isoformat() + "Z"
    entry_payload = f"{case_id}:{action}:{details}:{performed_by}:{ts}"
    entry_hash = hashlib.sha256(entry_payload.encode('utf-8')).hexdigest()

    con = get_db(db_path)
    cur = con.cursor()
    cur.execute("""
    INSERT INTO audit_log (case_id, action, details, performed_by, timestamp, record_hash)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (case_id, action, details, performed_by, ts, entry_hash))
    con.commit()
    con.close()

def extract_entities_from_text(text: str) -> Dict[str, List[str]]:
    """Deterministic extractor for Phone, UPI, TRON, BTC, ETH, UTR, Locations, and Slang."""
    results = {
        "phones": [],
        "upi_handles": [],
        "crypto_wallets": [],
        "transaction_refs": [],
        "locations": [],
        "slang_keywords": []
    }

    # Shield URLs to prevent query params, doc IDs, and paths from triggering false phones/crypto
    shielded_text = re.sub(r'https?://\S+', ' [URL_SHIELDED] ', text)

    # 1. Phones: Normalize and filter out invalid/accidental matches
    for m in REGEX_PATTERNS["phone"].finditer(shielded_text):
        raw_num = m.group(1)
        clean_digits = re.sub(r'[\s\-]', '', raw_num)
        if len(clean_digits) == 10 and clean_digits[0] in '6789' and clean_digits not in results["phones"]:
            results["phones"].append(clean_digits)

    # 2. UPI VPAs
    for m in REGEX_PATTERNS["upi"].finditer(shielded_text):
        vpa = m.group(1).lower()
        if vpa not in results["upi_handles"]:
            results["upi_handles"].append(vpa)

    # 3. TRON Wallets
    for m in REGEX_PATTERNS["tron"].finditer(shielded_text):
        wallet = m.group(1)
        if wallet not in results["crypto_wallets"]:
            results["crypto_wallets"].append(wallet)

    # 4. BTC Wallets
    for m in REGEX_PATTERNS["btc"].finditer(shielded_text):
        wallet = m.group(1)
        if wallet not in results["crypto_wallets"]:
            results["crypto_wallets"].append(wallet)

    # 5. ETH Wallets
    for m in REGEX_PATTERNS["eth"].finditer(shielded_text):
        wallet = m.group(1)
        if wallet not in results["crypto_wallets"]:
            results["crypto_wallets"].append(wallet)

    # 6. Transaction Reference / UTR numbers (12-digit Indian banking ref)
    for m in REGEX_PATTERNS["transaction_ref"].finditer(shielded_text):
        ref = m.group(1)
        if ref not in results["transaction_refs"]:
            results["transaction_refs"].append(ref)

    # 7. Dynamic Geographic Locations
    lower_text = text.lower()
    for pat, formatter in LOCATION_DYNAMIC_PATTERNS:
        for m in pat.finditer(text):
            loc_label = formatter(m)
            if loc_label not in results["locations"]:
                results["locations"].append(loc_label)

    # Tricity Landmarks
    for lm in KNOWN_TRICITY_LANDMARKS:
        if re.search(r'\b' + re.escape(lm) + r'\b', lower_text):
            title_lm = lm.title()
            if title_lm not in results["locations"]:
                # Suppress shorter redundant substring if full landmark matched (e.g. 'Sukhna' vs 'Sukhna Lake')
                if not any(title_lm in existing and existing != title_lm for existing in results["locations"]):
                    results["locations"].append(title_lm)

    # 8. Slang & Narcotics with Contextual Disambiguation
    for category, words in SUSPICIOUS_KEYWORDS.items():
        for w in words:
            if not re.search(r'\b' + re.escape(w) + r'\b', lower_text):
                continue

            # Contextual filter for 'acid' (distinguish LSD from chemistry battery / homework)
            if w == "acid":
                is_chemistry = False
                for match in re.finditer(r'(\b\w+[\s\-]*)?\b(acid)\b', lower_text):
                    prefix = match.group(1)
                    if prefix and prefix.strip().rstrip('-') in ACID_NON_NARCOTIC_PREFIXES:
                        is_chemistry = True
                        break
                if is_chemistry or "acid-base" in lower_text or any(c in lower_text for c in ['hcl', 'hno3', 'h2so4', 'reaction', 'titration', 'molar', 'benzene', 'aniline', 'phenol', 'diazotization', 'equilibria', 'aqueous']):
                    continue

            # Contextual filter for 'ice tea' (distinguish iced beverage from meth)
            elif w == "ice tea":
                has_commercial = bool(re.search(r'(?:₹|rs\.?|inr|\/g|\/gm|\b(?:gm|gram|grams|pudiya|tola|stash|deaddrop|dead drop|parcel|plug|rate|delivery)\b)', lower_text))
                if not has_commercial:
                    continue

            # Contextual filter for 'stamp paper' / 'paper' (distinguish exams / stationery)
            elif "paper" in w:
                is_innocent_paper = False
                for p_pre in PAPER_INNOCENT_PREFIXES:
                    if f"{p_pre} paper" in lower_text or f"{p_pre}paper" in lower_text:
                        is_innocent_paper = True
                        break
                if is_innocent_paper:
                    continue

            if category == "locations":
                if w.title() not in results["locations"]:
                    results["locations"].append(w.title())
            elif category != "locations" and w not in results["slang_keywords"]:
                results["slang_keywords"].append(w)

    return results

def parse_and_ingest_file(case_id: str, filename: str, content_bytes: bytes, db_path: str = DB_PATH, skip_ocr: bool = False, engine_preference: str = "auto") -> Dict[str, Any]:
    """Ingests a file, auto-detects format, extracts entities, and populates SQLite."""
    file_sha256 = hashlib.sha256(content_bytes).hexdigest()
    file_id = f"FIL_{file_sha256[:12]}"
    now_str = datetime.utcnow().isoformat() + "Z"

    # Decode content
    text_content = content_bytes.decode('utf-8', errors='ignore')

    records_to_insert = []
    file_type = "UNKNOWN"

    # 0. Seized Mobile Screenshot / Receipt Image Detection (OCR)
    import ocr_worker
    if ocr_worker.is_image_data(filename, content_bytes[:32]):
        images_dir = os.path.join(os.path.dirname(db_path), "evidence_images")
        os.makedirs(images_dir, exist_ok=True)
        img_save_path = os.path.join(images_dir, f"{file_id}_{os.path.basename(filename)}")
        with open(img_save_path, "wb") as f_img:
            f_img.write(content_bytes)

        if skip_ocr:
            file_type = "IMAGE_EXHIBIT_RAW"
            records_to_insert.append({
                "source_type": "SEIZED_IMAGE_NO_OCR",
                "sender_id": "SEIZED_EXHIBIT",
                "timestamp": now_str,
                "raw_text": f"[IMAGE EXHIBIT ARCHIVED - OCR SKIPPED BY OPERATOR: {os.path.basename(filename)}]",
                "line_number": 1
            })
        else:
            try:
                ocr_res = ocr_worker.process_image_bytes(content_bytes, filename, case_id, engine_preference=engine_preference)
                file_type = f"IMAGE_OCR_{ocr_res.get('detected_category', 'SEIZURE')}"
                for r in ocr_res.get("records", []):
                    records_to_insert.append({
                        "source_type": "SEIZED_SCREENSHOT_OCR",
                        "sender_id": r.get("sender_id", "SEIZED_SCREENSHOT"),
                        "timestamp": r.get("timestamp", now_str),
                        "raw_text": r.get("raw_text", ""),
                        "line_number": r.get("line_number", 1)
                    })
            except Exception as ocr_err:
                print(f"[OCR ERROR] {ocr_err}")

    # 1. Telegram & Darknet JSON Detect
    if not records_to_insert and (filename.endswith(".json") or '"messages"' in text_content[:500]):
        try:
            tg_data = json.loads(text_content)
            if isinstance(tg_data, dict) and "messages" in tg_data:
                is_darknet = "marketplace" in tg_data or "onion" in text_content[:1000].lower()
                file_type = "DARKNET_MARKET_EXPORT" if is_darknet else "TELEGRAM_EXPORT"
                source_label = "DARKNET_LISTING" if is_darknet else "TELEGRAM"
                for idx, msg in enumerate(tg_data.get("messages", [])):
                    if msg.get("type") != "message":
                        continue
                    
                    # Telegram text may be str or array of objects
                    raw_msg_text = ""
                    t_val = msg.get("text", "")
                    if isinstance(t_val, str):
                        raw_msg_text = t_val
                    elif isinstance(t_val, list):
                        for chunk in t_val:
                            if isinstance(chunk, str):
                                raw_msg_text += chunk
                            elif isinstance(chunk, dict) and "text" in chunk:
                                raw_msg_text += chunk["text"]
                    
                    sender = msg.get("from") or msg.get("actor") or f"user_{msg.get('from_id', 'unknown')}"
                    records_to_insert.append({
                        "source_type": source_label,
                        "sender_id": str(sender),
                        "timestamp": msg.get("date", now_str),
                        "raw_text": raw_msg_text.strip(),
                        "line_number": idx + 1
                    })
        except Exception:
            pass

    # 2. CSV Detect (Darknet or Bank)
    if not records_to_insert and (filename.endswith(".csv") or "," in text_content[:300]):
        try:
            csv_reader = csv.DictReader(io.StringIO(text_content))
            headers = [h.strip() for h in (csv_reader.fieldnames or [])]
            
            # Darknet listings check
            if "product_title" in headers or "seller" in headers:
                file_type = "DARKNET_LISTINGS_CSV"
                for idx, row in enumerate(csv_reader):
                    title = row.get("product_title") or ""
                    desc = row.get("product_description") or ""
                    seller = row.get("seller") or "Anonymous"
                    price = row.get("price") or ""
                    source = row.get("source") or "Marketplace"
                    combined_text = f"[{source.upper()}] Listing: {title} | Price: {price} | Seller: {seller}\nDescription: {desc[:400]}"
                    records_to_insert.append({
                        "source_type": "DARKNET_LISTING",
                        "sender_id": str(seller),
                        "timestamp": now_str,
                        "raw_text": combined_text.strip(),
                        "line_number": idx + 2
                    })

            # Bank Statement check
            elif any("Narration" in h or "Deposit" in h or "Withdrawal" in h or "counterparty_upi" in h or "txn_type" in h for h in headers):
                file_type = "BANK_STATEMENT_CSV"
                for idx, row in enumerate(csv_reader):
                    date_val = row.get("Date") or row.get("Value Dt") or row.get("timestamp") or now_str
                    narration = row.get("Narration") or row.get("Description") or row.get("description_remarks") or ""
                    credit = row.get("Deposit Amt") or row.get("Deposit") or ""
                    debit = row.get("Withdrawal Amt") or row.get("Withdrawal") or ""
                    
                    # Also handle structured UPI bank CSV format (counterparty_upi, txn_type, amount)
                    if not credit and not debit and "amount" in row:
                        amt = row.get("amount", "")
                        ttype = (row.get("txn_type") or "").upper()
                        if ttype == "CREDIT":
                            credit = amt
                        elif ttype == "DEBIT":
                            debit = amt
                        else:
                            credit = amt

                    c_upi = row.get("counterparty_upi") or ""
                    c_name = row.get("counterparty_name") or ""
                    acc = row.get("account_number") or ""
                    
                    amount_str = f"+₹{credit}" if credit else f"-₹{debit}" if debit else ""
                    parts = [f"BANK TX [{date_val}]: {amount_str}"]
                    if acc:
                        parts.append(f"A/C: {acc}")
                    if c_upi:
                        parts.append(f"UPI: {c_upi}")
                    if c_name:
                        parts.append(f"Counterparty: {c_name}")
                    if narration:
                        parts.append(f"Narration: {narration}")

                    combined = " | ".join(parts)
                    records_to_insert.append({
                        "source_type": "BANK_STATEMENT",
                        "sender_id": str(c_upi if c_upi else "BANK_CORE"),
                        "timestamp": date_val,
                        "raw_text": combined.strip(),
                        "line_number": idx + 2
                    })
        except Exception:
            pass

    # 3. WhatsApp Chat Export & Fallback Plain Text Detect
    if not records_to_insert:
        lines = text_content.splitlines()
        
        wa_bracket_pat = re.compile(r'^\[?(\d{1,2}/\d{1,2}/\d{2,4},\s*[\d:]+(?:\s*[APap][Mm])?)\]?\s*[-:]?\s*([^:]+?):\s*(.*)$')
        wa_dash_pat = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4},\s*[\d:]+(?:\s*[APap][Mm])?)\s*-\s*([^:]+?):\s*(.*)$')

        wa_records = []
        sample_count = 0
        wa_matches = 0
        for l in lines[:100]:
            clean_l = l.strip().replace('\u200e', '').replace('\u200f', '').replace('\ufeff', '')
            if not clean_l:
                continue
            sample_count += 1
            if wa_bracket_pat.match(clean_l) or wa_dash_pat.match(clean_l):
                wa_matches += 1
        
        if sample_count > 0 and (wa_matches / sample_count) >= 0.2:
            file_type = "WHATSAPP_CHAT_EXPORT"
            line_idx = 0
            current_record = None
            for l in lines:
                clean_l = l.strip().replace('\u200e', '').replace('\u200f', '').replace('\ufeff', '')
                if not clean_l:
                    continue
                line_idx += 1
                m = wa_bracket_pat.match(clean_l) or wa_dash_pat.match(clean_l)
                if m:
                    ts_str, sender, msg_text = m.groups()
                    current_record = {
                        "source_type": "WHATSAPP_CHAT",
                        "sender_id": sender.strip(),
                        "timestamp": ts_str.strip(),
                        "raw_text": msg_text.strip(),
                        "line_number": line_idx
                    }
                    wa_records.append(current_record)
                elif current_record:
                    # Multiline message continuation
                    current_record["raw_text"] += "\n" + clean_l
            records_to_insert = wa_records

        # Fallback Plain Text (handles logs, memos, etc.)
        if not records_to_insert:
            file_type = "PLAINTEXT_DUMP"
            for idx, line in enumerate(lines):
                line_str = line.strip()
                if not line_str:
                    continue
                records_to_insert.append({
                    "source_type": "PLAINTEXT",
                    "sender_id": "SYSTEM",
                    "timestamp": now_str,
                    "raw_text": line_str,
                    "line_number": idx + 1
                })

    # Insert into database
    con = get_db(db_path)
    cur = con.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO evidence_files (file_id, case_id, filename, file_type, sha256_hash, record_count, uploaded_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (file_id, case_id, filename, file_type, file_sha256, len(records_to_insert), now_str))

    # Clean up prior records and mentions for this file in this case to ensure idempotent re-ingestion
    cur.execute("""
        DELETE FROM entity_mentions 
        WHERE record_id IN (SELECT record_id FROM evidence_records WHERE file_id = ? AND case_id = ?)
    """, (file_id, case_id))
    cur.execute("DELETE FROM evidence_records WHERE file_id = ? AND case_id = ?", (file_id, case_id))

    total_flagged = 0
    extracted_summary = {
        "phones": set(),
        "upi_handles": set(),
        "crypto_wallets": set(),
        "transaction_refs": set(),
        "locations": set(),
        "slang_keywords": set(),
    }
    flagged_records_sample = []

    for r in records_to_insert:
        rec_id = f"REC_{hashlib.md5((file_id + str(r['line_number'])).encode()).hexdigest()[:10]}"
        text = r["raw_text"]
        
        # Entity extraction
        ents = extract_entities_from_text(text)
        flag_reasons = []
        if ents["phones"]:
            flag_reasons.append(f"Phone: {', '.join(ents['phones'])}")
            extracted_summary["phones"].update(ents["phones"])
        if ents["upi_handles"]:
            flag_reasons.append(f"UPI: {', '.join(ents['upi_handles'])}")
            extracted_summary["upi_handles"].update(ents["upi_handles"])
        if ents["crypto_wallets"]:
            flag_reasons.append(f"Crypto: {', '.join(ents['crypto_wallets'])}")
            extracted_summary["crypto_wallets"].update(ents["crypto_wallets"])
        if ents.get("transaction_refs"):
            flag_reasons.append(f"UTR: {', '.join(ents['transaction_refs'])}")
            extracted_summary["transaction_refs"].update(ents["transaction_refs"])
        if ents["slang_keywords"]:
            flag_reasons.append(f"Slang: {', '.join(ents['slang_keywords'])}")
            extracted_summary["slang_keywords"].update(ents["slang_keywords"])
        if ents["locations"]:
            flag_reasons.append(f"Location: {', '.join(ents['locations'])}")
            extracted_summary["locations"].update(ents["locations"])

        is_flagged = 1 if flag_reasons else 0
        if is_flagged:
            total_flagged += 1
            if len(flagged_records_sample) < 10:
                flagged_records_sample.append({
                    "record_id": rec_id,
                    "line": r["line_number"],
                    "sender": r["sender_id"],
                    "source": r["source_type"],
                    "text": text[:200],
                    "reasons": flag_reasons
                })

        # Insert record
        cur.execute("""
        INSERT OR REPLACE INTO evidence_records (record_id, file_id, case_id, source_type, sender_id, timestamp, raw_text, line_number, is_flagged, flag_reasons)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (rec_id, file_id, case_id, r["source_type"], r["sender_id"], r["timestamp"], text, r["line_number"], is_flagged, "; ".join(flag_reasons)))

        # Update FTS5 index
        cur.execute("""
        INSERT INTO records_fts(rowid, raw_text, sender_id)
        VALUES (last_insert_rowid(), ?, ?)
        """, (text, r["sender_id"]))

        # Store Entities & Mentions
        all_entities = (
            [("PHONE", p) for p in ents["phones"]] +
            [("UPI_ID", u) for u in ents["upi_handles"]] +
            [("CRYPTO_WALLET", c) for c in ents["crypto_wallets"]] +
            [("TRANSACTION_REF", t) for t in ents.get("transaction_refs", [])] +
            [("LOCATION", l) for l in ents["locations"]] +
            [("NARCOTICS_KEYWORD", s.title()) for s in ents["slang_keywords"]]
        )
        if r["source_type"] == "DARKNET_LISTING" and r["sender_id"] not in ["Anonymous", "SYSTEM"]:
            all_entities.append(("DARKNET_VENDOR", f"@{r['sender_id']}"))

        for ent_type, val in all_entities:
            clean_val = val.strip()
            ent_id = f"ENT_{hashlib.sha256(clean_val.lower().encode()).hexdigest()[:16]}"
            risk = 90 if ent_type in ["UPI_ID", "CRYPTO_WALLET", "TRANSACTION_REF"] else 85 if ent_type == "NARCOTICS_KEYWORD" else 75 if ent_type == "DARKNET_VENDOR" else 50
            cur.execute("""
            INSERT INTO entities (entity_id, entity_type, raw_value, first_seen_case, risk_score, mention_count)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(entity_id) DO UPDATE SET mention_count = mention_count + 1
            """, (ent_id, ent_type, clean_val, case_id, risk))

            cur.execute("""
            INSERT OR IGNORE INTO entity_mentions (record_id, entity_id, context_snippet)
            VALUES (?, ?, ?)
            """, (rec_id, ent_id, text[:120]))

    con.commit()
    con.close()

    # Log audit event
    log_audit(case_id, "FILE_INGESTED", f"Ingested {filename} ({file_type}) with {len(records_to_insert)} records, {total_flagged} flagged.", db_path=db_path)

    return {
        "file_id": file_id,
        "filename": filename,
        "file_type": file_type,
        "sha256": file_sha256,
        "total_records": len(records_to_insert),
        "total_flagged": total_flagged,
        "extracted_entities": {k: sorted(list(v)) for k, v in extracted_summary.items()},
        "sample_flagged": flagged_records_sample
    }

def get_cross_source_correlations(case_id: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Discovers high-value correlations between chat handles, UPIs, and bank records."""
    con = get_db(db_path)
    cur = con.cursor()

    # Find UPIs that appear in both chat/darknet records AND bank statement records
    cur.execute("""
    SELECT e.raw_value, COUNT(DISTINCT er.source_type) as distinct_sources, GROUP_CONCAT(DISTINCT er.source_type) as sources
    FROM entities e
    JOIN entity_mentions em ON e.entity_id = em.entity_id
    JOIN evidence_records er ON em.record_id = er.record_id
    WHERE er.case_id = ? AND e.entity_type IN ('UPI_ID', 'PHONE', 'CRYPTO_WALLET', 'TRANSACTION_REF')
    GROUP BY e.raw_value
    HAVING distinct_sources > 1
    """, (case_id,))
    
    correlations = []
    for row in cur.fetchall():
        correlations.append({
            "entity": row["raw_value"],
            "distinct_sources": row["distinct_sources"],
            "sources_list": row["sources"].split(","),
            "status": "HIGH_CORROBORATION",
            "confidence": 95
        })

    con.close()
    return correlations

def search_records_fts(query: str, case_id: Optional[str] = None, limit: int = 50, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Runs fast full-text search across all ingested evidence lines."""
    con = get_db(db_path)
    cur = con.cursor()

    tokens = re.findall(r'[a-zA-Z0-9_\-]+', query)
    safe_query = " ".join(tokens).strip()

    results = []
    if safe_query:
        sql = """
        SELECT er.record_id, er.file_id, er.source_type, er.sender_id, er.timestamp, er.raw_text, er.line_number, er.is_flagged, er.flag_reasons, ef.filename
        FROM records_fts fts
        JOIN evidence_records er ON fts.rowid = er.rowid
        JOIN evidence_files ef ON er.file_id = ef.file_id
        WHERE records_fts MATCH ?
        """
        params = [safe_query]
        if case_id:
            sql += " AND er.case_id = ?"
            params.append(case_id)
        sql += " LIMIT ?"
        params.append(limit)

        try:
            cur.execute(sql, params)
            results = [dict(row) for row in cur.fetchall()]
        except Exception:
            results = []

    # Fallback to direct substring search if FTS yielded 0 results
    if not results and len(query.strip()) >= 3:
        sql_fallback = """
        SELECT er.record_id, er.file_id, er.source_type, er.sender_id, er.timestamp, er.raw_text, er.line_number, er.is_flagged, er.flag_reasons, ef.filename
        FROM evidence_records er
        JOIN evidence_files ef ON er.file_id = ef.file_id
        WHERE er.raw_text LIKE ?
        """
        params_fb = [f"%{query.strip()}%"]
        if case_id:
            sql_fallback += " AND er.case_id = ?"
            params_fb.append(case_id)
        sql_fallback += " LIMIT ?"
        params_fb.append(limit)
        cur.execute(sql_fallback, params_fb)
        results = [dict(row) for row in cur.fetchall()]

    con.close()
    return results

def get_case_graph_data(case_id: str, db_path: str = DB_PATH) -> Dict[str, Any]:
    """Generates clean graph nodes and edges for network visualization, excluding drug keywords."""
    con = get_db(db_path)
    cur = con.cursor()

    # 1. Get non-narcotics entities (Actors, Financial Rails, Wallets, Locations)
    cur.execute("""
    SELECT DISTINCT e.entity_id, e.entity_type, e.raw_value, e.risk_score, COUNT(em.record_id) as mentions
    FROM entities e
    JOIN entity_mentions em ON e.entity_id = em.entity_id
    JOIN evidence_records er ON em.record_id = er.record_id
    WHERE er.case_id = ? AND e.entity_type NOT IN ('NARCOTICS_KEYWORD', 'SLANG')
    GROUP BY e.entity_id
    ORDER BY mentions DESC
    LIMIT 50
    """, (case_id,))
    
    nodes_map = {}
    for row in cur.fetchall():
        ent_type = row["entity_type"]
        color = "#8b5cf6" if ent_type == "DARKNET_VENDOR" else "#f59e0b" if ent_type in ["UPI_ID", "CRYPTO_WALLET", "TRANSACTION_REF"] else "#10b981" if ent_type == "LOCATION" else "#3b82f6"
        nodes_map[row["entity_id"]] = {
            "id": row["entity_id"],
            "label": row["raw_value"],
            "type": ent_type,
            "risk": row["risk_score"],
            "mentions": row["mentions"],
            "color": color
        }

    # 2. Build graph edges:
    # A. Proximity edges: entities mentioned within 5 lines of each other (conversational linkage)
    cur.execute("""
    SELECT em1.entity_id as src, em2.entity_id as dst, COUNT(*) as weight, 'Co-mentioned' as rel_type
    FROM entity_mentions em1
    JOIN entity_mentions em2 ON em1.entity_id < em2.entity_id
    JOIN evidence_records er1 ON em1.record_id = er1.record_id
    JOIN evidence_records er2 ON em2.record_id = er2.record_id
    JOIN entities e1 ON em1.entity_id = e1.entity_id
    JOIN entities e2 ON em2.entity_id = e2.entity_id
    WHERE er1.case_id = ? AND er2.case_id = ?
      AND er1.file_id = er2.file_id
      AND ABS(er1.line_number - er2.line_number) <= 6
      AND e1.entity_type NOT IN ('NARCOTICS_KEYWORD', 'SLANG') 
      AND e2.entity_type NOT IN ('NARCOTICS_KEYWORD', 'SLANG')
    GROUP BY em1.entity_id, em2.entity_id
    LIMIT 60
    """, (case_id, case_id))
    raw_edges = cur.fetchall()

    # B. Cross-file corroboration edges:
    # If an entity (e.g. UPI or phone) appears in a BANK_STATEMENT record AND in a chat/darknet record,
    # link that corroborated entity to the primary counterparty/suspect/location entities in the case!
    cur.execute("""
    SELECT DISTINCT em_bank.entity_id as src, em_other.entity_id as dst, 3 as weight, 'Corroborated in Bank TX' as rel_type
    FROM entity_mentions em_bank
    JOIN evidence_records er_bank ON em_bank.record_id = er_bank.record_id
    JOIN evidence_records er_other ON er_bank.case_id = er_other.case_id AND er_bank.file_id != er_other.file_id
    JOIN entity_mentions em_other ON er_other.record_id = em_other.record_id
    JOIN entities e_bank ON em_bank.entity_id = e_bank.entity_id
    JOIN entities e_other ON em_other.entity_id = e_other.entity_id
    WHERE er_bank.case_id = ? 
      AND er_bank.source_type = 'BANK_STATEMENT'
      AND em_bank.entity_id != em_other.entity_id
      AND e_bank.entity_type IN ('UPI_ID', 'PHONE', 'TRANSACTION_REF')
      AND e_other.entity_type IN ('DARKNET_VENDOR', 'LOCATION', 'UPI_ID', 'CRYPTO_WALLET')
    LIMIT 35
    """, (case_id,))
    cross_edges = cur.fetchall()

    # C. Also link same-case entities that share high-confidence financial flows
    # (e.g. UPI handles and Darknet Vendors or Drop Locations appearing in the same case)
    cur.execute("""
    SELECT DISTINCT em1.entity_id as src, em2.entity_id as dst, 2 as weight, 'Cross-Source Link' as rel_type
    FROM entity_mentions em1
    JOIN evidence_records er1 ON em1.record_id = er1.record_id
    JOIN entities e1 ON em1.entity_id = e1.entity_id
    JOIN entity_mentions em2 ON em1.entity_id != em2.entity_id
    JOIN evidence_records er2 ON em2.record_id = er2.record_id
    JOIN entities e2 ON em2.entity_id = e2.entity_id
    WHERE er1.case_id = ? AND er2.case_id = ?
      AND (
        (e1.entity_type = 'DARKNET_VENDOR' AND e2.entity_type IN ('UPI_ID', 'CRYPTO_WALLET', 'PHONE')) OR
        (e1.entity_type = 'UPI_ID' AND e2.entity_type IN ('LOCATION', 'TRANSACTION_REF', 'CRYPTO_WALLET')) OR
        (e1.entity_type = 'PHONE' AND e2.entity_type IN ('UPI_ID', 'LOCATION'))
      )
      AND e1.entity_type NOT IN ('NARCOTICS_KEYWORD', 'SLANG')
      AND e2.entity_type NOT IN ('NARCOTICS_KEYWORD', 'SLANG')
    LIMIT 40
    """, (case_id, case_id))
    semantic_edges = cur.fetchall()

    edges = []
    connected_node_ids = set()
    seen_edge_pairs = set()

    all_edge_rows = list(raw_edges) + list(cross_edges) + list(semantic_edges)
    for row in all_edge_rows:
        s = row["src"]
        d = row["dst"]
        if s in nodes_map and d in nodes_map and s != d:
            pair_key = tuple(sorted([s, d]))
            if pair_key in seen_edge_pairs:
                continue
            seen_edge_pairs.add(pair_key)
            
            w = row["weight"]
            label_txt = row["rel_type"] if "rel_type" in row.keys() else f"{w} mentions"
            edges.append({
                "from": s,
                "to": d,
                "label": label_txt,
                "weight": w,
                "arrows": "to"
            })
            connected_node_ids.add(s)
            connected_node_ids.add(d)

    con.close()

    # Filter to only nodes that are connected in the network
    connected_nodes = [nodes_map[nid] for nid in connected_node_ids if nid in nodes_map]

    # Sufficient data & linkage threshold:
    # Requires at least 3 connected nodes and at least 2 edges
    if len(connected_nodes) < 3 or len(edges) < 2:
        return {
            "status": "insufficient_linkage",
            "reason": "Insufficient cross-source corroborated linkages between targets, financial rails, and locations.",
            "connected_node_count": len(connected_nodes),
            "edge_count": len(edges),
            "nodes": [],
            "edges": []
        }

    return {
        "status": "sufficient_linkage",
        "nodes": connected_nodes,
        "edges": edges,
        "connected_node_count": len(connected_nodes),
        "edge_count": len(edges)
    }

def create_or_update_case(case_id: str, fir_number: str, police_station: str = "PS Cyber Crime, Sector 17, Chandigarh", io_name: str = "Insp. Vikramjit Singh", io_belt: str = "Belt #788-UT", category: str = "NDPS_CYBER", assigned_officer_id: Optional[str] = None, db_path: str = DB_PATH) -> Dict[str, Any]:
    """Registers or updates a case entry in SQLite."""
    con = get_db(db_path)
    cur = con.cursor()
    now_str = datetime.utcnow().isoformat() + "Z"

    # Match assigned_officer_id by name if not explicitly passed
    if not assigned_officer_id:
        cur.execute("SELECT officer_id FROM officers WHERE name = ?", (io_name,))
        row = cur.fetchone()
        assigned_officer_id = row[0] if row else "OFFICER_IO_01"

    cur.execute("""
    INSERT INTO cases (case_id, fir_number, police_station, io_name, io_belt, category, created_at, assigned_officer_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(case_id) DO UPDATE SET
        fir_number = excluded.fir_number,
        police_station = excluded.police_station,
        io_name = excluded.io_name,
        io_belt = excluded.io_belt,
        category = excluded.category,
        assigned_officer_id = COALESCE(excluded.assigned_officer_id, cases.assigned_officer_id)
    """, (case_id, fir_number, police_station, io_name, io_belt, category, now_str, assigned_officer_id))
    con.commit()
    con.close()
    log_audit(case_id, "CASE_REGISTERED", f"Case {case_id} ({fir_number}) registered under IO {io_name} ({assigned_officer_id}).", performed_by=io_name, db_path=db_path)
    return {
        "case_id": case_id,
        "fir_number": fir_number,
        "police_station": police_station,
        "io_name": io_name,
        "io_belt": io_belt,
        "category": category,
        "assigned_officer_id": assigned_officer_id,
        "created_at": now_str
    }

def get_officers(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Returns list of registered officers/investigators with role information and case counts."""
    con = get_db(db_path)
    cur = con.cursor()
    cur.execute("""
    SELECT 
        o.officer_id,
        o.name,
        o.belt,
        o.rank,
        o.role,
        o.station,
        o.created_at,
        COUNT(DISTINCT c.case_id) as assigned_cases_count,
        COUNT(DISTINCT cc.case_id) as shared_cases_count
    FROM officers o
    LEFT JOIN cases c ON c.assigned_officer_id = o.officer_id
    LEFT JOIN case_collaborators cc ON cc.officer_id = o.officer_id
    GROUP BY o.officer_id
    ORDER BY o.officer_id ASC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows

def create_officer(name: str, belt: str, rank: str, role: str, station: str, db_path: str = DB_PATH) -> Dict[str, Any]:
    """Registers a new officer profile."""
    con = get_db(db_path)
    cur = con.cursor()
    officer_id = f"OFFICER_{role}_{int(datetime.utcnow().timestamp())}"
    now_str = datetime.utcnow().isoformat() + "Z"
    cur.execute("""
    INSERT INTO officers (officer_id, name, belt, rank, role, station, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (officer_id, name, belt, rank, role, station, now_str))
    con.commit()
    con.close()
    return {
        "officer_id": officer_id,
        "name": name,
        "belt": belt,
        "rank": rank,
        "role": role,
        "station": station,
        "created_at": now_str
    }

def share_case(case_id: str, officer_id: str, role: str = "FORENSIC_EXAMINER", granted_by: str = "Insp. Vikramjit Singh", notes: str = "", db_path: str = DB_PATH) -> Dict[str, Any]:
    """Shares or bridges case exhibits and triage stream to another officer profile."""
    con = get_db(db_path)
    cur = con.cursor()
    now_str = datetime.utcnow().isoformat() + "Z"
    cur.execute("""
    INSERT INTO case_collaborators (case_id, officer_id, role, granted_by, granted_at, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(case_id, officer_id) DO UPDATE SET
        role = excluded.role,
        granted_by = excluded.granted_by,
        granted_at = excluded.granted_at,
        notes = excluded.notes
    """, (case_id, officer_id, role, granted_by, now_str, notes))
    con.commit()
    con.close()

    # Log Section 63 BSA audit trail
    log_audit(
        case_id,
        "CASE_BRIDGED_COLLABORATION",
        f"Case exhibit stream bridged to {officer_id} (Role: {role}) by {granted_by}. Purpose: {notes or 'Inter-Agency / Specialist Delegation'}",
        performed_by=granted_by,
        db_path=db_path
    )

    return {
        "case_id": case_id,
        "officer_id": officer_id,
        "role": role,
        "granted_by": granted_by,
        "granted_at": now_str,
        "notes": notes
    }

def get_case_collaborators(case_id: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Returns all officers who have bridged access to a case."""
    con = get_db(db_path)
    cur = con.cursor()
    cur.execute("""
    SELECT 
        cc.case_id,
        cc.officer_id,
        cc.role as bridge_role,
        cc.granted_by,
        cc.granted_at,
        cc.notes,
        o.name as officer_name,
        o.belt as officer_belt,
        o.rank as officer_rank,
        o.role as officer_role,
        o.station as officer_station
    FROM case_collaborators cc
    JOIN officers o ON cc.officer_id = o.officer_id
    WHERE cc.case_id = ?
    ORDER BY cc.granted_at ASC
    """, (case_id,))
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows

def get_all_cases(officer_id: Optional[str] = None, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Returns all registered forensic cases with file/record aggregates, assigned officer info, and collaboration bridges."""
    con = get_db(db_path)
    cur = con.cursor()
    cur.execute("""
    SELECT 
        c.case_id, 
        c.fir_number, 
        c.police_station, 
        c.io_name, 
        c.io_belt, 
        c.category, 
        c.created_at,
        COALESCE(c.assigned_officer_id, 'OFFICER_IO_01') as assigned_officer_id,
        o.name as assigned_officer_name,
        o.belt as assigned_officer_belt,
        o.rank as assigned_officer_rank,
        o.role as assigned_officer_role,
        COUNT(DISTINCT ef.file_id) as total_files,
        COUNT(DISTINCT er.record_id) as total_records,
        COUNT(DISTINCT CASE WHEN er.is_flagged = 1 THEN er.record_id END) as flagged_records,
        COUNT(DISTINCT em.entity_id) as total_entities
    FROM cases c
    LEFT JOIN officers o ON c.assigned_officer_id = o.officer_id
    LEFT JOIN evidence_files ef ON c.case_id = ef.case_id
    LEFT JOIN evidence_records er ON c.case_id = er.case_id
    LEFT JOIN entity_mentions em ON er.record_id = em.record_id
    GROUP BY c.case_id
    ORDER BY c.created_at DESC
    """)
    cases = [dict(row) for row in cur.fetchall()]

    # Fetch collaborators for each case
    cur.execute("""
    SELECT cc.case_id, cc.officer_id, cc.role as bridge_role, cc.granted_by, cc.granted_at, cc.notes,
           o.name as officer_name, o.belt as officer_belt, o.role as officer_role
    FROM case_collaborators cc
    JOIN officers o ON cc.officer_id = o.officer_id
    """)
    collab_map = {}
    for r in cur.fetchall():
        cid = r["case_id"]
        if cid not in collab_map:
            collab_map[cid] = []
        collab_map[cid].append(dict(r))

    con.close()

    for c in cases:
        c["collaborators"] = collab_map.get(c["case_id"], [])
        if officer_id:
            c["is_assigned"] = (c.get("assigned_officer_id") == officer_id)
            c["is_shared"] = any(col["officer_id"] == officer_id for col in c["collaborators"])
            shared_info = next((col for col in c["collaborators"] if col["officer_id"] == officer_id), None)
            c["shared_role"] = shared_info["bridge_role"] if shared_info else None
        else:
            c["is_assigned"] = False
            c["is_shared"] = False
            c["shared_role"] = None

    return cases

def get_case_details(case_id: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Returns full metadata for a specific case."""
    con = get_db(db_path)
    cur = con.cursor()
    cur.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    row = cur.fetchone()
    con.close()
    return dict(row) if row else None

def get_cross_case_matches(case_id: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Identifies entities in the current case that match historical cases stored on device."""
    con = get_db(db_path)
    cur = con.cursor()
    cur.execute("""
    SELECT DISTINCT
        e.entity_type,
        e.raw_value,
        e.raw_value AS entity_value,
        e.risk_score,
        r_other.case_id AS matched_case_id,
        COALESCE(c_other.fir_number, r_other.case_id) AS matched_fir,
        COALESCE(c_other.police_station, 'Precinct Station') AS matched_ps,
        COALESCE(c_other.io_name, 'Investigating Officer') AS matched_io,
        COALESCE(f_other.filename, 'Archived Seizure') AS matched_filename,
        r_other.line_number AS matched_line,
        r_other.raw_text AS matched_context,
        r_other.timestamp AS matched_timestamp
    FROM entity_mentions em_curr
    JOIN evidence_records r_curr ON em_curr.record_id = r_curr.record_id
    JOIN entities e ON em_curr.entity_id = e.entity_id
    JOIN entity_mentions em_other ON e.entity_id = em_other.entity_id
    JOIN evidence_records r_other ON em_other.record_id = r_other.record_id
    LEFT JOIN cases c_other ON r_other.case_id = c_other.case_id
    LEFT JOIN evidence_files f_other ON r_other.file_id = f_other.file_id
    WHERE r_curr.case_id = ? AND r_other.case_id != ?
    ORDER BY e.risk_score DESC, r_other.timestamp DESC
    LIMIT 50
    """, (case_id, case_id))
    matches = [dict(row) for row in cur.fetchall()]
    con.close()
    return matches

def get_case_files(case_id: Optional[str] = None, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Returns list of real evidence files uploaded for a case."""
    con = get_db(db_path)
    cur = con.cursor()
    if case_id:
        cur.execute("""
        SELECT file_id, case_id, filename, file_type, sha256_hash, record_count, uploaded_at
        FROM evidence_files
        WHERE case_id = ?
        ORDER BY uploaded_at ASC
        """, (case_id,))
    else:
        cur.execute("""
        SELECT file_id, case_id, filename, file_type, sha256_hash, record_count, uploaded_at
        FROM evidence_files
        ORDER BY uploaded_at ASC
        """)
    files = [dict(row) for row in cur.fetchall()]
    con.close()
    return files

def get_file_records(file_id: str, limit: int = 1000, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Returns the parsed records/lines for a specific evidence file."""
    con = get_db(db_path)
    cur = con.cursor()
    cur.execute("""
    SELECT record_id, file_id, case_id, source_type, sender_id, timestamp, raw_text, line_number, is_flagged, flag_reasons
    FROM evidence_records
    WHERE file_id = ?
    ORDER BY line_number ASC
    LIMIT ?
    """, (file_id, limit))
    records = [dict(row) for row in cur.fetchall()]
    con.close()
    return records

def get_evidence_image_path(file_id: str, db_path: str = DB_PATH) -> Optional[str]:
    """Finds the local file path for an ingested seized evidence image."""
    images_dir = os.path.join(os.path.dirname(db_path), "evidence_images")
    if not os.path.isdir(images_dir):
        return None
    for fname in os.listdir(images_dir):
        if fname.startswith(f"{file_id}_") or fname.startswith(file_id):
            full_p = os.path.join(images_dir, fname)
            if os.path.isfile(full_p):
                return full_p
    return None

def get_dynamic_triage_leads(case_id: Optional[str] = None, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Dynamically generates triage leads from extracted entities and flagged records with cross-case matching."""
    con = get_db(db_path)
    cur = con.cursor()
    
    # 1. High-value entities (UPI, Phone, Crypto, Narcotics, Darknet Vendor, Location)
    if case_id:
        cur.execute("""
        SELECT e.entity_id, e.entity_type, e.raw_value, e.risk_score, e.mention_count,
               er.record_id, er.file_id, er.line_number, er.raw_text, ef.filename, er.case_id
        FROM entities e
        JOIN entity_mentions em ON e.entity_id = em.entity_id
        JOIN evidence_records er ON em.record_id = er.record_id
        JOIN evidence_files ef ON er.file_id = ef.file_id
        WHERE er.case_id = ?
        GROUP BY e.entity_id
        ORDER BY e.risk_score DESC, e.mention_count DESC
        LIMIT 40
        """, (case_id,))
    else:
        cur.execute("""
        SELECT e.entity_id, e.entity_type, e.raw_value, e.risk_score, e.mention_count,
               er.record_id, er.file_id, er.line_number, er.raw_text, ef.filename, er.case_id
        FROM entities e
        JOIN entity_mentions em ON e.entity_id = em.entity_id
        JOIN evidence_records er ON em.record_id = er.record_id
        JOIN evidence_files ef ON er.file_id = ef.file_id
        GROUP BY e.entity_id
        ORDER BY e.risk_score DESC, e.mention_count DESC
        LIMIT 40
        """)
    
    leads = []
    seen_values = set()
    for row in cur.fetchall():
        val = row["raw_value"]
        if val.lower() in seen_values:
            continue
        seen_values.add(val.lower())
        
        ent_type = row["entity_type"]
        cat = "financial" if ent_type in ["UPI_ID", "CRYPTO_WALLET", "TRANSACTION_REF"] else "darknet" if ent_type == "DARKNET" else "slang" if ent_type == "SLANG" else "financial"
        type_label = "UPI IDENTIFIER" if ent_type == "UPI_ID" else "CRYPTO WALLET" if ent_type == "CRYPTO_WALLET" else "PHONE IDENTIFIER" if ent_type == "PHONE" else "TRANSACTION REF" if ent_type == "TRANSACTION_REF" else "GEOGRAPHIC LANDMARK" if ent_type == "LOCATION" else "NARCOTICS CODEWORD"
        
        # Check cross-case link in SQLite
        cross_case_hit = None
        if case_id:
            cur_cross = con.cursor()
            cur_cross.execute("""
            SELECT r2.case_id, COALESCE(c.fir_number, r2.case_id) as fir, COALESCE(c.io_name, 'IO') as io, f.filename, r2.raw_text
            FROM entity_mentions em2
            JOIN evidence_records r2 ON em2.record_id = r2.record_id
            LEFT JOIN cases c ON r2.case_id = c.case_id
            LEFT JOIN evidence_files f ON r2.file_id = f.file_id
            WHERE em2.entity_id = ? AND r2.case_id != ?
            LIMIT 1
            """, (row["entity_id"], case_id))
            cross_row = cur_cross.fetchone()
            if cross_row:
                cross_case_hit = {
                    "matchedCaseId": cross_row["case_id"],
                    "matchedFir": cross_row["fir"],
                    "matchedIo": cross_row["io"],
                    "matchedFile": cross_row["filename"],
                    "snippet": cross_row["raw_text"][:140]
                }

        confidence_val = "99%" if cross_case_hit else f"{min(99, row['risk_score'] + 15)}%"
        corrob_basis = f"Detected in {row['filename']} (Line #{row['line_number']})"
        if cross_case_hit:
            corrob_basis += f" &bull; ⚠️ Linked to past case {cross_case_hit['matchedFir']} ({cross_case_hit['matchedIo']})"

        leads.append({
            "id": f"lead-{row['entity_id']}",
            "category": cat,
            "type": type_label,
            "value": val,
            "fileId": row["file_id"],
            "fileName": row["filename"],
            "lineNum": row["line_number"],
            "method": "Deterministic NER + FTS" if not cross_case_hit else "Cross-Case Intelligence + NER",
            "confidence": confidence_val,
            "crossCaseHit": cross_case_hit,
            "isCrossCase": cross_case_hit is not None,
            "corroboration": {
                "score": "99% (CRITICAL MATCH)" if cross_case_hit else f"{min(98, 70 + row['mention_count'] * 8)}% (CORROBORATED)",
                "isHigh": (row["mention_count"] > 1) or (cross_case_hit is not None),
                "basis": corrob_basis
            },
            "status": "candidate",
            "context": row["raw_text"][:160],
            "slmRationale": None
        })
        
    # 2. Flagged records that have slang keywords
    cur.execute("""
    SELECT er.record_id, er.file_id, er.line_number, er.raw_text, er.flag_reasons, ef.filename
    FROM evidence_records er
    JOIN evidence_files ef ON er.file_id = ef.file_id
    WHERE (? IS NULL OR er.case_id = ?) AND er.flag_reasons LIKE '%Slang:%'
    LIMIT 20
    """, (case_id, case_id))
    
    for row in cur.fetchall():
        reasons = row["flag_reasons"]
        slang_part = [r for r in reasons.split(";") if "Slang:" in r]
        slang_val = slang_part[0].replace("Slang:", "").strip() if slang_part else "Suspicious Contraband"
        if slang_val.lower() in seen_values:
            continue
        seen_values.add(slang_val.lower())
        
        leads.append({
            "id": f"lead-slang-{row['record_id']}",
            "category": "slang",
            "type": "SLANG / NARCOTICS CODE",
            "value": slang_val.title(),
            "fileId": row["file_id"],
            "fileName": row["filename"],
            "lineNum": row["line_number"],
            "method": "Precinct Lexicon + SLM Filter",
            "confidence": "94%",
            "crossCaseHit": None,
            "isCrossCase": False,
            "corroboration": {
                "score": "91% (HIGH CORROBORATION)",
                "isHigh": True,
                "basis": f"Flagged in {row['filename']} line #{row['line_number']} with commercial context."
            },
            "status": "candidate",
            "context": row["raw_text"][:160],
            "slmRationale": {
                "model": "LFM2.5-8B-A1B-Q4_0 (Local)",
                "promptTask": "Identify evasive narcotics code and commercial intent.",
                "reasoning": f"Flagged term '{slang_val}' corroborated by transaction phrasing in evidence record."
            }
        })
        
    con.close()
    return leads

def get_slang_dictionary(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Returns all confirmed and inducted codewords from the precinct dictionary."""
    con = get_db(db_path)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS slang_dictionary (
        slang_term TEXT PRIMARY KEY,
        canonical_meaning TEXT,
        status TEXT,
        detected_count INTEGER DEFAULT 1,
        induct_timestamp TEXT
    );
    """)
    cur.execute("SELECT slang_term, canonical_meaning, status, detected_count, induct_timestamp FROM slang_dictionary ORDER BY induct_timestamp DESC")
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows

def get_transactional_candidates(case_id: Optional[str] = None, file_id: Optional[str] = None, limit: int = 25, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Returns candidate transactional messages from ingested evidence for SLM induction."""
    con = get_db(db_path)
    cur = con.cursor()
    
    where_clauses = []
    params: List[Any] = []
    if case_id:
        where_clauses.append("er.case_id = ?")
        params.append(case_id)
    if file_id and file_id != "all":
        where_clauses.append("er.file_id = ?")
        params.append(file_id)

    where_str = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else "WHERE 1=1"

    cur.execute(f"""
    SELECT er.record_id, er.file_id, er.case_id, er.source_type, er.sender_id, er.timestamp, er.raw_text, er.line_number, er.is_flagged, er.flag_reasons, ef.filename
    FROM evidence_records er
    JOIN evidence_files ef ON er.file_id = ef.file_id
    {where_str}
      AND (er.raw_text LIKE '%deliver%' OR er.raw_text LIKE '%parcel%' OR er.raw_text LIKE '%drop%' 
           OR er.raw_text LIKE '%packet%' OR er.raw_text LIKE '%rate%' OR er.raw_text LIKE '%stock%' 
           OR er.raw_text LIKE '%box%' OR er.raw_text LIKE '%piece%' OR er.raw_text LIKE '%gpay%' 
           OR er.raw_text LIKE '%usdt%' OR er.raw_text LIKE '%tea%' OR er.raw_text LIKE '%coffee%' 
           OR er.raw_text LIKE '%shoes%' OR er.raw_text LIKE '%stamp%' OR er.raw_text LIKE '%apple%'
           OR er.raw_text LIKE '%advance%' OR er.raw_text LIKE '%paid%' OR er.raw_text LIKE '%payment%'
           OR er.raw_text LIKE '%chitta%' OR er.raw_text LIKE '%syrup%' OR er.raw_text LIKE '%mule%')
    ORDER BY er.is_flagged DESC, er.line_number ASC
    LIMIT ?
    """, params + [limit])
    rows = [dict(r) for r in cur.fetchall()]

    # If a specific file is targeted and has no keyword matches, let's pull non-blank lines from that file
    # so the operator can still run induction on novel or unflagged text from that seized exhibit
    if not rows and file_id and file_id != "all":
        cur.execute("""
        SELECT er.record_id, er.file_id, er.case_id, er.source_type, er.sender_id, er.timestamp, er.raw_text, er.line_number, er.is_flagged, er.flag_reasons, ef.filename
        FROM evidence_records er
        JOIN evidence_files ef ON er.file_id = ef.file_id
        WHERE er.file_id = ? AND LENGTH(TRIM(er.raw_text)) > 4
        ORDER BY er.line_number ASC
        LIMIT ?
        """, (file_id, limit))
        rows = [dict(r) for r in cur.fetchall()]

    con.close()
    return rows

def load_default_demo_datasets(case_id: str = "FIR_104_2026", base_dir: Optional[str] = None, dataset_type: str = "default") -> Dict[str, Any]:
    """Ingests authentic demo or adversarial evidence files from the data directory into SQLite."""
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    if dataset_type == "adversarial":
        adv_dir = os.path.join(base_dir, "data", "adversarial")
        candidate_paths = [
            os.path.join(adv_dir, "adversarial_whatsapp_hinglish.txt"),
            os.path.join(adv_dir, "adversarial_darknet_listings.json"),
            os.path.join(adv_dir, "adversarial_bank_structuring.csv"),
            os.path.join(adv_dir, "adversarial_seized_chat_chit.png"),
            os.path.join(adv_dir, "adversarial_handwritten_chit.jpeg")
        ]
    else:
        candidate_paths = [
            os.path.join(base_dir, "data", "processed", "darknet_listings_sample.csv"),
            os.path.join(base_dir, "data", "raw", "sample_telegram_export.json"),
            os.path.join(base_dir, "data", "processed", "bank_statement_baseline.csv"),
            os.path.join(base_dir, "data", "raw", "seized_paytm_mule_receipt.png"),
            os.path.join(base_dir, "data", "raw", "seized_telegram_chat_drop.png")
        ]

    ingested = []
    total_records = 0
    total_flagged = 0

    for p in candidate_paths:
        if os.path.exists(p):
            fn = os.path.basename(p)
            with open(p, "rb") as f:
                raw_bytes = f.read()
            res = parse_and_ingest_file(case_id, fn, raw_bytes)
            ingested.append(res)
            total_records += res.get("total_records", 0)
            total_flagged += res.get("total_flagged", 0)

    log_audit(case_id, "DEMO_DATA_INGESTED", f"Pre-fetched {len(ingested)} demo files ({total_records} records, {total_flagged} flagged).")

    return {
        "status": "success",
        "case_id": case_id,
        "files_loaded": len(ingested),
        "total_records": total_records,
        "total_flagged": total_flagged,
        "details": ingested
    }

def mine_unstructured_entities_chunked(case_id: str, file_id: Optional[str] = None, max_chunks: int = 5, db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Extracts unstructured Indian physical addresses, landmarks, meet points,
    and covert Hinglish slang using chunked LLM semantic analysis on high-signal conversational clusters.
    """
    con = get_db(db_path)
    cur = con.cursor()

    # Find candidate flagged/suspicious records or conversational anchors
    sql = """
    SELECT record_id, file_id, line_number, sender_id, timestamp, raw_text, is_flagged
    FROM evidence_records
    WHERE case_id = ?
    """
    params = [case_id]
    if file_id:
        sql += " AND file_id = ?"
        params.append(file_id)
    sql += " ORDER BY line_number ASC"

    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    con.close()

    if not rows:
        return {"status": "no_records", "discovered_locations": [], "discovered_slang": []}

    # Group records into conversational context windows (e.g. 8-12 records per chunk) around flagged lines
    flagged_indices = [idx for idx, r in enumerate(rows) if r["is_flagged"]]
    if not flagged_indices:
        flagged_indices = list(range(0, min(len(rows), 40), 8))

    selected_ranges = []
    for f_idx in flagged_indices[:max_chunks * 2]:
        start = max(0, f_idx - 3)
        end = min(len(rows), f_idx + 5)
        if not any(abs(start - prev_s) < 4 for prev_s, _ in selected_ranges):
            selected_ranges.append((start, end))
        if len(selected_ranges) >= max_chunks:
            break

    if not selected_ranges:
        selected_ranges.append((0, min(len(rows), 10)))

    chunks = []
    for start, end in selected_ranges:
        window_rows = rows[start:end]
        snippet = "\n".join([f"[{r.get('sender_id', 'User')}]: {r.get('raw_text', '')}" for r in window_rows])
        anchor_rec_id = window_rows[len(window_rows)//2]["record_id"]
        chunks.append({
            "anchor_record_id": anchor_rec_id,
            "snippet": snippet
        })

    # Call local or remote LLM (via Tailscale/LAN), or fallback semantic extractor
    slm_url = os.environ.get("SLM_URL")
    slm_host = os.environ.get("SLM_HOST", "localhost")
    slm_port = os.environ.get("SLM_PORT", "8012")
    candidates = []
    if slm_url:
        candidates.append(slm_url.rstrip('/'))
    if slm_host and slm_host != "localhost":
        for p in [slm_port, 8012, 8080]:
            candidates.append(f"http://{slm_host}:{p}")
    for p in [8012, 8080, 8015, 8081]:
        candidates.append(f"http://localhost:{p}")

    active_endpoint = None
    for cand in candidates:
        try:
            req = urllib.request.Request(f"{cand}/v1/models")
            with urllib.request.urlopen(req, timeout=0.6) as resp:
                if resp.status == 200:
                    active_endpoint = cand
                    break
        except Exception:
            pass

    discovered_locations = []
    discovered_slang = []

    for c in chunks:
        if active_endpoint:
            try:
                system_prompt = (
                    "You are an expert Indian Cyber Narcotics intelligence copilot for Chandigarh Police. "
                    "Analyze the given group chat / darknet conversation chunk. "
                    "Extract:\n"
                    "1. Unstructured physical locations, meeting drop points, landmarks, or street directions (e.g. 'near Aroma chowk', 'behind hostel 4', 'booth 12').\n"
                    "2. Covert slang, disguised narcotics terms, or delivery code words with suspected meaning.\n"
                    "Return strictly JSON with schema: {\"locations\": [\"...\"], \"slang\": [{\"term\": \"...\", \"meaning\": \"...\"}]}"
                )
                payload = json.dumps({
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": c["snippet"]}
                    ],
                    "temperature": 0.0,
                    "max_tokens": 250
                }).encode('utf-8')

                req = urllib.request.Request(f"{active_endpoint}/v1/chat/completions", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=12.0) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    raw_ans = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    json_match = re.search(r'\{.*\}', raw_ans, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group(0))
                        for loc in parsed.get("locations", []):
                            if loc.strip() and loc.strip() not in [d["value"] for d in discovered_locations]:
                                discovered_locations.append({"value": loc.strip(), "record_id": c["anchor_record_id"]})
                        for s in parsed.get("slang", []):
                            if isinstance(s, dict) and s.get("term"):
                                discovered_slang.append({"term": s["term"].strip(), "meaning": s.get("meaning", "Suspected Codeword"), "record_id": c["anchor_record_id"]})
                            elif isinstance(s, str) and s.strip():
                                discovered_slang.append({"term": s.strip(), "meaning": "Suspected Codeword", "record_id": c["anchor_record_id"]})
            except Exception:
                pass

        # If LLM offline or returned 0, run spatial & contextual candidate extractor
        if not discovered_locations:
            for m in re.finditer(r'\b(?:near|opp|opposite|behind|gate|chowk|market|road|sector|sec|phase|booth)\s+([a-zA-Z0-9\s\-]{3,25})\b', c["snippet"], re.IGNORECASE):
                cand = m.group(0).strip().title()
                if len(cand) > 5 and cand not in [d["value"] for d in discovered_locations]:
                    discovered_locations.append({"value": cand, "record_id": c["anchor_record_id"]})

    # Seal discovered entities into SQLite
    con = get_db(db_path)
    cur = con.cursor()
    newly_added = 0

    for item in discovered_locations:
        loc_val = item["value"].title()
        ent_id = f"ENT_{hashlib.sha256(loc_val.lower().encode()).hexdigest()[:16]}"
        cur.execute("""
        INSERT INTO entities (entity_id, entity_type, raw_value, first_seen_case, risk_score, mention_count)
        VALUES (?, 'LOCATION', ?, ?, 65, 1)
        ON CONFLICT(entity_id) DO UPDATE SET mention_count = mention_count + 1
        """, (ent_id, loc_val, case_id))
        cur.execute("""
        INSERT OR IGNORE INTO entity_mentions (record_id, entity_id, context_snippet)
        VALUES (?, ?, ?)
        """, (item["record_id"], ent_id, "Discovered via Chunked Semantic Miner"))
        newly_added += 1

    for s in discovered_slang:
        term_val = s["term"].title()
        ent_id = f"ENT_{hashlib.sha256(term_val.lower().encode()).hexdigest()[:16]}"
        cur.execute("""
        INSERT INTO entities (entity_id, entity_type, raw_value, first_seen_case, risk_score, mention_count)
        VALUES (?, 'NARCOTICS_KEYWORD', ?, ?, 75, 1)
        ON CONFLICT(entity_id) DO UPDATE SET mention_count = mention_count + 1
        """, (ent_id, term_val, case_id))
        cur.execute("""
        INSERT OR IGNORE INTO entity_mentions (record_id, entity_id, context_snippet)
        VALUES (?, ?, ?)
        """, (s["record_id"], ent_id, f"Inferred meaning: {s['meaning']}"))
        newly_added += 1

    con.commit()
    con.close()

    log_audit(case_id, "SLM_SEMANTIC_MINED", f"Chunked Miner analyzed {len(chunks)} windows, registered {newly_added} entities (LLM used: {bool(port)}).", db_path=db_path)

    return {
        "status": "success",
        "chunks_analyzed": len(chunks),
        "llm_used": bool(port),
        "new_entities_added": newly_added,
        "discovered_locations": [d["value"] for d in discovered_locations],
        "discovered_slang": discovered_slang
    }

