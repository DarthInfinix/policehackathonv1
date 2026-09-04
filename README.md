# TACTICAL EVIDENCE TRIAGE & CORRELATION PLATFORM (TETCP)
### Chandigarh Police Hackathon 2026 — Problem Statement 3 (PS3-DWID)
> **Track:** Detection of Illicit Drug Sales on Darknet and Other Encrypted Platforms  
> **Legal Compliance:** Section 63(4) Bharatiya Sakshya Adhiniyam (BSA), 2023  
> **Architecture:** 100% Air-Gapped, Local-First, Zero Cloud Lock-In

---

## 1. Executive Summary & Core Mission

Frontline law enforcement officers frequently seize gigabytes of messy, unstructured digital evidence—Tor marketplace `.onion` HTML mirrors, raw Telegram/WhatsApp chat dumps, bank statement CSVs, and phone camera screenshots. 

Existing workflows suffer from manual fatigue, tool fragmentation, and strict legal vulnerability under India's new criminal codes (**Bharatiya Sakshya Adhiniyam, 2023**).

This platform acts as an **air-gapped forensic copilot** that:
1. **Ingests & Normalizes** heterogeneous seized data without cloud dependencies.
2. **Extracts Deterministic Identifiers** (Indian UPI handles, +91 phone numbers, TRON/Bitcoin wallets) with zero latency.
3. **Triages Evasion Slang** (*Chitta, White Shoes, Ice Tea, Pudiya*) using an offline, quantized Small Language Model (SLM).
4. **Correlates Entities** across cases into an interactive visual link graph (`Vendor ➔ Telegram Admin ➔ UPI Mule ➔ Drop Location`).
5. **Generates Dual Outputs:** Instant field WhatsApp dispatches for PCR patrol vans, and court-admissible Section 63 BSA Digital Evidence Certificates with SHA-256 hash chains.

---

## 2. Quickstart (Running Offline in 60 Seconds)

The application is designed to run completely offline without npm builds or complex dependencies.

### Prerequisites
- Python 3.9+ installed on your system.
- Modern web browser (Chrome, Edge, Firefox).

### Launching the Dashboard
From the root repository directory, run:
```bash
python3 -m http.server 8000
```
Open your browser and navigate to:
```
http://localhost:8000/
```
*(When backend services are active, the UI connects to `http://localhost:8000/api`. If the backend is not running, the dashboard operates seamlessly using pre-compiled offline forensic fixtures).*

---

## 3. Modular Team Demarcation (AI Agent Prompts)

To prevent merge conflicts and ensure clean modular development, **do NOT edit core UI files directly**. 

Each team member has a self-contained, isolated module. **Copy the exact prompt block below and paste it directly into your Gemini Pro / AI assistant.**

---

### 🔹 MEMBER 1: Case Storage & Audit Trail Module
* **Deliverable:** A standalone Python module `storage.py` (standard library `sqlite3` only).
* **Scope:** Zero external database server setup. Manages single-file SQLite database with full-text search (FTS5) and immutable SHA-256 audit logging.
* **Copy-Paste Prompt for Gemini Pro:**
```text
You are a senior systems engineer building a local forensic storage module for a law enforcement hackathon.

Write a self-contained Python 3 script named `storage.py` using ONLY the standard library (`sqlite3`, `hashlib`, `json`, `datetime`).

Requirements:
1. Database File: `precinct_evidence.db`
2. Tables to create:
   - `cases` (case_id TEXT PRIMARY KEY, fir_number TEXT, io_name TEXT, created_at TEXT)
   - `evidence_records` (record_id TEXT PRIMARY KEY, case_id TEXT, source_type TEXT, raw_text TEXT, line_number INT, sha256_hash TEXT)
   - `entities` (entity_id TEXT PRIMARY KEY, entity_type TEXT, raw_value TEXT UNIQUE, risk_score INT)
   - `audit_log` (log_id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT, action TEXT, performed_by TEXT, timestamp TEXT, record_hash TEXT)
3. Full-Text Search: Create an FTS5 virtual table indexing `raw_text` for instant keyword lookups.
4. Implement functions:
   - `init_db()`
   - `save_case(case_id, fir, io_name)`
   - `insert_record(case_id, source_type, raw_text, line_number)`: auto-computes SHA-256 and logs to audit_log.
   - `search_records(keyword)`: fast full-text search returning matching records with line numbers.
   - `check_cross_case_hit(raw_value)`: checks if a phone number or UPI handle already appeared in past cases.
5. Include a clean `if __name__ == "__main__":` block demonstrating the creation of a mock case, inserting 3 records, and executing a cross-case search.
```

