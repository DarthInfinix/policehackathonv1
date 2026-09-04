first, you can read the details from the hackathon track 3 documentation pdf. below are my raw thoughts :

< my thoughts >

The itinerary :

8th sept
8am registration begins
9am hackathon starts
1 pm lunch
4 pm hi tea
8 pm judging of your prototype followed by dinner
10 pm results for round 2 will be declared
← around here is where i expect to be eliminated →
9th sept
11 am inaugration
11.10-12.20pm presentation of shortlisted candidates.
12.20 to 1.30 speeches by dignitaries followed by valedictory and lunch.

Step 1 , have a meeting?
Main thing, what got us shortlisted?
I believe it is the local first approach , along with us not over-promising. We are not (capable of) building palantir that can generate insights from deep, complex, sometimes ai, sometimes hand rolled heuristics.
The prompt is “A Platform Related to Detection of Illicit
Drug Sales on Dark Net and Other Encrypted
Platforms”

Okay, what roles to give ?
To figure that out, need to know what each person CAN’T do, and what needs to be done.

According to our pitch,
Have a login flow where each role is separated
It essentially must track every action taken on data , timestamps , hashes, the works.
It should accept all forms of data. What does that mean? Html files, pdf files, images.
We should be able to process that data, meaning get something meaningful out of them.
Includes images using OCR , which is hit or miss.
We should do classical pattern matching for things that resemble data, like phone numbers, upi ids, crypto wallets.
We must have a way to break the data into manageable and lightly related chunks, that can be then sent to a local ai to do the all important “in context” keyword detection
They require us to model actors, which includes a visual way to represent them, which probably means nodes and graphs, but could be something else too.
It must not be cluttered, but also no feature should be tucked away.
Generate localized, standardized template alerts, be it copy pastable or what.
Have a way to store previous cases and insights generated. In a format that’s portable, searchable, and also fragile against local device outages, migration, etc.
Processing on device or from a local api can be slow and hallucination prone. Data may be multi gigabyte in size. Processing should be robust, and easy to inspect as it’s occurring, as it may be a multi hour ordeal.
Any insight generated must somehow be surfaced with its original source, and validation is a must, can’t rely on hallucination or rubber stamp tendencies.
Search must be intuitive, allow for filters.
Alright, team members, what can each one of us do / not do?

Prince : has spent time using local ai, is the team lead, made the initial prototype. Might be fit for the ai / pattern matching bits.

Pushkar : knows precisely zero code. Might have an eye for aesthetics. Could brainstorm the UX, flow, and meditate / critique the features on a high level, without worrying about implementation. Is also able to speak / present.

Vivek : self appointed DSA learner, but i can judge it to be that he doens’t know much coding either. However, is smart and will be able to work on self contained bits as assigned, with ai’s help of course. Unsure of his “taste” in smelling a bad / overengineered solution.

Ankush : big unknown , has done many leetcode problems, and has learnt “frontend”, but only using plain htmljs, but is the primary hope for building an ui that works.

Chirag : same boat as vivek, but is passionate, which is worth something i suppose. Will work on anything tasked with, might have more or less technical taste than vivek. Is unfamiliar with ai tools, which is an issue.

Introduce all of them to antigravity to spread out the massive token costs we will incur?

Create a master plan that encompasses this discussion so it can be worked on in independent parts.

Next concern : what role to give each, both in the 3 day gap we have before the hackathon, and in the main event itself.

There are passionate teams coming all the way from chennai / pune that are dedicated, have a lot to lose, and might have five whole members that work cohesively, cohesively enough to travel thousands of km together.

What do we have? Two members who don’t want to look into the implementation , dont want to discuss ideas, are just taking for granted we got shortlisted, i don’t blame them, i would too, as they did essentially zero work.

Other two who are essentially strangers, who talk a lot, but then fail to even prepare a single power point presentation because “ the topic is too much “.

All of them need to be told what to do exactly, and even then results are unclear.

Goal : to go have fun in those 24 hours ? but also don’t look incompetent.

