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
Run the forensic server from the repository root:
```bash
python3 server.py
```
Open your browser to:
```
http://localhost:8000/
```

### Instant Verification
1. On Step 1, click **"Proceed to Evidence Media Intake ➔"**.
2. On Step 2, click **"⚡ Load Pre-Staged Datasets"** (instantly ingests 683 real records across 3 multi-source forensic datasets into SQLite).
3. On Step 3, the model discovery engine will automatically ping your local server, populate model slugs, and show capability blurbs. Click **"⚡ Start Forensic Pipeline & Triage ➔"**.
4. The workbench will load with live dynamic tabs, streaming raw database records, 31+ real triage leads, dynamic network graph, and active codeword induction.

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
- **1-Click Demo Ingestion (`POST /api/load_demo_data`)**: Reads and parses `data/processed/darknet_listings_sample.csv` (600 lines), `data/raw/sample_telegram_export.json` (8 lines), and `data/processed/bank_statement_baseline.csv` (75 lines) into SQLite in < 500ms.
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
  - Drag-and-drop file ingestion supporting multi-file selection.
  - Visual upload progress bar (`#upload-progress-container`) tracking live ingestion percentages.
  - Dynamic staged table (`#staged-evidence-tbody`) displaying authentic ingested files and SHA-256 hashes.
  - Instant pre-staged dataset button (`autofillEvidenceFiles()`).
- **Step 3 (Inference Engine Configuration)**:
  - SillyTavern-style server URL input, presets (`8080`, `8012`, `11434`), and connection status badge (`🟢 Connected` / `🔴 Offline`).
  - Dynamic model select dropdown populated from live server.
  - Dynamic model capability blurb card.
- **Step 5 (Workbench Dashboard)**:
  - **Panel 1 (Left - Evidence Explorer)**: Dynamic file tabs generated from database; real SHA-256 display; streaming raw record viewer with line numbers and flag tags; real-time line search filter; instant `[ ＋ Ingest File ]` button.
  - **Panel 2 (Center - Triage Workbench)**: Dynamic cards for 31+ real entities; risk scores; clickable `traceToSource(fileId, lineNum)` button jumping and highlighting source lines in Panel 1.
  - **Panel 3 (Right - Intelligence & Governance)**:
    - **Tab A (Link Graph)**: Dynamic SVG network topology generated from real entities and mentions.
    - **Tab B (Section 63 BSA)**: Live digital evidence certificate with SHA-256 hash chains.
    - **Tab C (Field Ops)**: 1-click PCR Patrol Van WhatsApp Alert generator and Case Diary (Zimni) exporter.
    - **Tab D (Codeword Induction Workbench)**: Unified copilot with live AI telemetry HUD (active core, latency, decode speed, surfaced count), scrolling audit console, real database candidates from `GET /api/candidates`, editable proposed noun cards, and Section 63 BSA induct/reject buttons.

---

## 3. Core REST API Reference

| Endpoint | Method | Params / Body | Description |
| :--- | :--- | :--- | :--- |
| `/api/files` | `GET` | `case_id` | Returns list of all ingested evidence files with SHA-256 and record counts. |
| `/api/file_records` | `GET` | `file_id`, `limit` | Streams actual records/lines for a file with forensic line numbers and tags. |
| `/api/leads` | `GET` | `case_id` | Returns dynamic triage leads generated from real extracted entities. |
| `/api/candidates` | `GET` | `case_id`, `limit` | Returns transactional evidence messages for codeword induction. |
| `/api/slang_dictionary` | `GET` | — | Returns confirmed inducted codewords from precinct database. |
| `/api/graph` | `GET` | `case_id` | Returns nodes and links for the interactive entity relationship graph. |
| `/api/search` | `GET` | `q`, `case_id`, `limit` | Runs SQLite FTS5 full-text search across all evidence records. |
| `/api/llm/models` | `GET` | `url` | Pings local inference server for available model slugs with architecture blurbs. |
| `/api/slm_status` | `GET` | — | Quick ping to check if local llama-server is online on default ports. |
| `/api/upload` | `POST` | `case_id`, `filename` (query), binary body | Ingests and parses an evidence file into SQLite; extracts entities. |
| `/api/load_demo_data` | `POST` | `case_id` | Ingests authentic Darknet, Telegram, and Bank statement samples from disk. |
| `/api/extract_codeword` | `POST` | `{ message, context, server_url, model }` | SLM few-shot completion isolating disguised contraband nouns. |
| `/api/induct_codeword` | `POST` | `{ term, meaning, case_id, io_name }` | Commits an officer-verified codeword into `slang_dictionary` with BSA audit. |
| `/api/dismiss_codeword` | `POST` | `{ term, reason, case_id, io_name }` | Logs candidate rejection in the Section 63 BSA audit log. |