---

### 🔹 MEMBER 2: Regex Extractor & Offline OCR Worker
* **Deliverable:** A standalone Python module `extractor.py`.
* **Scope:** Deterministic pattern extraction (high recall) for Indian payment handles and crypto wallets, with fallback image text extraction.
* **Copy-Paste Prompt for Gemini Pro:**
```text
You are a digital forensics specialist creating a fast, deterministic entity extractor for Indian law enforcement.

Write a standalone Python 3 script named `extractor.py` using standard `re`, `json`, and optionally `pytesseract` or `easyocr`.

Requirements:
1. Extract Indian Phone Numbers:
   - Standard 10-digit Indian numbers starting with 6, 7, 8, 9.
   - Prefixes with +91, 0, or formatted with hyphens/spaces (e.g. +91-98140-12345).
2. Extract Indian UPI Handles (VPAs):
   - Format: `username@bank` (e.g., @okhdfcbank, @ybl, @paytm, @icici, @axl, @upi).
3. Extract Cryptocurrency Wallets:
   - TRON (TRC-20 USDT): Starts with 'T', 34 alphanumeric characters.
   - Bitcoin: Starts with '1', '3', or 'bc1', 26-42 alphanumeric characters.
4. Extract Pricing & Quantity Indicators:
   - Detect amounts in INR (`₹`, `rs`, `inr`, `k`) and weights (`g`, `gram`, `pudiya`, `tola`).
5. OCR Function:
   - `extract_text_from_image(image_path)`: Uses pytesseract or easyocr to return text lines with timestamps.
6. Main Extraction Function:
   - `extract_all_entities(text)`: Returns a structured dictionary:
     `{"phones": [...], "upi_handles": [...], "crypto_wallets": [...], "pricing_hints": [...]}`
7. Include an `if __name__ == "__main__":` test block with a 5-line messy Hinglish drug negotiation snippet demonstrating 100% extraction accuracy.
```

---

### 🔹 MEMBER 3: Interactive Network Link-Graph Module
* **Deliverable:** A standalone JavaScript / HTML component `graph_view.js` (or standalone HTML preview `graph_preview.html`).
* **Scope:** Renders an entity relationship network linking suspects, UPI accounts, wallets, and drop points using **Vis.js Network** (CDN/local script, zero npm dependencies).
* **Copy-Paste Prompt for Gemini Pro:**
```text
You are a frontend data visualization engineer building an intelligence link-graph for police investigators.

Create a standalone HTML + JavaScript file named `graph_preview.html` using the Vis.js Network library (via CDN or local script tag).

Requirements:
1. Styling: Dark-mode forensic theme (dark slate background `#0f172a`, glowing node accents, clean monospace labels).
2. Node Types & Visual Encoding:
   - Suspects / Telegram Aliases: Red circles (icon or text label).
   - UPI Mule Accounts: Amber diamonds.
   - TRON / Crypto Wallets: Purple hexagons.
   - Dead-Drop Locations: Blue map-pins.
3. Interactive Features:
   - Physics-based force-directed layout (smooth bouncing and stabilizing).
   - Search/Filter input: Highlighting matching nodes on typing.
   - Click Event: When an investigator clicks a node, open a clean side-panel displaying:
     - Node Name & Type
     - Risk Score / Corroboration Status
     - Associated Case FIR Number
     - "Jump to Evidence" button.
