# TACTICAL EVIDENCE TRIAGE & CORRELATION PLATFORM (TETCP)
### Chandigarh Police Cyber Hackathon 2026 — Problem Statement 3 (PS3-DWID)
> **Track:** Detection of Illicit Drug Sales on Darknet and Other Encrypted Platforms  
> **Legal Compliance:** Section 63(4) Bharatiya Sakshya Adhiniyam (BSA), 2023  
> **Architecture:** 100% Air-Gapped, Local-First, Zero External Cloud Dependencies  
> **Main Branch Status:** Stable Core Active (`server.py` + `storage.py` + `app.js` + SQLite WAL Engine)

---

## 1. Quickstart: Running Main in 30 Seconds

The entire platform runs without `npm`, Node dependencies, Docker, or external cloud services.

### Prerequisites
- Python 3.9+ (Standard library only: `sqlite3`, `http.server`, `urllib`, `json`, `hashlib`).
- Local inference server (optional for full SLM induction): `llama-server` running on `localhost:8080` or `localhost:8012` with any GGUF (e.g. `LFM2.5-8B-A1B-Q4_0.gguf`, `llama-3.2-3b`, `gemma-2-2b`). If no local model is running, the platform operates seamlessly using heuristic semantic fallbacks.

### Launching the Platform

#### Option A: 1-Click Complete Startup Script (Recommended)
Automatically checks and launches `llama-server` instances for LiquidAI (port 8012) and dots.ocr (port 8015), starts `server.py` on port 8000, and opens the browser:
```bash
./start.sh
```

#### Option B: Standalone Web Server
```bash
python3 server.py
```
Open your browser to: `http://localhost:8000/`

### Instant 4-Step Verification
1. **Step 1 (Case Intake)**: Review prefilled Chandigarh Police case details (FIR 104/2026/CYBER, Sec 21/22 NDPS & Sec 66D IT Act), click **"Proceed to Evidence Media Intake ➔"**.
2. **Step 2 (Media Intake & Previews)**:
   - Browse or drag & drop seized evidence (images, CSVs, JSON, text dumps) or click **"⚡ Load Pre-Staged Datasets & OCR"**.
   - Review live staged cards: see image thumbnails with an explicit **`[✓] Run Neural OCR`** checkbox (allowing operator to run or skip OCR per image), and monospace preview boxes showing the first lines of CSV/text files.
   - Click **"Proceed to Engine Configuration ➔"**.
3. **Step 3 (Engine Presets)**:
   - **⚡ Light Mode (Default)**: Pure deterministic regex & financial NER + fast Tesseract OCR (0 GPU overhead).
   - **🧠 Accuracy Mode**: Deep contextual reasoning via LiquidAI (LFM2.5 on port 8012) + dots.ocr Neural ViT.
   - Click **"⚡ Start Forensic Pipeline & Triage ➔"**.
4. **Step 4 (Genuine Loading Screen)**:
   - Watches authentic live execution across exhibits: hashes files with SHA-256, streams neural OCR status and elapsed time, runs financial NER, queries correlations, and seals forensic records under Section 63(4) BSA before loading the Workbench.

---

## 2. What Has Been Built & Is Fully Functional (Main Branch)

All hardcoded mock data, fake preview arrays, and simulated files have been **completely eliminated**. The main branch is fully wired to an authentic SQLite forensic pipeline:

### A. Database Storage & Integrity Engine (`storage.py`)
- **SQLite WAL Mode**: Configured `PRAGMA journal_mode=WAL;`, `busy_timeout=30000;`, and `synchronous=NORMAL;` across all connections. Thread-safe concurrency prevents database locking.
- **Evidence Storage**:
  - `evidence_files`: Real uploaded files with calculated SHA-256 hashes, file types, line counts, and timestamps.
  - `evidence_records`: Normalized line-by-line evidence stream with forensic line numbers, timestamps, sender IDs, raw text, and detection flags.
  - `records_fts`: Full-text search virtual table (SQLite FTS5) indexing raw text and sender IDs for sub-millisecond searches.
  - `entities`: Extracted phones, UPI handles, crypto wallets, locations, and darknet vendor handles with mention counts and risk scores.
  - `entity_mentions`: Link table mapping every entity occurrence to its exact source line.
  - `slang_dictionary`: Confirmed and rejected evasive codewords inducted by officers.
  - `audit_log`: Cryptographic event ledger with SHA-256 entry hashes conforming to Section 63 BSA.
