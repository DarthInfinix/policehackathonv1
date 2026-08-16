# CHANDIGARH POLICE HACKATHON 2026: MASTER STRATEGY, DOMAIN SPECIFICATIONS & ARCHITECTURAL BLUEPRINT

> **Document Classification:** Comprehensive Briefing & Cross-Agent System Context  
> **Problem Statement:** Track 3 (Problem Statement 3) — *Development of a Platform for Detection of Illicit Drug Sales on Darknet and Other Encrypted Platforms*  
> **Organizers:** Chandigarh Police in collaboration with UIET (Panjab University) & PEC (Punjab Engineering College)  
> **Submission Deadline:** 20 August 2026 (Round 1: Pitch Deck PPT + 2–3 Minute Demonstration Video)  
> **Live Prototype Reference:** `http://localhost:8080` (Local Air-Gapped Forensic Workbench)

---

## 1. HACKATHON BLUEPRINT & OFFICIAL SPECIFICATIONS

### 1.1 Key Links & Deliverables
* **Official Problem Statement:** *"Development of a Platform for Detection of Illicit Drug Sales on Darknet and Other Encrypted Platforms"*
* **Official PPT Template:** `https://tinyurl.com/chdpolicehackathon-ppt`
* **Official Submission Form:** `https://docs.google.com/forms/d/e/1FAIpQLSd26gxPTZt7xRVPOfsi3s_Tj21P5gQN0Kt5E3CZ1bGUzA9lLA/viewform?usp=header`
* **Round 1 Deliverables:** 
  1. Pitch Deck following official slide headers.
  2. 2-to-3 minute video demonstration of working prototype.

### 1.2 The Official 10-Point Technical Specifications (From Released PDF)
The organizing committee released a formal 4-page specification document outlining 10 required system capabilities and visual figures showing Tor Browser, Torch search engine, and Darknet drug marketplace listings (DMT, 4-MMC, Telegram storefronts):

```
┌────┬──────────────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ #  │ OFFICIAL SPECIFICATION           │ OPERATIONAL MEANING FOR LEAs                                           │
├────┼──────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 1  │ Multi-Source Data Collection     │ Ingest Tor .onion listings, public forums, blockchain, phone dumps.    │
│ 2  │ Intelligent Entity Correlation   │ Link usernames, crypto wallets, emails, phone numbers, mule accounts.  │
│ 3  │ Suspicious Activity Detection    │ Auto-detect drug keywords, high-risk listings, surrogate slang codes.  │
│ 4  │ Interactive Intelligence Dash    │ Centralized UI for alerts, trends, line search, and case management.   │
│ 5  │ Network Visualization            │ Visual link graph (Marketplace ➔ Telegram Admin ➔ Crypto ➔ Mule A/c).   │
│ 6  │ Automated Alert Generation       │ Priority field alerts for high-risk transactions and dead-drops.       │
│ 7  │ Search & Investigation Support   │ Fast multi-filter search across aliases, wallet addresses, and text.   │
│ 8  │ Reporting & Evidence Management  │ Legally compliant audit logs and court-admissible evidence dossiers.   │
│ 9  │ Security & Access Control        │ Role-based access, air-gapped machine manifests, immutable hash logs.  │
│ 10 │ Scalability & Modularity         │ Extensible offline pipeline with zero cloud lock-in.                   │
└────┴──────────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

---

## 2. THE "METAGAME" & COMPETITOR THREAT MODELING

### 2.1 Silicon Valley vs. Indian Police Hackathons (The "Palantir Trap")
* **The Trap:** When 2nd-year student teams read the problem statement, they attempt to build **Palantir Gotham + Chainalysis + NSA PRISM in 5 slides**. They promise to "hack WhatsApp 256-bit AES encryption in real-time" or "track all darknet servers via satellite".
* **The Reality:** Senior IPS officers and PEC/UIET computer science professors judge this hackathon. They screen 1,000+ entries in 5 days (**90 to 180 seconds per pitch deck**). They instantly disqualify naive sci-fi claims and cloud API wrappers (OpenAI/Claude) that violate Indian police data sovereignty.
* **Our Winning Wedge:** We built the **"Last-Mile Forensic Triage Bridge"** for the frontline Investigating Officer (IO). Instead of pretending to be a $100M defense contractor, we solve the exact 6-hour forensic logjam an officer faces when seizing phone exports and bank statements in Sector 17.

### 2.2 The Real-World Drug Trafficking Topology in Chandigarh Tricity
Why the obsession with Tor/Darknet if retail dealing is on clearweb?

```
 ┌────────────────────────────────────────────────────────┐
 │ TIER 1: WHOLESALE SOURCING (Tor / Darknet .onion)      │
 │ • Bulk synthetic psychoactives (LSD blotters, 4-MMC,   │
 │   MDMA crystals, DMT) imported from Europe/China.      │
 │ • Escrow payments via Bitcoin / TRON USDT.             │
 └───────────────────────────┬────────────────────────────┘
                             │ (Postal parcel consignments to Delhi/Punjab)
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │ TIER 2: LOCAL TRICITY DISTRIBUTION (Clearweb/Telegram) │
 │ • Broken into retail 'Pudiyas' (~1g packets).          │
 │ • Sold to college youth via Telegram, WhatsApp, Signal.│
 │ • Paid via domestic UPI Mules & Cash on Dead-Drops.    │
 └───────────────────────────┬────────────────────────────┘
                             ▼
 [ OUR PLATFORM: THE CORRELATION BRIDGE ]
 Cross-correlates Tor marketplace vendor PGP/listings with 
 local Telegram distributors (@chd_plug) and domestic UPI mule bank accounts.