Main worry? The PS has been open for a month, and the organizers expect us to work on it full time all that time, with the hackathon period essentially being the cherry on top where you showcase and refine what you have built so far with mentorship.

What have we done? Nothing yet.

Need to do something.

Figure out the actual UX , mock up some sketch designs on what exactly we want the platform to look like, and what dream features , when implemented would look like.

Main components of the app ?
The platform front end , which encompasses the reactivity, the ui, the ux, and the visualization bits.
The back end, which would run locally, and would encompass, what? The OCR, the pattern matching itself, model and potentially reach out to APIs for any sort of validation, manage the database. feed prompts to the ai, receive back ai responses, send data to the frontend
The data storage, should be portable and local. What does it store? An entire previous case, able to be called up at will, or even searched and cross referenced. Allow for uploading of peer databases from other instances of the platform, or even sync. What to store ? Ocr for future reference, the actual entity graph, all the learnt and validated keywords, a part of it should also store addresses, names, etc.
What to give to whom?
Vivek : i want him to work on the data storage , along with the backend to interface with said data storage. To somehow understnad what portability means and try to make the database like that.
Pushkar : i want him to understand this entire flow, then mock up some designs, think about what the app does, and then collaborate with ankush on the front end design
Ankush : i want him to work on the frontend along side the ai bits. Think about what the frontend looks like, what exact tech we will use to make it, how it will travel across devices, etc.
Chirag : i want him to work on the backend, interface with ai responses, implement search, implement ocr, implement a system that is not fragile.
Prince : bring this sinking ship together so it atleast sets sail once.

Coming back to the meeting, i want to brainstorm how this app will nitty gritty work, and then tomorrow evening hold a meeting such that i can clearly communicate what i want each of my “team” members to do, so i don’t end up trying to do everything on my own (which would be bad because winning is out of the cards, and slaving away alone feels like a waste of time).

How to communicate all this ? first begin with what the meta game happening with pre prep from other teams, how we cant do that, and what they all think the app is, then lay out my vision, then ask for feedback, then tentatively hand out roles along with concrete things i want out of them before monday, if only as a symbol, and then accept pushback, and then lay out my thoughts i tried to convey in this document itself.
< my thoughts end >
and then i had a conversation with an instance of you before, and , well, it built the whole prototype for me , and therefore is a bit too, uh, idk, optimistic? whatever, these are their thoughts, i mostly don't agree with the scope and what not, but just to give you more background.

< ai thoughts >

# CHANDIGARH POLICE HACKATHON 2026: MASTER BRIEF & STRATEGIC PLAYBOOK

> **Track:** Problem Statement 3 (PS3-DWID) — _Detection of Illicit Drug Sales on Darknet and Other Encrypted Platforms_  
> **Team:** `jugaducoders` (Punjab Engineering College, Chandigarh)  
> **Status:** Top 9 National Finalists (Selected from ~70 Track-3 Teams Nationwide)  
> **Grand Finale Venue:** UIET (University Institute of Engineering and Technology), Panjab University, Sector-25, Chandigarh  
> **Execution Date:** 8 September 2026 (12-Hour Active Hacking & Evaluation: 08:00 to 20:00 IST)  
> **Author & Technical Lead:** guy 5 (PEC Chandigarh)

---

## 1. THE STATUS QUO & REALITY CHECK

### 1.1 Where We Stand Today

Against ~70 technical teams nationwide (including senior teams from Army Institute of Technology Pune, Chennai Institute of Technology, Plaksha, Delhi, and Chandigarh University), a team of 2nd-year undergraduates from PEC built a legally grounded, air-gapped prototype and **qualified for the Top 9 National Finals**.

We did not get here by accident or luck. We got here because 85% of other teams submitted generic ChatGPT wrappers or sci-fi fantasies about "hacking encrypted WhatsApp in real-time." Our proposal won because it answered **real police friction**:

