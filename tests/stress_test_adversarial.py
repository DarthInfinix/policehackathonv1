"""
stress_test_adversarial.py - Forensic Stress-Testing Suite for PS3-DWID
Chandigarh Police Cyber Crime Investigation Platform
Tests obfuscated chat dumps, darknet listings, structured bank accounts, and seized OCR exhibits.
"""

import os
import sys
import time
import json
import sqlite3

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage
import ocr_worker

def run_stress_test():
    print("==========================================================================")
    print("🛡️  CHANDIGARH POLICE FORENSICS — ADVERSARIAL STRESS TEST SUITE")
    print("Testing Obfuscation Evasion, Codeword Disambiguation, & Cross-Case Links")
    print("==========================================================================")

    storage.init_db()
    case_id = "FIR_STRESS_2026_ADVERSARIAL"
    fir_number = "FIR No. 999/2026/CYBER-STRESS"
    
    # 1. Register Case
    case_info = storage.create_or_update_case(
        case_id=case_id,
        fir_number=fir_number,
        police_station="PS Cyber Crime, Sector 17, Chandigarh",
        io_name="Insp. Vikramjit Singh",
        io_belt="Belt #788-UT",
        category="ADVERSARIAL_STRESS_TEST"
    )
    print(f"✓ Registered test case: {case_info['fir_number']} (ID: {case_id})")

    adversarial_dir = os.path.join(BASE_DIR, "data", "adversarial")
    test_files = [
        ("adversarial_whatsapp_hinglish.txt", False),
        ("adversarial_darknet_listings.json", False),
        ("adversarial_bank_structuring.csv", False),
        ("adversarial_seized_chat_chit.png", False), # Run OCR
    ]

    # Ingestion & Benchmark
    ingest_results = {}
    start_total = time.time()

    for fname, skip_ocr in test_files:
        fpath = os.path.join(adversarial_dir, fname)
        if not os.path.isfile(fpath):
            print(f"⚠️  Missing file {fpath}, skipping...")
            continue

        print(f"\n▶ Ingesting exhibit: {fname} (Size: {os.path.getsize(fpath)} bytes)...")
        t0 = time.time()
        with open(fpath, "rb") as f:
            raw_bytes = f.read()

        res = storage.parse_and_ingest_file(
            case_id=case_id,
            filename=fname,
            content_bytes=raw_bytes,
            skip_ocr=skip_ocr,
            engine_preference="auto"
        )
        t_elapsed = time.time() - t0
        ingest_results[fname] = res
        print(f"  ✓ Ingested in {t_elapsed:.2f}s | Records: {res['total_records']} | Flagged: {res['total_flagged']} | SHA-256: {res['sha256'][:16]}...")

    total_time = time.time() - start_total

    # 2. Extract & Aggregate Extracted Entities
    leads = storage.get_dynamic_triage_leads(case_id)
    all_extracted_values = set()
    for l in leads:
        all_extracted_values.add(str(l["value"]).lower())

    # Query all raw mentions
    con = storage.get_db()
    cur = con.cursor()
    cur.execute("""
    SELECT DISTINCT LOWER(e.raw_value)
    FROM entities e
    JOIN entity_mentions em ON e.entity_id = em.entity_id
    JOIN evidence_records er ON em.record_id = er.record_id
    WHERE er.case_id = ?
    """, (case_id,))
    for row in cur.fetchall():
        all_extracted_values.add(row[0])
    con.close()

    print("\n--------------------------------------------------------------------------")
    print("📊 TARGET OBJECTION RECALL VERIFICATION")
    print("--------------------------------------------------------------------------")

    target_checks = [
        ("UPI: 9814022341@paytm", "9814022341@paytm"),
        ("UPI: chd_mule99@okaxis", "chd_mule99@okaxis"),
        ("UPI: mule44@ybl", "mule44@ybl"),
        ("Phone: 9814022341", "9814022341"),
        ("Phone: 9876543210", "9876543210"),
        ("TRON USDT: TJ4V87qR984b2cNmQ7yXkL99pQ12345678", "tj4v87qr984b2cnmq7yxkl99pq12345678"),
        ("Bitcoin: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "1a1zp1ep5qgefi2dmptftl5slmv7divfna"),
        ("Darknet Vendor: @chd_plug_official", "@chd_plug_official"),
        ("Location: Sector 35", "sector 35"),
        ("Location: Sector 22", "sector 22"),
        ("Narcotic: Chitta", "chitta"),
        ("Narcotic: White Shoes", "white shoes"),
        ("Narcotic: 4-MMC", "4-mmc"),
    ]

    hits = 0
    for label, target_val in target_checks:
        found = False
        for ext in all_extracted_values:
            if target_val.lower() in ext or ext in target_val.lower():
                found = True
                break
        status_icon = "✅ PASS" if found else "❌ MISS"
        if found:
            hits += 1
        print(f"  {status_icon} | {label}")

    recall_pct = (hits / len(target_checks)) * 100
    print(f"\nTotal Target Recall: {hits}/{len(target_checks)} ({recall_pct:.1f}%)")

    # 3. Cross-Case Correlations Check
    print("\n--------------------------------------------------------------------------")
    print("🔗 CROSS-CASE REFERENCING & ENTITY RESOLUTION")
    print("--------------------------------------------------------------------------")
    cross_matches = storage.get_cross_case_matches(case_id)
    print(f"Cross-Case Linkages Detected: {len(cross_matches)}")
    for m in cross_matches[:5]:
        print(f"  🔗 [CRITICAL] {m['entity_type']}: {m['raw_value']} ➔ Linked to Case: {m['matched_fir']} ({m['matched_io']}) in {m['matched_filename']}")

    # 4. Multi-Source Corroborations in Active Case
    corrs = storage.get_cross_source_correlations(case_id)
    print(f"\nWithin-Case Multi-Source Corroborations: {len(corrs)}")
    for c in corrs:
        print(f"  ⚡ Corroborated entity: {c['entity']} across {c['distinct_sources']} sources: {' ➔ '.join(c.get('sources_list', []))}")

    print("\n==========================================================================")
    print(f"BENCHMARK COMPLETE in {total_time:.2f}s")
    print(f"Total Records Ingested: {sum(r['total_records'] for r in ingest_results.values())}")
    print(f"Total Flagged Records:  {sum(r['total_flagged'] for r in ingest_results.values())}")
    print(f"Target Obfuscation Recall: {recall_pct:.1f}%")
    print(f"Cross-Case Corroborations: {len(cross_matches)}")
    print("==========================================================================")

    assert recall_pct >= 75.0, f"Recall {recall_pct}% is below required 75% threshold"
    print("✅ ADVERSARIAL STRESS TEST PASSED SPECIFICATION!")

if __name__ == "__main__":
    run_stress_test()