```

### 2.3 Evaluation on Sanitized Synthetic Benchmarks vs. Live Tor Scrapes
* **Critical Rule:** Never attempt live scraping of active darknet sites during student hackathons. It creates legal, safety, and network liability, and sites frequently go offline.
* **The Framing:** We evaluate our pipeline on a **curated, sanitized benchmark dataset of darknet marketplace archives and synthetic forensic chat logs** modeled on Narcotics Control Bureau (NCB) and Europol case typologies.

---

## 3. THE 5 FATAL CRITIQUES & OUR ARCHITECTURAL DEFENSES

We audited the core idea against the toughest questions from judges, defense attorneys, and senior police officers:

```
┌──────────────────────────────────────┬──────────────────────────────────────────┬─────────────────────────────────────────┐
│ FATAL CRITIQUE                       │ WHY IT WOULD DISQUALIFY A TEAM           │ OUR ARCHITECTURAL DEFENSE               │
├──────────────────────────────────────┼──────────────────────────────────────────┼─────────────────────────────────────────┤
│ 1. Format Brittleness                │ Real Cellebrite / Magnet exports are     │ Universal Forensic Message Envelope     │
│    (Cellebrite / Oxygen Realities)   │ messy XML/SQLite, not clean JSON.        │ (UFME) normalization pipeline.          │
├──────────────────────────────────────┼──────────────────────────────────────────┼─────────────────────────────────────────┤
│ 2. Static Lexicon & Slang Drift      │ Drug slang evolves weekly; static        │ Antifragile In-Context Induction Engine │
│    (Evolving Jargon)                 │ keyword lists break immediately.         │ (discovers novel codes like 'Ice Tea'). │
├──────────────────────────────────────┼──────────────────────────────────────────┼─────────────────────────────────────────┤
│ 3. Judicial Evidentiary Scrutiny     │ Section 63 BSA 2023 requires proving     │ Forensic Machine Manifest (Schedule C), │
│    (BSA Section 63 Attack in Court)  │ deterministic parameters and hashes.     │ SHA-256 Checksums, Fixed Seed & Temp 0.0│
├──────────────────────────────────────┼──────────────────────────────────────────┼─────────────────────────────────────────┤
│ 4. Post-Triage Inaction              │ Finding a UPI is useless if an officer   │ 1-Click Section 91 CrPC Bank Freezing & │
│    (Paperwork & Freezing Drag)       │ spends 2 hours typing legal notices.     │ Telecom CDR Preservation Orders.        │
├──────────────────────────────────────┼──────────────────────────────────────────┼─────────────────────────────────────────┤
│ 5. Malicious Framing & False Positives│ Adversarial users spamming enemy phone   │ Multi-Factor Corroboration Matrix       │
│    (Single-Source Framing Risk)      │ numbers in public drug chats.            │ (Chat + Bank CSV cross-match).          │
└──────────────────────────────────────┴──────────────────────────────────────────┴─────────────────────────────────────────┘
```

---

## 4. KEY TECHNICAL INNOVATIONS & ARCHITECTURAL BREAKTHROUGHS

### 4.1 Legal Grounding: Section 63(4) Bharatiya Sakshya Adhiniyam (BSA), 2023
* **The Legal Shift:** On July 1, 2024, the Indian Evidence Act of 1872 was repealed. **Section 65B is replaced by Section 63(4) of the BSA, 2023.**
* **The Forensic Machine Manifest:** To defend SLM-assisted triage in the Sector 43 District Court, our certificate documents:
  - Host OS and kernel version.
  - Model Name & Checksum: `Llama-3.2-3B-Instruct (4-bit GGUF, SHA-256 Checksum)`.
  - Deterministic Hyperparameters: `Temperature = 0.0`, `Seed = 42`, `Top-P = 1.0`.
  - Dual Attestation: Signed by both the Investigating Officer (IO) and Cyber Lab Technical Examiner.

### 4.2 The Antifragile Active Induction Engine (Pattern Discovery Beyond Words)
When criminals invent new slang or shift payment rails, the system does not break—it gets stronger:

```
  Raw Seized Chat Dump ➔ [ Syntactic Frame Extraction ] ➔ [ Anomaly Clustering ] ➔ [ IO Promotion ] ➔ [ Persistent Lexicon ]