- **Deterministic Entity Extraction**:
  - Indian Phone Numbers: `+91`, `0`, or 10-digit formats starting with 6–9.
  - Indian UPI Handles (VPAs): `@okhdfcbank`, `@okaxis`, `@ybl`, `@paytm`, `@upi`, etc.
  - Cryptocurrency Wallets: TRON TRC-20 (`T...` 34 chars) and Bitcoin (`1...`, `3...`, `bc1...`).
  - Darknet Vendors: `@VendorName` extracted from darknet listing records.
  - Narcotics Keywords: Multi-lingual illicit terms (*chitta, white shoes, 4-mmc, mephedrone, ice tea, mdma, cocaine, heroin, charas, pudiya, tola, diazepam*).

### B. Forensic Backend Server (`server.py`)
- **Threaded Concurrency**: Built on `socketserver.ThreadingTCPServer` to handle simultaneous file uploads, streaming lines, and SLM queries.
- **Binary Multi-File Ingestion (`POST /api/upload`)**: Safely ingests heterogeneous file streams via `arrayBuffer()`, preserving binary and multi-byte UTF-8 encodings (tested on 463 KB darknet CSV dumps).
- **1-Click Demo Ingestion (`POST /api/load_demo_data`)**: Reads and parses 5 multi-source evidence datasets into SQLite in < 500ms:
  - `darknet_listings_sample.csv` (600 records)
  - `sample_telegram_export.json` (8 records)
  - `bank_statement_baseline.csv` (75 records)
  - `seized_paytm_mule_receipt.png` (8 records via Air-Gapped OCR)
  - `seized_telegram_chat_drop.png` (7 records via Air-Gapped OCR)
- **Air-Gapped OCR Engine (`ocr_worker.py`)**:
  - Direct integration with local system **Tesseract 5.5.2** (`/opt/homebrew/bin/tesseract`) with zero external cloud or Python image library dependencies.
  - TSV/line-level parsing extracting per-line bounding boxes and forensic confidence ratings.
  - Contextual classification recognizing `UPI_PAYMENT_RECEIPT` (Paytm, PhonePe, Google Pay) vs `ENCRYPTED_CHAT_SCREENSHOT` (Telegram, WhatsApp).
  - Speaker attribution extracting conversational usernames (`Karan`, `Desi_Plug`) from screenshot chat bubbles into forensic `sender_id`.
  - Serves original exhibits via `GET /api/evidence_image?file_id=...` with content-type preservation.
  - Reports OCR capabilities via `GET /api/ocr_status`.
- **SillyTavern-Style Model Discovery (`GET /api/llm/models?url=...`)**:
  - Pings `${serverUrl}/v1/models` (default `http://localhost:8080`, with presets for `8012` and `11434`).
  - Dynamically classifies detected model architectures (Liquid LFM, Google Gemma, Meta Llama, Alibaba Qwen, Microsoft Phi) and injects operational blurbs and throughput metrics.
- **Active Codeword Induction (`POST /api/extract_codeword`)**:
  - Uses targeted few-shot `/completion` calls (T=0.0, 8 max tokens) against local SLM to isolate disguised contraband nouns.
  - Includes a blacklist guardrail screening out routine payment terms (*USDT, UPI, GPay*).
  - Includes a fast deterministic heuristic fallback if the SLM port is temporarily offline.
- **Precinct Lexicon Governance (`POST /api/induct_codeword` & `POST /api/dismiss_codeword`)**:
  - Saves approved words into `slang_dictionary` in SQLite.
  - Logs immutable Section 63 BSA audit trail entries.

### C. Frontend Forensic Workbench (`index.html`, `app.js`, `styles.css`)
- **Step 1 (Case Intake)**: Real FIR and IO metadata capture with Belt and Police Station auto-formatting.
- **Step 2 (Media Intake)**:
  - Drag-and-drop file ingestion supporting multi-file selection including images (`.png`, `.jpg`, `.jpeg`, `.webp`).
  - Visual upload progress bar (`#upload-progress-container`) tracking live ingestion percentages.
  - Dynamic staged table (`#staged-evidence-tbody`) displaying authentic ingested files, `📸 AIR-GAPPED OCR` badges, and SHA-256 hashes.
  - Instant pre-staged dataset button (`autofillEvidenceFiles()`).