1. It grounded digital evidence in **Section 63(4) of the Bharatiya Sakshya Adhiniyam (BSA), 2023** (not the repealed 1872 Evidence Act).
2. It separated fast deterministic regex from **local, air-gapped Small Language Model (SLM) contextual triage**.
3. It addressed **slang drift and vocabulary evasion** via active in-context induction.
4. It recognized that frontline police officers need **copy-pasteable WhatsApp dispatches for PCR patrol teams and raw text for the Station Munshi**, not just rigid PDFs.

---

## 2. THE EVENT ITINERARY & THE "12-HOUR" CLOCK

The official schedule released by the organizing committee reveals a critical operational fact:

```
┌─────────────────┬────────────────────────────────────────────────────────────────────────────────────────┐
│ TIME            │ OFFICIAL EVENT PHASE                                                                   │
├─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
│ 08:00 AM        │ Mandatory Registration & Desk Allocation (UIET Sector-25)                              │
│ 09:00 AM        │ Hackathon Officially Begins                                                            │
│ 01:00 PM        │ Lunch & Informal Mentor Rounds                                                         │
│ 04:00 PM        │ High Tea & Second Evaluator Rounds                                                     │
│ 08:00 PM        │ ⚠️ OFFICIAL PROTOTYPE JUDGING BY POLICE & ACADEMIC JURY                                 │
│ 10:00 PM        │ Declaration of Round 2 Results (Top 3 Advance to Stage Presentations on Sept 9th)      │
└─────────────────┴────────────────────────────────────────────────────────────────────────────────────────┘
```

### The Critical Takeaway:

**The hackathon is not a 24-hour coding marathon. It is an 11-hour sprint.**  
Evaluation happens at **8:00 PM on Day 1**. If you try to invent an entire new application from a blank folder on Monday morning, you will run out of time.

### The "Open Secret" of In-Person Hackathons:

No serious team builds a complex cyber intelligence platform from scratch in 11 hours. Competitor teams from Pune and Chennai have spent the past three weeks assembling their codebases.

The 11-hour in-person round is an **evaluation theater & fraud filter** designed to test:

1. **Legitimacy:** Are the registered students capable of running, explaining, and debugging their own software?
2. **Mentorship Adaptability:** Can the team take live feedback from a Cyber Crime DSP at 2:00 PM and incorporate a small tweak by 6:00 PM?
3. **Local Resilience:** Does the software run 100% offline without crashing when university Wi-Fi inevitably fails?

---

## 3. OFFICIAL GUIDELINES & UNSTATED JURY EXPECTATIONS

The organizing committee released a strict 2-page directive. Here is how to decode the rules:

```
┌──────────────────────────────────────┬──────────────────────────────────────────┬─────────────────────────────────────────┐
│ OFFICIAL RESTRICTION IN GUIDELINES   │ WHY THE RULE EXISTS                      │ OUR STRATEGIC DEFENSE                   │
├──────────────────────────────────────┼──────────────────────────────────────────┼─────────────────────────────────────────┤
│ 1. Mandatory Physical Presence       │ Stops teams from having an off-site      │ All 5 registered members stay in the    │
│    (All 5 members must be in hall)   │ senior/brother code for them remotely.   │ room from 8 AM to 8 PM. Zero skips.     │
├──────────────────────────────────────┼──────────────────────────────────────────┼─────────────────────────────────────────┤
│ 2. "Every member must be able to     │ Judges love grilling the quietest member │ Every teammate has a pre-rehearsed      │
│    explain code, models, & logic"    │ to catch ghostwritten projects.          │ 60-second explanation of their module.  │
├──────────────────────────────────────┼──────────────────────────────────────────┼─────────────────────────────────────────┤
│ 3. Strictly NO Live Dark Web / PII   │ Avoids legal/university liability and    │ We proudly cite this rule and demo on a │
│    (Must use synthetic/OSINT data)   │ live `.onion` market downtime.           │ sanitized, multi-source mock dataset.   │
├──────────────────────────────────────┼──────────────────────────────────────────┼─────────────────────────────────────────┤
│ 4. NO Thin-Wrapper Commercial APIs   │ MHA / Police policy forbids sending real │ We use open-weight `Llama-3.2-3B`       │
│    (OpenAI/Claude wrappers banned)   │ criminal evidence to US commercial APIs. │ running 100% offline via Ollama/GGUF.   │
├──────────────────────────────────────┼──────────────────────────────────────────┼─────────────────────────────────────────┤
│ 5. Version-Controlled Git History    │ Proves the team actively worked and      │ Make 5–6 meaningful commits throughout   │
│    (Meaningful development history)  │ committed code during the hackathon.     │ the day (e.g. `feat: add regex parser`).│
└──────────────────────────────────────┴──────────────────────────────────────────┴─────────────────────────────────────────┘
```

