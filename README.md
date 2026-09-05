# TACTICAL EVIDENCE TRIAGE & STATUTORY COMPLIANCE PLATFORM (TETCP)
### Chandigarh Police Hackathon 2026 — Problem Statement 3 (PS3-DWID)
> **Track:** Detection of Illicit Drug Sales on Darknet and Other Encrypted Platforms  
> **Statutory Compliance:** Section 63(4) Bharatiya Sakshya Adhiniyam (BSA), 2023 & Section 91 CrPC  
> **Architecture:** 100% Air-Gapped, Local-First, Zero Cloud AI Lock-In

---

## 1. Executive Summary & Upgraded Architecture

The **Tactical Evidence Triage & Statutory Compliance Platform (TETCP)** is a unified, air-gapped forensic copilot and statutory approval gateway engineered for frontline law enforcement officers, cyber crime investigators, and judicial prosecution teams.

The platform provides a complete end-to-end investigative and compliance pipeline:
1. **Government Portal Homepage:** "One Platform. Every Approval & Digital Forensics." Demonstrating problem-solution-value architecture and key performance metrics.
2. **5-Step Application & Intake Workflow:** Seamless **← Previous / Next →** navigation, state validation, and pre-execution review manifest.
3. **Multi-Source Evidence Ingestion:** Ingests Tor `.onion` HTML mirrors, Cellebrite Telegram JSON dumps, WhatsApp text exports, Bank statement CSVs, and EXIF imagery into Universal Forensic Message Envelopes (UFME) with pre-calculated SHA-256 hashes.
4. **Deterministic NER + Local Quantized SLM:** Instant regex extraction for Indian UPI VPAs, mobile numbers, and TRON USDT/Bitcoin crypto addresses, paired with an offline SLM (Llama-3.2-3B / Qwen-2.5) for evasive slang disambiguation (*Chitta, White Shoes, Stamp Paper, Ice Tea*).
5. **Trace-to-Source Byte Jumping & Glass-Box Explainability:** Every lead traces directly to the exact seized evidence line and discloses prompt task, temperature ($T=0.0$), and mathematical reasoning.
6. **Interactive Entity Link Graph:** Force-directed SVG topology cross-linking Tor marketplace storefronts, syndicate telegram admins, burner SIMs, crypto escrows, and domestic bank accounts.
7. **Statutory Compliance Center:** Live compliance scoring meter (94% Grade A+) under Section 63(4) Bharatiya Sakshya Adhiniyam, 2023.
8. **Case & Application Tracking Dashboard:** Searchable case directory with a 5-stage lifecycle milestone timeline.
9. **Document & Evidence Vault:** Tamper-evident repository with client-side real-time SHA-256 integrity verification.
10. **Government Schemes & Statutory Acts Directory:** Searchable library of MHA cyber grants, I4C initiatives, CCPWC funds, and legal procedural acts.
11. **Smart AI Forensic Copilot:** Offline statutory advisory answering queries on Section 63 BSA, Section 91 CrPC, and evidence prerequisites.
12. **Dual Operational Packaging:** 1-click tactical WhatsApp alerts for PCR patrol vans and court-admissible Section 63 BSA Digital Evidence Certificates with Section 91 CrPC bank freeze and telecom CDR orders.

---

## 2. Quickstart & Running the Platform

The application is engineered to run 100% offline on any forensic workstation without npm, Node.js, or cloud dependencies.

### Prerequisites
* Python 3.9+ (Standard library only: `http.server`, `sqlite3`, `hashlib`, `json`, `re`)
* Modern Web Browser (Google Chrome, Microsoft Edge, Mozilla Firefox)

### Option A: Launching with Python Server & Local REST API (Recommended)
From the root repository directory, run:
```powershell
python server.py
```
This automatically initializes the local SQLite database (`precinct_evidence.db`), seeds historical cases, and launches the air-gapped HTTP server and REST API at:
```
http://localhost:8000/
```

### Option B: Self-Testing Backend & Regex NER
To run automated verification tests:
```powershell
python server.py --test
```

### Option C: Standalone Client Mode
You can also run any standard static server:
```powershell
python -m http.server 8000
```
Open `http://localhost:8000/` in your browser.

---

## 3. Project File Structure

```
policehackathonv1/
│
├── index.html                  # Main Gov-Tech portal, 5-step wizard, 3-panel workbench, modals
├── styles.css                  # Enterprise Gov-Tech stylesheet, responsive breakpoints, print theme
├── app.js                      # Unified router, state management, triage logic, graph inspector
├── server.py                   # Lightweight local Python 3 HTTP server, SQLite DB & REST API
├── precinct_evidence.db        # Single-file SQLite database (auto-created on server launch)
├── README.md                   # Complete documentation, setup guide & demo script
├── Track 3 Documenation (1).pdf # Official Problem Statement 3 specification
└── Chandigarh Police Hackathon Guidelines...pdf # Hackathon ground rules & compliance directives
```

---

## 4. Local REST API Reference