- **Step 3 (Inference Engine Configuration)**:
  - SillyTavern-style server URL input, presets (`8080`, `8012`, `11434`), and connection status badge (`🟢 Connected` / `🔴 Offline`).
  - Dynamic model select dropdown populated from live server.
  - Dynamic model capability blurb card.
- **Step 5 (Workbench Dashboard)**:
  - **Panel 1 (Left - Evidence Explorer)**: Dynamic file tabs with `📸` badges for screenshots; real SHA-256 display; dual view toggle (`[ 📄 OCR Stream ]` vs `[ 📸 Seized Screenshot Original ]`); image preview viewer with Section 63(4) cryptographic verification subtext; streaming raw record viewer with line numbers, OCR badges, and flag tags; real-time line search filter; instant `[ ＋ Ingest File ]` button.
  - **Panel 2 (Center - Triage Workbench)**: Dynamic cards for 40+ real entities (including screenshot entities like UPI `mule44@ybl` and drug slang `white shoes`, `ice tea`); risk scores; clickable `traceToSource(fileId, lineNum)` button automatically toggling text mode, jumping to, and highlighting source lines in Panel 1.
  - **Panel 3 (Right - Intelligence & Governance)**:
    - **Tab A (Link Graph)**: Dynamic SVG network topology generated from real entities and mentions.
    - **Tab B (Section 63 BSA)**: Live digital evidence certificate with SHA-256 hash chains.
    - **Tab C (Field Ops)**: 1-click PCR Patrol Van WhatsApp Alert generator and Case Diary (Zimni) exporter.
    - **Tab D (Codeword Induction Workbench)**: Unified copilot with live AI telemetry HUD (active core, latency, decode speed, surfaced count), scrolling audit console, real database candidates from `GET /api/candidates`, editable proposed noun cards, and Section 63 BSA induct/reject buttons.

---

## 3. Core REST API Reference

| Endpoint | Method | Params / Body | Description |
| :--- | :--- | :--- | :--- |
| `/api/cases` | `GET` | — | Returns list of all registered precinct cases with file and record totals. |
| `/api/cases/create` | `POST` | `{ case_id, fir_number, police_station, io_name, io_belt, category }` | Registers a case in SQLite for Section 63 BSA legal chain of custody. |
| `/api/cross_case_matches`| `GET` | `case_id` | Identifies matching targets (UPI, phones, wallets) across historical cases. |
| `/api/files` | `GET` | `case_id` | Returns list of all ingested evidence files with SHA-256, OCR types, and record counts. |
| `/api/file_records` | `GET` | `file_id`, `limit` | Streams actual records/lines for a file with forensic line numbers and tags. |
| `/api/evidence_image` | `GET` | `file_id` | Serves original seized evidence image exhibit for Section 63(4) BSA preview. |
| `/api/ocr_status` | `GET` | — | Returns local air-gapped OCR engine status (dots.ocr / Tesseract 5.5.2). |
| `/api/leads` | `GET` | `case_id` | Returns dynamic triage leads with `crossCaseHit` indicators and corroboration basis. |
| `/api/candidates` | `GET` | `case_id`, `file_id`, `limit` | Returns transactional evidence messages for codeword induction. |
| `/api/slang_dictionary` | `GET` | — | Returns confirmed inducted codewords from precinct database. |
| `/api/graph` | `GET` | `case_id` | Returns nodes and links for the interactive entity relationship graph. |
| `/api/search` | `GET` | `q`, `case_id`, `limit` | Runs SQLite FTS5 full-text search across all evidence records. |
| `/api/llm/models` | `GET` | `url` | Pings local inference server for available model slugs with architecture blurbs. |
| `/api/slm_status` | `GET` | — | Quick ping to check if local llama-server is online on default ports. |
| `/api/upload` | `POST` | `case_id`, `filename` (query), binary body | Ingests and parses an evidence file (or runs OCR on images) into SQLite; extracts entities. |
| `/api/load_demo_data` | `POST` | `case_id`, `type=default|adversarial` | Ingests pre-staged datasets or the adversarial stress corpus from disk. |
| `/api/extract_codeword` | `POST` | `{ message, context, server_url, model }` | SLM few-shot completion isolating disguised contraband nouns. |
| `/api/induct_codeword` | `POST` | `{ term, meaning, case_id, io_name }` | Commits an officer-verified codeword into `slang_dictionary` with SHA-256 hash. |
| `/api/dismiss_codeword` | `POST` | `{ term, reason, case_id, io_name }` | Dismisses a false positive candidate with BSA audit record. |