4. Provide a rich mock dataset with 12 nodes and 15 edges modeling a realistic Chandigarh distribution ring (`Tor Vendor ➔ Telegram Admin ➔ Mule UPI ➔ Sector 26 Drop`).
```

---

### 🔹 MEMBER 4: Pitch Deck, Presentation Script & Section 63 BSA Dossier
* **Deliverable:** A complete 8-slide presentation deck structure, 3-minute jury pitch script, and legal justification dossier (`PITCH_DECK_AND_LEGAL_DOSSIER.md`).
* **Scope:** Equips non-coding team members to confidently command the table during evaluator visits and jury Q&A.
* **Copy-Paste Prompt for Gemini Pro:**
```text
You are a legal-tech strategist and hackathon pitch coach preparing a university team for the Grand Finale of the Chandigarh Police Hackathon 2026 (Problem Statement 3).

Generate a complete, exhaustive markdown document named `PITCH_DECK_AND_LEGAL_DOSSIER.md` containing:

1. 8-SLIDE PRESENTATION DECK BLUEPRINT:
   - Slide 1: The Frontline Reality (The flood of seized unformatted dumps).
   - Slide 2: The Core Problem (Evasion slang, crypto mules, courtroom inadmissibility).
   - Slide 3: The Architecture (Air-gapped, two-speed engine: Deterministic Regex + Local SLM).
   - Slide 4: Real-Time Entity Correlation & Cross-Case Matching.
   - Slide 5: Active Slang Induction (Human-in-the-loop candidate discovery).
   - Slide 6: Legal Grounding: Section 63(4) BSA 2023 vs Repealed 65B Evidence Act.
   - Slide 7: Operational Dual Packaging (PCR WhatsApp alert + Munshi Zimni text).
   - Slide 8: Technical Scalability & Zero Cloud Lock-In.
   Provide exact bullet points, speaker notes, and key visual ideas for every slide.

2. THE 3-MINUTE TABLE PITCH SCRIPT:
   - Word-for-word spoken script timed precisely to 180 seconds for when police evaluators walk up to our desk.

3. JURY DEFENSE & HARD QUESTIONS CHEAT-SHEET:
   - "Why not just use ChatGPT/OpenAI API?" ➔ (MHA evidence security directives, data privacy).
   - "What if the SLM hallucinates?" ➔ (Trace-to-Source byte jumping, deterministic foundation).
   - "How do you handle Wi-Fi outages?" ➔ (100% offline local model execution).
```

---

## 4. Repository Structure

```
├── index.html                  # Main forensic dashboard UI
├── styles.css                  # Dark-mode investigative stylesheet
├── app.js                      # UI logic, state management & mock fixtures
├── storage.py                  # (Member 1) SQLite case database & audit logger
├── extractor.py                # (Member 2) Regex entity parser & OCR engine
├── graph_preview.html          # (Member 3) Vis.js interactive network topology
├── PITCH_DECK_AND_LEGAL_DOSSIER.md # (Member 4) Jury deck, pitch script & legal cheat-sheet
├── HACKATHON_MASTER_STRATEGY_AND_BRIEF.md # Comprehensive strategic playbook
└── README.md                   # This document
```

---

## 5. Hackathon Code of Conduct & Ground Rules

1. **Air-Gap Rule:** No commercial external AI APIs (OpenAI, Anthropic, Claude) may be queried at runtime. Models must run locally (e.g., via Ollama/GGUF).
2. **Data Sanitization:** Never ingest live dark web PII or live illicit contraband. All demonstration fixtures must remain synthetic or public academic OSINT data (Rule 3 compliant).
3. **No Overwriting:** Each teammate works in their assigned file. Integration into the primary dashboard is handled centrally by the team lead.