---

## 4. THE CORE ARCHITECTURAL VISION: WHAT THE APP REALLY IS

Our platform is an **Air-Gapped Forensic Triage Copilot for Frontline Law Enforcement**. It bridges the gap between raw, messy seized digital evidence and legally admissible courtroom evidence.

```
 [ INGESTION LAYER ]         [ PROCESSING LAYER ]          [ INTELLIGENCE LAYER ]          [ ACTION & LEGAL LAYER ]
 ┌──────────────────────┐    ┌────────────────────────┐    ┌─────────────────────────┐     ┌────────────────────────┐
 │ • Tor .onion HTML    │ ──>│ • UFME Normalizer      │ ──>│ • Entity Link Graph     │ ──> │ • WhatsApp PCR Alert   │
 │ • Telegram Dumps     │    │ • Deterministic Regex  │    │ • Anti-Framing Matrix   │     │ • Munshi Zimni Export  │
 │ • WhatsApp Exports   │    │ • Local SLM (T=0.0)    │    │ • Slang Induction       │     │ • Sec 63 BSA Cert      │
 │ • Bank CSV Records   │    │ • SHA-256 Hash Chain   │    │ • Cross-Case Search     │     │ • Sec 91 CrPC Notices  │
 └──────────────────────┘    └────────────────────────┘    └─────────────────────────┘     └────────────────────────┘
```

### The 7 Indispensable Capabilities:

1. **Multi-Source Ingestion (Universal Forensic Message Envelope - UFME):** Normalizes darknet marketplace listings, Telegram chats, WhatsApp exports, and bank statements into a single, unified JSON schema.
2. **Deterministic vs. Semantic Two-Speed Engine:**
   - _Deterministic Regex:_ Extracts phone numbers, UPI handles, and TRON/Bitcoin wallets with zero latency and 100% certainty.
   - _Local Quantized SLM (`Llama-3.2-3B`, $T=0.0$):_ Disambiguates regional slang (_Chitta, White Shoes, 4-MMC, Pudiya, Tola_) and transaction context without cloud dependencies.
3. **Glass-Box "Trace-to-Source" Line Jumping:** Clicking `[Jump to Source ↗]` instantly scrolls to and highlights the raw evidence line and byte offset. Eliminates black-box AI hallucinations.
4. **Multi-Factor Anti-Framing Corroboration:** Cross-checks chat payment handles against bank statement credit transactions (`Score: 95% High Corroboration`) to protect innocent third parties from malicious framing.
5. **Antifragile In-Context Slang Induction:** Identifies recurring novel evasion codewords (_"Ice Tea"_) and promotes them to the precinct prompt dictionary with one click.
6. **Interactive Entity-Relationship Link Graph:** Visual SVG topology mapping connections between `Tor Market ➔ Telegram Admin ➔ TRON Wallet ➔ UPI Mule ➔ Bank Account ➔ Dead Drop`.
7. **Dual-Tier Operational Packaging:**
   - _Tactical Tier:_ 1-click formatted WhatsApp dispatches for PCR patrol vans and raw text for the Station Munshi Case Diary (_Zimni_).
   - _Judicial Tier:_ Section 63(4) BSA Digital Evidence Certificates with complete Machine & Model Manifests and Section 91 CrPC statutory bank freezing orders.

---

## 5. TEAM DYNAMICS & FOOLPROOF DELEGATION PLAYBOOK