---

## 4. Adversarial Stress Testing & Verification

The repository includes a comprehensive adversarial stress test corpus and automated test suites:

### A. Adversarial Stress Corpus (`data/adversarial/`)
- `adversarial_whatsapp_hinglish.txt`: Heavily obfuscated chat threads using Hinglish and Punjabi phonetic substitutions (*chitta, white sneakers, sweet mithai, tola, peti, parcel*), split payments, and drop point coordinates (Aroma Hotel Sector 22, ISBT 43).
- `adversarial_darknet_listings.json`: PGP-signed synthetic Tor marketplace storefront listings for 4-MMC (mephedrone), LSD blotters, and pharma grade benzos with TRON USDT and Bitcoin escrow addresses.
- `adversarial_bank_structuring.csv`: AML evasion micro-deposits structured below reporting thresholds matching chat amounts and mule accounts.
- `adversarial_seized_chat_chit.png`: Dark-mode mobile chat screenshot with real timestamps and UPI handles for neural OCR stress testing.
- `adversarial_handwritten_chit.jpeg`: Authentic seized handwritten Hindi/English ledger exhibit.

### B. Running Automated Verification Suites
```bash
# 1. Run Adversarial Stress Test (Obfuscation recall & cross-case corroboration)
python3 tests/stress_test_adversarial.py

# 2. Run End-to-End Workbench API Integration Suite
python3 tests/test_api_workflow.py
```

The core architecture (SQLite, WAL mode, FTS5, OCR engine, SLM induction, dual-view exhibit UI) is **fully implemented and tested**. Agents working on new features should branch out from `main`:

---

### 🔹 FORK B: Advanced Force-Directed Graph & Syndicate Centrality
* **Branch Name:** `feature/advanced-network-graph`
* **Files to Modify:** `index.html` (Panel 3 Tab A), `app.js` (`renderNetworkGraph`)
* **Objective:** Upgrade the current lightweight SVG graph to a full interactive forensic intelligence network using Vis.js Network or Cytoscape.js (served locally, zero npm build).
* **Scope & Requirements:**
  1. **Visual Encoding**:
     - Red nodes: Darknet Vendors & Telegram Admins.
     - Amber diamonds: Mule Bank / UPI Accounts.
     - Purple hexagons: Crypto Wallets (TRC-20 USDT / BTC).
     - Blue pins: Physical Drop Locations (Sector 17, Sector 35, etc.).
  2. **Physics & Clustering**:
     - Force-directed physics layout with auto-stabilization.
     - Highlight clusters: clicking any node highlights its 1st- and 2nd-degree neighbors and dims the rest.
  3. **Syndicate Centrality Metric**:
     - Compute in-degree / out-degree centrality on the graph to automatically badge the likely "Kingpin / Coordinator" vs "Peripheral Mule".
  4. **Timeline Scrubber**:
     - Add a slider at the bottom of the graph to filter active connections chronologically across the investigation timeframe.

---

### 🔹 FORK C: Telecom CDR, IPDR & Tower Azimuth Geo-Correlator
* **Branch Name:** `feature/cdr-tower-correlator`
* **File to Create:** `cdr_analyser.py`
* **Objective:** Indian cyber crime cells receive raw Call Detail Records (CDR) and IP Detail Records (IPDR) CSV dumps from Airtel/Jio/Vi.
* **Scope & Requirements:**
  1. Implement `parse_cdr_csv(file_bytes, case_id)`:
     - Handles standard Indian telco CSV columns (`Calling_No`, `Called_No`, `Date`, `Time`, `Duration`, `First_Cell_ID`, `Last_Cell_ID`, `IMEI`, `IMSI`).
  2. Implement Tower Location Lookup:
     - Map Cell IDs to Chandigarh sectors (Sector 17, Sector 22, Sector 26, Sector 43, Aroma Hotel, Mohali Phase 7).
  3. Geo-Temporal Co-Location Matching:
     - Correlate dead-drop delivery timestamps from Telegram/Darknet chats with suspect phone presence at the same cell tower during that window.
     - Output high-confidence "Physical Co-Location" alerts in Panel 2.