```

1. **Syntactic Slot Framing:** The model looks for the universal transaction frame:  
   $$\text{Frame} = [\text{Quantity / Unit}] + [\mathbf{UNKNOWN\_NOUN}] + [\text{Numerical Price (INR)}] + [\text{Dead-Drop Landmark}]$$
   * Example: *"Bhai 2 bottle **Ice Tea** bhej do 1500 mein, sector 17 fountain pe"*
2. **Frequency Thresholding:** If *"Ice Tea"* appears $\ge 3$ times across independent users in commodity slots, it is flagged as an **Emerging Codeword Candidate (Confidence: 89%)**.
3. **Human-in-the-Loop Promotion:** The IO clicks `[✓ Approve & Add to Lexicon]`. It is permanently appended to `lexicon.json` on disk and instantly loaded into the SLM prompt context for all future cases.
4. **Extensions Beyond Slang:**
   - **Voucher Rail Induction:** Discovers Amazon Gift Card voucher formats (`EGV-[A-Z0-9]{12}`) when dealers evade UPI.
   - **Micro-Landmark Atlas:** Clusters hyper-local informal dead-drops (*"Pillar 14 ISBT"*, *"transformer ke piche"*).
   - **Platform Migration Vectors:** Extracts `session://`, `simplex.chat/`, and Matrix lifeboat links when Telegram channels get banned.

### 4.3 Multi-Tier Tactical Export (The "Munshi & PCR Van" Reality)
Officers in the field cannot read 10-page PDFs. The platform provides a 3-tier export model:
1. **`[📲 Copy WhatsApp Field Dispatch]`**: 1-click formatted operational alert ready to paste into police WhatsApp/Signal coordination channels for immediate PCR patrolling and ATM stakeouts.
2. **`[📝 Copy Munshi Case Diary (Zimni) Text]`**: Clean, formal plaintext for the Station Steno/Munshi to paste straight into the official *Zimni* in Microsoft Word.
3. **`[⚖️ Generate Section 63 BSA Court Certificate]`**: Formal printable legal affidavit for the Judicial Magistrate.

### 4.4 Glass-Box "Trace-to-Source" Verification
Every extracted token has a `[Jump to Source ↗]` button. Clicking it instantly jumps to, centers, and flashes the exact raw line and byte offset in the seized file, ensuring zero black-box hallucinations.

---

## 5. COMPLETE APPLICATION USER FLOW & DEMO SCRIPT