---

## 4. Work Left to Implement: Next Modules for AI Agents & Forks

Other AI agents building in their own forks or feature branches should focus on the following concrete extensions. **The core architecture, database schema, and REST endpoints are already in place—build your modules to plug directly into this backbone:**

```
                               ┌────────────────────────┐
                               │     MAIN PIPELINE      │
                               │ server.py + storage.py │
                               └───────────┬────────────┘
         ┌──────────────────┬──────────────┼──────────────┬──────────────────┐
         ▼                  ▼              ▼              ▼                  ▼
   [FORK A: OCR]      [FORK B: GRAPH] [FORK C: CDR] [FORK D: DOSSIER] [FORK E: SIDECAR]
   Screenshot OCR     Force-Directed   Tower Azimuth  Court PDF & QR   Offline llama.cpp
   Receipt Extractor  Timeline Physics Geo-Fencing    Sec 91 Notices   Launcher Script
```

---

### 🔹 FORK A: Offline OCR & Seized Screenshot Harvester
* **Branch Name:** `feature/offline-ocr-worker`
* **File to Create:** `ocr_worker.py`
* **Objective:** Frontline police seize screenshots of WhatsApp chats, Telegram channels, and UPI payment receipts (Paytm/PhonePe/Google Pay).
* **Scope & Requirements:**
  1. Use standard library or local lightweight OCR (`pytesseract` or `easyocr` or `surya-ocr`).
  2. Implement `process_evidence_image(image_path_or_bytes, case_id)`:
     - Pre-processes image (greyscale, contrast thresholding).
     - Extracts text lines with approximate bounding boxes.
     - Parses detected UPI transaction IDs, transaction amounts (₹), timestamps, and mobile numbers.
  3. Wire directly into `storage.parse_and_ingest_file(case_id, filename, text_content.encode())` so screenshots appear seamlessly in Panel 1 as an ingested evidence stream.

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
├── index.html                  # Main forensic dashboard UI (Steps 1-5, Panel 1-3)
├── styles.css                  # High-density dark-mode forensic styling
├── app.js                      # Core frontend controller, WebSocket/REST API client, state
├── server.py                   # Threaded Python HTTP forensic server (zero dependencies)
├── storage.py                  # SQLite WAL database engine, FTS5 search, entity extractor
├── codeword_experiment.html    # (Reference only - features merged into View D)
├── data/
│   ├── case_evidence.db        # Active SQLite database in WAL mode
│   ├── processed/
│   │   ├── darknet_listings_sample.csv  # 600 authentic darknet illicit marketplace listings
│   │   └── bank_statement_baseline.csv  # 75 authentic banking & UPI transaction records
│   └── raw/
│       ├── sample_telegram_export.json  # Multi-party encrypted chat negotiation dump
│       └── drug_listings.csv            # Reference raw listings corpus
├── README.md                   # This master documentation and AI agent briefing
└── .gitignore                  # Git hygiene rules
```

---

## 6. Ground Rules for AI Agents Collaborating on Forks

1. **Air-Gap Law:** Never import or make network requests to external commercial cloud APIs (OpenAI, Anthropic, Google Cloud, HuggingFace Hub). Everything must resolve on `localhost` or standard library.
2. **Database Schema Integrity:** Always query through `storage.get_db()`. Do not alter table primary keys or delete columns from `evidence_files` and `evidence_records` to prevent breaking existing dashboard panels.
3. **Trace-to-Source Rule:** Any new intelligence lead generated must preserve its source citation (`file_id` and `line_number`) so officers can click `traceToSource(fileId, lineNum)` to see the raw verified evidence.
4. **No NPM / Build Step Required:** Keep JavaScript vanilla ES6+ so the platform runs directly in any modern browser without Webpack, Vite, or npm installs.