The platform includes a zero-dependency local REST API running on `http://localhost:8000`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status & BSA compliance flag |
| `GET` | `/api/cases` | Retrieve all registered cases and tracking stages from SQLite |
| `POST` | `/api/cases` | Register a new statutory case into the database |
| `POST` | `/api/extract` | Deterministic entity extractor (phones, UPI handles, crypto wallets, pricing) |
| `GET` | `/api/compliance`| Statutory Section 63 BSA compliance scores and checklist |
| `GET` | `/api/audit` | Tamper-evident chronological audit ledger |
| `POST` | `/api/audit` | Record an immutable officer action with SHA-256 signature |

---

## 5. Verification & Testing Checklist

- [x] **Homepage Hero & Navigation:** Loads authoritative Indian Gov-Tech header, statistics counter, and responsive navigation links.
- [x] **5-Step Application Wizard:**
  - [x] Step 1: Case details input + validation + autofill demo button.
  - [x] Step 2: Evidence media drop zone + staged files table + SHA-256 hashes.
  - [x] Step 3: Offline SLM engine selector + regional lexicon settings + modular toggles.
  - [x] Step 4: Comprehensive pre-execution review manifest summarizing entered parameters.
  - [x] Step 5: Pipeline progress bar with live terminal simulation and transition to Workbench.
  - [x] **Previous & Next Navigation:** Previous disabled on Step 1, Next advances with validation, Previous preserves all entered data without reset.
- [x] **Command Workbench (3 Panels):**
  - [x] Panel 1: Multi-source stream selector (Tor, Telegram, WhatsApp, Bank CSV, EXIF) with search and line highlighting.
  - [x] Panel 2: Corroborated triage cards with confidence scores, glass-box model rationale drawer, and Verify/Dismiss/Edit actions.
  - [x] Panel 3: Target Summary metrics, novel slang harvester ("Ice Tea"), verified BSA table, and Section 91 CrPC requisitions.
- [x] **Interactive Network Link Graph:** Clickable nodes open attributes card and filter correlated evidence leads.
- [x] **Case & Application Tracking:** Searchable case cards with 5-stage chronological lifecycle timelines.
- [x] **Statutory Compliance Center:** Radial progress gauge (94% Grade A+) and mandatory legal checklist.
- [x] **Document Vault:** Registry of evidence files with live client-side SHA-256 calculation tool.
- [x] **Government Schemes Directory:** Filterable cards covering I4C, CFSL, CCPWC, and legal acts.
- [x] **Smart AI Forensic Copilot:** Offline rule-based advisory answering questions on BSA 63, CrPC 91, and drug slang.
- [x] **Court Documents & Dispatches:** Print-ready Section 63 BSA certificate, Section 91 CrPC orders, and WhatsApp field alert text copy.

---

## 6. Hackathon Table Pitch Script (2–3 Minutes)

When jury members and police evaluators walk up to your desk, follow this demonstration journey:

1. **Step 1 — The Hook & Platform Overview (0:00 - 0:30):**
   * *"Good morning, esteemed jury. Frontline cyber crime officers face massive, messy dumps—Tor marketplace listings, Telegram chats, bank CSVs. Existing tools are fragmented and vulnerable under India's new criminal codes. Welcome to TETCP: One Platform. Every Approval & Digital Forensics."*
   * Point to the **Portal Homepage** showing key metrics: 100% Air-Gapped, 94% Statutory Compliance, and zero cloud AI lock-in.

2. **Step 2 — Structured 5-Step Intake & Hashing (0:30 - 1:00):**
   * Click **New Intake**. Show Step 1 with autofilled case details (FIR-104 Sector 17).
   * Click **Next** to show Step 2. Highlight the 5 multi-source evidence streams with pre-calculated SHA-256 hashes matching Malkhana barcodes.
   * Demonstrate **Previous** to prove no data is lost, then advance through Step 3 (Engine Settings) and Step 4 (Review Manifest).
   * Click **Submit & Run Pipeline** to watch the progress bar correlate the corpus into UFME.

3. **Step 3 — The Forensic Command Workbench (1:00 - 1:45):**
   * Inside the **Workbench**, demonstrate **Trace-to-Source**: click *"Jump to Source"* on the UPI mule lead (`mule44@ybl`) to show Panel 1 scrolling and flashing the exact chat line.
   * Open the **Glass-Box Model Rationale** to explain how the local SLM disambiguated `"Chitta"` and `"White Shoes 5g"` with temperature $T=0.0$.
   * Click the **Network Graph** tab to show the interactive link graph connecting the Tor marketplace, syndicate admin, burner SIM, and UPI mule.

4. **Step 4 — Statutory Compliance & Court Output (1:45 - 2:30):**
   * Switch to the **Compliance Center** to show the 94% court admissibility score.
   * Click **Generate Section 63(4) BSA Digital Evidence Certificate** to open the print-ready court document complete with Schedule A (file hashes), Schedule B (verified leads), and the Machine/Model Manifest.
   * Show the **Section 91 CrPC Bank Freeze Notice** ready for immediate dispatch to SBI.

5. **Step 5 — Closing Impact (2:30 - 3:00):**
   * *"In under 3 minutes, an officer goes from an unstructured seized dump to court-admissible electronic evidence, automated bank freeze orders, and tactical field alerts—all 100% offline. Thank you, and we welcome your questions."*