The live application (`http://localhost:8080`) implements a 5-step narrative flow:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌──────────────────────┐
│ STEP 1          │ ──> │ STEP 2          │ ──> │ STEP 3          │ ──> │ STEP 4          │ ──> │ STEP 5               │
│ Officer Intake  │     │ Media Upload    │     │ Engine Setup    │     │ Pipeline Logs   │     │ Clean Command Center │
│ (FIR, PS, IO ID)│     │ (SHA-256 Hashes)│     │ (Offline SLM)   │     │ (3-Sec Parse)   │     │ (Full Officer Control│
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘     └──────────────────────┘
```

1. **Step 1: Case Registration & Officer Intake**
   - Fields: FIR No., Police Station, IO Name, Belt No., Statutory Sections.
   - *Demo Button:* `[⚡ Autofill Demo Case (FIR-104 Sector 17)]`.
2. **Step 2: Seized Media Ingestion & Hashing**
   - Ingests Telegram dump, WhatsApp raw export, SBI statement CSV, drop-zone photo.
   - *Demo Button:* `[⚡ Load Seized Case Files (4 Mock Evidence Items)]` stages files and calculates live SHA-256 hashes.
3. **Step 3: Inference Engine & Modality Settings**
   - Pre-selects offline `Llama-3.2-3B-Instruct (Local 4-bit GGUF, T=0.0)`.
   - Selects regional lexicon: `Chandigarh Tricity NDPS (Active)`.
4. **Step 4: Realistic Forensic Ingestion Pipeline (Animated Terminal)**
   - 3-second animated execution logs showing UFME normalization, SHA-256 verification, Regex parsing, local SLM inference, and cross-corroboration.
5. **Step 5: Clean, Officer-Controlled Command Center**
   - **Panel 1:** Raw Evidence Line Explorer with live search.
   - **Panel 2:** Corroborated Triage with Anti-Framing Badges (`95% High Corroboration` vs `45% Uncorroborated`) and `[Jump to Source ↗]`.
   - **Panel 3:** Emerging Slang Harvester (`"Ice Tea"` approval), WhatsApp Field Dispatch, Section 91 CrPC Bank/CDR notices, and 24-hr Activity Heatmap.

---

## 6. ROUND 1 SUBMISSION PITCH & TEAM ALLOCATION

### 6.1 3-Minute Video Demonstration Script
* **00:00 – 00:30 (The Problem & Scope):** Explain the dual reality—Tor darknet is used for wholesale synthetic imports, while local retail delivery runs on Telegram and UPI mules. Introduce the 6-hour forensic bottleneck.
* **00:30 – 01:45 (Live Software Walkthrough):** 
  - Show Step 1 to Step 4 onboarding in 15 seconds.
  - Show the Command Center: Trace-to-Source line jumping, anti-framing bank credit corroboration, approving `"Ice Tea"` in the Harvester, and generating the 1-click WhatsApp PCR dispatch.
* **01:45 – 02:30 (Legal & Technical Defensibility):** Open the Section 63 BSA Court Certificate modal, showing the Machine Manifest, SHA-256 checksums, and dual IO/Examiner attestation.
* **02:30 – 03:00 (Conclusion):** Reiterate the air-gapped, zero-cloud architecture and readiness for field deployment.

### 6.2 4-Person Team Role Allocation
1. **Member 1 (Legal & Operational Lead):** Section 63 BSA 2023 compliance, Section 91 CrPC notices, Chain of Custody.
2. **Member 2 (NLP & Local SLM Lead):** Offline SLM prompt engineering, deterministic Regex token parsing, slang disambiguation.
3. **Member 3 (Frontend & Workflow Lead):** Government of India light-theme UI, Glass-Box Trace-to-Source micro-interactions.
4. **Member 4 (Data & Systems Lead):** Universal Forensic Message Envelope (UFME), multi-source ingestion, air-gapped deployment.

---

### 7. MASTER CONCLUSION FOR PEER AGENTS
This platform is grounded in **operational reality, Indian legal statutes (BSA 2023), and strict forensic defensibility**. It avoids all high-level sci-fi traps while delivering an intuitive, self-updating, air-gapped workbench that solves real police friction on day one.