### The Golden Rule of Delegating to Beginners:

> **Never ask beginners to design architecture or solve open-ended problems.**  
> **Give them self-contained, 30-line Python script recipes that AI can write in 5 minutes, and that they can test, run, and explain in terminal without touching the working master code.**

```
┌───────────┬───────────────────────────────┬──────────────────────────────────────────────────────────────────────┐
│ TEAMMATE  │ ASSIGNED MODULE               │ THE EXACT, BITE-SIZED DELIVERABLE                                    │
├───────────┼───────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
│ guy 1   │ Pitch, Story & Jury Lead      │ Master the slides, rehearse the 3-minute pitch, handle jury Q&A.     │
│ guy 2     │ SQLite Case Storage Worker    │ A 40-line Python script `storage.py` that saves/loads case JSONs.    │
│ guy 3    │ Regex & Offline OCR Worker    │ A 50-line Python script `extractor.py` pulling UPIs/SIMs & OCR text. │
│ guy 4    │ Frontend Link-Graph & Polish  │ Refine the SVG Network Graph in `index.html` & verify button states. │
│ guy 5    │ System Integrator & SLM Glue  │ Connect backend scripts to the UI via FastAPI and run local Ollama.  │
└───────────┴───────────────────────────────┴──────────────────────────────────────────────────────────────────────┘
```

### Detailed Deliverables for Each Member:

#### 1. guy 1 (The Speaker / Non-Coder)

- **His Mission:** Master the story and command the table when judges and mentors arrive.
- **His Cheat-Sheet to Memorize:**
  - Why Section 63 BSA (2023) replaced Section 65B of the 1872 Evidence Act.
  - The "Wholesale vs. Retail" reality (Tor is used for wholesale synthetic imports; Telegram/WhatsApp is used for local Tricity retail distribution).
  - How our anti-framing score protects innocent people whose phone numbers are spammed in public drug chats.

#### 2. guy 2 (Case Storage Module)

- **His Mission:** Write a standalone Python script `storage.py` using standard `sqlite3`.
- **The Exact Prompt guy 2 Gives to AI:**
  ```text
  Write a clean Python 3 script using sqlite3. It should create a database called `precinct_cases.db` with a table `cases` containing (case_id TEXT PRIMARY KEY, fir_number TEXT, io_name TEXT, evidence_json TEXT, created_at TEXT). Include three functions: save_case(case_id, fir, io, data), load_case(case_id), and search_cases(keyword). Add a main block demonstrating saving and loading a mock case.
  ```

#### 3. guy 3 (Data Ingest & OCR Module)

- **His Mission:** Write a standalone Python script `extractor.py` using `re` and `pytesseract`.
- **The Exact Prompt guy 3 Gives to AI:**
  ```text
  Write a standalone Python 3 script using standard `re` and `pytesseract` (or easyocr). It should take a text string or an image filepath. It must extract: (1) all Indian UPI handles (ending in @ybl, @okhdfcbank, @paytm, etc.), (2) Indian phone numbers starting with +91 or 10-digits, (3) TRON/Bitcoin wallet addresses. Print the extracted entities as a clean Python dictionary.
  ```

#### 4. guy 4 (Frontend & Graph Polish)

- **His Mission:** Review `index.html` and `styles.css` on his laptop.
- **The Exact Task:**
  - Verify that the SVG Network Graph renders crisply on different screen sizes.
  - Ensure all modal close buttons (`✕`) and tabs switch smoothly with zero JavaScript console warnings.

#### 5. guy 5 (You: System Integrator & SLM Runner)

- Keep `Ollama` running locally with `Llama-3.2-3B`.
- Write a simple 40-line `FastAPI` server (`server.py`) that imports guy 2's `storage.py`, guy 3's `extractor.py`, and exposes 2 endpoints:
  - `POST /api/ingest`: Runs extractor and returns entities.
  - `POST /api/triage`: Feeds context to Ollama and returns structured JSON.
- Connect the frontend `fetch()` calls to these endpoints. If the backend is ever buggy, the UI automatically falls back to our pre-computed mock data!

