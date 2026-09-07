#!/usr/bin/env python3
"""
benchmark_p2v_accuracy.py - Real-World Forensic Benchmark on Raw Group Chat
Evaluates Phone, Crypto, UPI, Location, and Narcotics Extraction against 22,468 lines of human chat.
"""

import os
import sys
import re
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage

P2V_PATH = os.path.join(BASE_DIR, "data", "raw", "p2v_chat.txt")

def benchmark():
    print("=" * 75)
    print("🔬 CHANDIGARH POLICE FORENSICS — REAL-WORLD ACCURACY BENCHMARK")
    print(f"Dataset: data/raw/p2v_chat.txt")
    print("=" * 75)

    if not os.path.exists(P2V_PATH):
        print(f"❌ Error: {P2V_PATH} not found!")
        return

    with open(P2V_PATH, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Total Lines in Dataset: {total_lines:,}\n")

    t0 = time.time()

    # Track detections
    all_phones = set()
    all_crypto = set()
    all_upis = set()
    all_locations = set()
    all_slang = set()
    all_utrs = set()

    # Known ground truth targets
    known_real_phones = {
        "8824750994": "Gopal Pareek (+91 88247 50994)",
        "8264887080": "Hitesh Kochar (+91 82648 87080)",
        "8219674691": "Tarak Sharma (+91 82196 74691)",
        "8699199255": "Pushkar PEC MNC (+91 86991 99255)",
        "8437137229": "Pushkar PEC MNC (+91 84371 37229)",
        "8046110007": "Ahel Helpline (08046110007)",
        "8376804102": "Fortis Helpline (+918376804102)",
        "8369799513": "iCALL Helpline (8369799513)",
        "9372048501": "iCALL Helpline (9372048501)",
        "9920241248": "iCALL Helpline (9920241248)",
        "8422984528": "Samaritans Mumbai (918422984528)",
        "8422984529": "Samaritans Mumbai (918422984529)",
        "8422984530": "Samaritans Mumbai (918422984530)",
        "8445650266": "Kiran Helpline (8445650266)",
        "9999666555": "Vandrevala Helpline (9999666555)"
    }

    known_false_positives = {
        "phones": ["7867826290", "6666666666"],
        "crypto": ["1UyVZDziitMwK7cZP2UpJaHrJK1B7oekQ"],
    }

    flagged_records_count = 0
    acid_hits = []
    icetea_hits = []
    paper_hits = []

    for idx, line in enumerate(lines):
        ents = storage.extract_entities_from_text(line)
        has_flag = False

        if ents["phones"]:
            has_flag = True
            all_phones.update(ents["phones"])
        if ents["crypto_wallets"]:
            has_flag = True
            all_crypto.update(ents["crypto_wallets"])
        if ents["upi_handles"]:
            has_flag = True
            all_upis.update(ents["upi_handles"])
        if ents["locations"]:
            has_flag = True
            all_locations.update(ents["locations"])
        if ents["slang_keywords"]:
            has_flag = True
            all_slang.update(ents["slang_keywords"])
            if "acid" in ents["slang_keywords"]:
                acid_hits.append((idx + 1, line.strip()[:80]))
            if "ice tea" in ents["slang_keywords"]:
                icetea_hits.append((idx + 1, line.strip()[:80]))
            if "stamp paper" in ents["slang_keywords"] or "stamp papers" in ents["slang_keywords"]:
                paper_hits.append((idx + 1, line.strip()[:80]))
        if ents.get("transaction_refs"):
            has_flag = True
            all_utrs.update(ents["transaction_refs"])

        if has_flag:
            flagged_records_count += 1

    elapsed = time.time() - t0

    print("---------------------------------------------------------------------------")
    print(f"⚡ BENCHMARK EXECUTION TIME: {elapsed:.2f}s ({total_lines / elapsed:.0f} lines/sec)")
    print(f"Total Lines Flagged: {flagged_records_count:,} / {total_lines:,}")
    print("---------------------------------------------------------------------------\n")

    # 1. Phone Extraction Analysis
    print("📞 PHONE NUMBER EXTRACTION:")
    print(f"   Total Unique Phones Discovered: {len(all_phones)}")
    real_detected = 0
    for ph, desc in known_real_phones.items():
        hit = ph in all_phones
        if hit:
            real_detected += 1
        status = "✅ PASS" if hit else "❌ MISSED"
        print(f"   {status} | {ph} - {desc}")

    phone_recall = (real_detected / len(known_real_phones)) * 100
    print(f"\n   Real Phone Target Recall: {real_detected}/{len(known_real_phones)} ({phone_recall:.1f}%)")

    # False positive check for phones
    phone_fp_count = 0
    for fp in known_false_positives["phones"]:
        hit = fp in all_phones
        if hit:
            phone_fp_count += 1
        status = "❌ FP DETECTED" if hit else "✅ REJECTED (SAFE)"
        print(f"   {status} | Substring {fp} (URL param / floating point decimal)")

    # 2. Crypto Extraction Analysis
    print("\n🪙 CRYPTO WALLET EXTRACTION:")
    print(f"   Total Crypto Wallets Discovered: {len(all_crypto)}")
    crypto_fp_count = 0
    for fp in known_false_positives["crypto"]:
        hit = fp in all_crypto
        if hit:
            crypto_fp_count += 1
        status = "❌ FP DETECTED" if hit else "✅ REJECTED (SAFE)"
        print(f"   {status} | Google Doc ID: {fp}")

    # 3. Slang Disambiguation Analysis
    print("\n💊 NARCOTICS & SLANG DISAMBIGUATION:")
    print(f"   'acid' (LSD) False Positives in Chemistry Chat: {len(acid_hits)} (Baseline was 10+)")
    for lno, text in acid_hits[:3]:
        print(f"      • Line {lno}: {text}")
    print(f"   'ice tea' (Meth) False Positives in Food Chat: {len(icetea_hits)} (Baseline was 5)")
    for lno, text in icetea_hits[:3]:
        print(f"      • Line {lno}: {text}")
    print(f"   'stamp paper' False Positives in Exam Chat: {len(paper_hits)}")
    for lno, text in paper_hits[:3]:
        print(f"      • Line {lno}: {text}")

    # 4. Tricity Location Extraction Analysis
    print("\n📍 TRICITY GEOGRAPHIC LOCATIONS DISCOVERED:")
    print(f"   Total Unique Locations Detected: {len(all_locations)}")
    for loc in sorted(all_locations):
        print(f"      • {loc}")

    # Final assertions
    print("\n" + "=" * 75)
    print("📋 SUMMARY REPORT:")
    print(f"   • Spaced & Dashed Indian Phone Number Recall: {phone_recall:.1f}%")
    print(f"   • Phone False Positives (URLs/Decimals):     {phone_fp_count} (0 expected)")
    print(f"   • Crypto False Positives (Google Docs):      {crypto_fp_count} (0 expected)")
    print(f"   • Chemistry 'acid' False Positives:          {len(acid_hits)} (0 expected)")
    print(f"   • Beverage 'ice tea' False Positives:        {len(icetea_hits)} (0 expected)")
    print("=" * 75)

    assert phone_recall >= 90.0, f"Phone recall {phone_recall}% is below 90%"
    assert phone_fp_count == 0, f"Phone false positives detected: {phone_fp_count}"
    assert crypto_fp_count == 0, f"Crypto false positives detected: {crypto_fp_count}"
    assert len(acid_hits) == 0, f"Acid false positives detected: {len(acid_hits)}"
    assert len(icetea_hits) == 0, f"Ice tea false positives detected: {len(icetea_hits)}"

    print("🎉 BENCHMARK VALIDATION SUCCESSFUL: ALL CRITICAL CRITERIA SATISFIED!\n")

if __name__ == "__main__":
    benchmark()