---

### 🔹 FORK D: Court-Admissible PDF Dossier & Section 91 CrPC Notice Generator
* **Branch Name:** `feature/legal-dossier-pdf`
* **File to Create:** `legal_dossier.py`
* **Objective:** Evaluators and police officers want to print a formal court document ready for submission to the Judicial Magistrate.
* **Scope & Requirements:**
  1. Generate formal, clean PDF documents using Python standard library or `reportlab`:
     - **Exhibit A: Section 63(4) BSA Digital Evidence Certificate**: Includes hardware hash, algorithm specification (SHA-256), chain of custody, and digital sign-off block.
     - **Exhibit B: Section 91 CrPC Requisition Notice**: Pre-formatted statutory legal order addressed to Telecom Nodal Officers or Bank Branch Managers directing immediate freeze/preservation of target accounts.
  2. Embed a verifiable cryptographic QR Code containing the SHA-256 hash digest of the case files and zimni entry.
  3. Connect to a frontend `[ 🖨️ Export Court PDF Dossier ]` button in the dashboard.

---

### 🔹 FORK E: One-Click Offline Inference Sidecar & Packaging Script
* **Branch Name:** `feature/offline-model-sidecar`
* **File to Create:** `run_sidecar.sh`
* **Objective:** Provide a foolproof 1-command startup script for police demonstration laptops.
* **Scope & Requirements:**
  1. Shell script that checks for local `llama-server` or `ollama`.
  2. If `llama-server` is installed, launches:
     ```bash
     llama-server -m models/LFM2.5-8B-A1B-Q4_0.gguf --port 8080 -ngl 99 -c 4096 --host 127.0.0.1
     ```
  3. Automatically starts `python3 server.py` on port 8000 and opens the browser.
  4. Manages graceful shutdown on `Ctrl+C`.

---

## 5. Repository File Tree

```
├── index.html                  # Main forensic dashboard UI (Steps 1-5, Panel 1-3, Dual Exhibit Viewer)
├── styles.css                  # High-density dark-mode forensic styling & exhibit image styles
├── app.js                      # Core frontend controller, WebSocket/REST API client, OCR mode toggle
├── server.py                   # Threaded Python HTTP forensic server (OCR & image endpoints)
├── storage.py                  # SQLite WAL database engine, FTS5 search, entity extractor
├── ocr_worker.py               # Air-gapped Tesseract 5.5.2 OCR engine & screenshot classifier
├── data/
│   ├── case_evidence.db        # Active SQLite database in WAL mode
│   ├── evidence_images/        # Seized evidence image store (Section 63(4) BSA exhibits)
│   ├── processed/
│   │   ├── darknet_listings_sample.csv  # 600 authentic darknet illicit marketplace listings
│   │   └── bank_statement_baseline.csv  # 75 authentic banking & UPI transaction records
│   └── raw/
│       ├── sample_telegram_export.json  # Multi-party encrypted chat negotiation dump
│       ├── seized_paytm_mule_receipt.png # Seized Paytm payment receipt exhibit
│       └── seized_telegram_chat_drop.png # Seized Telegram chat drop exhibit
├── README.md                   # Master documentation and AI agent briefing
└── .gitignore                  # Git hygiene rules
```

---

## 6. Ground Rules for AI Agents Collaborating on Forks

1. **Air-Gap Law:** Never import or make network requests to external commercial cloud APIs (OpenAI, Anthropic, Google Cloud, HuggingFace Hub). Everything must resolve on `localhost` or standard library.
2. **Database Schema Integrity:** Always query through `storage.get_db()`. Do not alter table primary keys or delete columns from `evidence_files` and `evidence_records` to prevent breaking existing dashboard panels.
3. **Trace-to-Source Rule:** Any new intelligence lead generated must preserve its source citation (`file_id` and `line_number`) so officers can click `traceToSource(fileId, lineNum)` to see the raw verified evidence.
4. **No NPM / Build Step Required:** Keep JavaScript vanilla ES6+ so the platform runs directly in any modern browser without Webpack, Vite, or npm installs.