---

## 6. SCRIPT FOR THE GOOGLE MEET (FRIDAY EVENING)

Keep the meeting under 20 minutes. Be calm, casual, and clear:

> _"Hey guys, thanks for hopping on. I know college quizzes have been brutal this week and everyone's drained. But look: **we are officially in the Top 9 National Finalists** out of 60+ teams across India. That’s already a massive achievement for 2nd years._
>
> _I want to be completely honest: nobody expects us to be senior defense contractors writing 10,000 lines of C++. We are going to UIET on Monday to have fun, eat free food, experience our first offline hackathon, and look sharp in front of the Chandigarh Police._
>
> _Here is the secret: **Most of our prototype is already built and working.** We don't need to panic. We just need to divide 4 small, isolated pieces so everyone has something legitimate to show and explain on their own laptop:_
>
> 1. _guy 1: You lead the presentation and jury interaction. You and I will rehearse the pitch so you own the room when mentors visit our table._
> 2. _guy 2: You take the Case Storage script. A simple Python script using SQLite to save and search past cases._
> 3. _guy 3: You take the Ingest Worker. A Python script using regex and basic OCR to pull UPI IDs and text from photos._
> 4. _guy 4: You take Frontend polish. You know HTML/JS, so you will polish our SVG Network Graph and verify UI responsiveness._
> 5. _Me (guy 5): I will run the local AI model (Llama-3.2) and wire your backend scripts to the frontend._
>
> _Before Monday, all I want from guy 2 and guy 3 is one small 40-line Python script that runs cleanly in terminal. That's it. Let's get through this together and make PEC proud on Monday."_

---

## 7. THE 72-HOUR COUNTDOWN (SEPT 4 TO SEPT 7)

```
┌─────────────────┬────────────────────────────────────────────────────────────────────────────────────────┐
│ TIMELINE        │ OBJECTIVE                                                                              │
├─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
│ Friday, Sept 4  │ • Hold the 20-minute Google Meet. Assign the 4 isolated tasks.                         │
│                 │ • Push current working prototype to a private GitHub repo: `chd-police-forensic-app`.  │
├─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
│ Saturday, Sept 5│ • guy 2 tests `storage.py` on his machine. guy 3 tests `extractor.py`.                │
│                 │ • guy 5 sets up local `Ollama` with `llama-3.2:3b` on the primary demo laptop.        │
├─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
│ Sunday, Sept 6  │ • guy 5 wires guy 2 & guy 3's scripts into `server.py` (FastAPI).                     │
│                 │ • guy 1 and guy 5 do two dry-runs of the 3-minute pitch deck.                       │
│                 │ • Pack hardware: 2 laptops, extension board, chargers, offline datasets on USB drive. │
├─────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
│ Monday, Sept 8  │ • 08:00 AM: Arrive at UIET Sector-25.                                                  │
│ (THE BIG DAY)   │ • 09:00 AM – 08:00 PM: Execute the 11-hour playbook, commit code, demo to jury!        │
└─────────────────┴────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. MASTER SUMMARY

You are not an imposter. You are not "LARPing."

You identified real legal constraints, designed an air-gapped system, and solved a real police problem that 85% of other teams completely missed.

Follow the isolated delegation plan. Protect your working master code. Help your friends write their 40-line scripts. Walk into UIET on Monday morning knowing that your team has the sharpest, most defensible solution in the room.

**Go win your place on that podium.** 🏆🔥
< ai thoughts end >

alright, now the important bit, take the ai thoughts with a grain of salt for now, and instead, let us have a conversation on how exactly this application will be built, in great detail. where to get the mock / synthetic data in sizeable enough quantities to be non trivial to parse, perhaps also find images and whatnot, what tech to use for the database, what to use for constrained ais, what for ocr, what for building a graph, what to build for a frontend, and before all of this, i want, through discussion, to arrive at an idea of what this platform even is, and how it will function, untethered from whatever decisions i made to make the proptotype you see in the three files. like, i say i want it to be resilient, but how to build that, etc.
