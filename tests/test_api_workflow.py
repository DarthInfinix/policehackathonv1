#!/usr/bin/env python3
"""
Integration test for Chandigarh Police Cyber Forensic Workbench API
Tests:
- Server endpoints: /api/cases, /api/cases/create
- Ingestion of adversarial dataset via /api/load_demo_data?type=adversarial
- Querying files and records: /api/files, /api/file_records
- Triage leads and cross-case hit annotations: /api/leads
- Cross-case matches: /api/cross_case_matches
- FTS5 global search: /api/search
- Codeword induction: /api/induct_codeword, /api/slang_dictionary
"""

import sys
import os
import json
import time
import threading
import urllib.request
import urllib.parse
from http.server import HTTPServer

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import server
import storage

PORT = 8899

def run_server():
    httpd = HTTPServer(("127.0.0.1", PORT), server.ForensicHTTPRequestHandler)
    httpd.serve_forever()

def http_get(path):
    url = f"http://127.0.0.1:{PORT}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

def http_post(path, data=None):
    url = f"http://127.0.0.1:{PORT}{path}"
    body = json.dumps(data).encode('utf-8') if data else b""
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

def main():
    print("=" * 70)
    print("🧪 RUNNING END-TO-END WORKBENCH API INTEGRATION TEST")
    print(f"Target Port: {PORT}")
    print("=" * 70)

    # Start server thread
    srv_thread = threading.Thread(target=run_server, daemon=True)
    srv_thread.start()
    time.sleep(0.8)

    test_case_id = f"TEST_CASE_{int(time.time())}"
    test_fir = f"FIR No. {int(time.time()) % 1000}/2026/CYBER-TEST"

    # 1. Test /api/cases
    status, res = http_get("/api/cases")
    assert status == 200, f"Expected 200, got {status}"
    assert "cases" in res, "Expected 'cases' in response"
    print(f"✓ GET /api/cases returned {len(res['cases'])} existing cases.")

    # 2. Test /api/cases/create
    case_payload = {
        "case_id": test_case_id,
        "fir_number": test_fir,
        "police_station": "PS Cyber Crime, Sector 17, Chandigarh",
        "io_name": "Insp. Jaswinder Singh",
        "io_belt": "Belt #999-UT",
        "category": "NDPS_CYBER"
    }
    status, res = http_post("/api/cases/create", case_payload)
    assert status == 200, f"Expected 200, got {status}"
    assert res.get("status") == "success", f"Case creation failed: {res}"
    print(f"✓ POST /api/cases/create registered case: {test_fir}")

    # 3. Test /api/load_demo_data with adversarial dataset
    status, res = http_post(f"/api/load_demo_data?case_id={test_case_id}&type=adversarial")
    assert status == 200, f"Expected 200, got {status}"
    assert res.get("status") == "success", f"Adversarial load failed: {res}"
    print(f"✓ POST /api/load_demo_data?type=adversarial loaded {res.get('files_loaded')} files ({res.get('total_records')} records).")

    # 4. Test /api/files
    status, res = http_get(f"/api/files?case_id={test_case_id}")
    assert status == 200, f"Expected 200, got {status}"
    files = res.get("files", [])
    assert len(files) >= 3, f"Expected at least 3 files, got {len(files)}"
    print(f"✓ GET /api/files returned {len(files)} files staged for {test_case_id}:")
    for f in files:
        print(f"   • {f['filename']} ({f['file_type']}) - {f['record_count']} records - SHA: {f['sha256_hash'][:16]}...")

    # 5. Test /api/leads with cross-case detection
    status, res = http_get(f"/api/leads?case_id={test_case_id}")
    assert status == 200, f"Expected 200, got {status}"
    leads = res.get("leads", [])
    assert len(leads) > 0, "Expected triage leads to be generated"
    cross_case_hits = [l for l in leads if l.get("crossCaseHit")]
    print(f"✓ GET /api/leads returned {len(leads)} triage leads ({len(cross_case_hits)} marked with CROSS-CASE HIT).")
    for l in leads[:4]:
        flag = " [⚠️ CROSS-CASE]" if l.get("crossCaseHit") else ""
        print(f"   • [{l['type']}] {l['value']}{flag} - Corroboration: {l.get('corroboration', {}).get('basis')}")

    # 6. Test /api/cross_case_matches
    status, res = http_get(f"/api/cross_case_matches?case_id={test_case_id}")
    assert status == 200, f"Expected 200, got {status}"
    matches = res.get("matches", [])
    print(f"✓ GET /api/cross_case_matches detected {len(matches)} historical links across precinct cases.")
    if matches:
        m = matches[0]
        print(f"   • Linked entity: {m['entity_value']} ({m['entity_type']}) linked to FIR: {m['matched_fir']}")

    # 7. Test /api/search (FTS5 global search)
    status, res = http_get("/api/search?q=mule44@ybl")
    assert status == 200, f"Expected 200, got {status}"
    hits = res.get("results", [])
    print(f"✓ GET /api/search?q=mule44@ybl returned {len(hits)} FTS5 indexed hits.")

    # 8. Test /api/induct_codeword
    induct_payload = {
        "term": "sweets",
        "meaning": "MDMA / Ecstasy Pills (NDPS Sec 22)",
        "case_id": test_case_id,
        "io_name": "Insp. Jaswinder Singh"
    }
    status, res = http_post("/api/induct_codeword", induct_payload)
    assert status == 200, f"Expected 200, got {status}"
    assert res.get("status") == "success", f"Induction failed: {res}"
    print(f"✓ POST /api/induct_codeword successfully sealed 'sweets' into precinct dictionary (SHA-256: {res.get('hash')[:16]}...)")

    # Verify in /api/slang_dictionary
    status, res = http_get("/api/slang_dictionary")
    assert status == 200
    terms = [w["slang_term"] for w in res.get("words", [])]
    assert "sweets" in terms, "Expected 'sweets' to be in dictionary"
    print(f"✓ GET /api/slang_dictionary verified presence of 'sweets'.")

    print("=" * 70)
    print("🎉 ALL END-TO-END WORKBENCH API INTEGRATION TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
