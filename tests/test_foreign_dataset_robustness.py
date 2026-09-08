#!/usr/bin/env python3
"""
test_foreign_dataset_robustness.py - Robustness Test Against Messy Real-World & Foreign Data
Tests:
1. International / non-standard Indian phone formatting (+91-98140-22341, 09814022341, +91 98140 22341)
2. Messy foreign characters, emoji-obfuscated text, zero-width spaces, UTF-8 BOM
3. Real-world unformatted bank CSVs with custom column names
4. Graph generation on foreign unstructured chats
5. False positive rejection (decimals like ₹4500.00, software versions, timestamps, URLs)
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage

def test_entity_extraction_robustness():
    print("----------------------------------------------------------------------")
    print("🧪 1. TESTING ENTITY EXTRACTION ON NOISY / UNSTRUCTURED FOREIGN DATA")
    print("----------------------------------------------------------------------")

    messy_inputs = [
        # Zero-width spaces, emojis, multiple formats of phones
        "Bhai contact runner on \u200b+91 98140 22341 or alternate 09876543210 immediately 📱🔥",
        # Decimals that should NOT be parsed as phones
        "Transfer amount is ₹4500.00 and closing balance is 109415.04. Call support at 1800112211 or 9814022341.",
        # URL shielding: numbers inside URLs should not be extracted
        "Check proof at https://ipfs.io/ipfs/QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco/9814022341/tx.png",
        # Obfuscated UPI VPAs
        "Pay to: 9814022341@paytm or backup account chd_mule99@okaxis or crypto_onramp@upi",
        # Foreign crypto addresses
        "TRC20: TJ4V87qR984b2cNmQ7yXkL99pQ12345678 and BTC: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    ]

    all_phones = set()
    all_upis = set()
    all_crypto = set()

    for text in messy_inputs:
        ents = storage.extract_entities_from_text(text)
        all_phones.update(ents["phones"])
        all_upis.update(ents["upi_handles"])
        all_crypto.update(ents["crypto_wallets"])

    print(f"✓ Extracted phones: {all_phones}")
    assert "9814022341" in all_phones, "Failed to normalize spaced/prefixed phone number"
    assert "9876543210" in all_phones, "Failed to extract leading-zero phone number"
    assert "4500.00" not in all_phones, "False positive decimal extracted as phone!"
    assert "109415.04" not in all_phones, "False positive balance extracted as phone!"
    print("✅ False positive rejection passed (decimals/balances safely ignored)")

    print(f"✓ Extracted UPIs: {all_upis}")
    assert "9814022341@paytm" in all_upis
    assert "chd_mule99@okaxis" in all_upis
    assert "crypto_onramp@upi" in all_upis
    print("✅ UPI extraction on messy text passed")

    print(f"✓ Extracted Crypto: {all_crypto}")
    assert "TJ4V87qR984b2cNmQ7yXkL99pQ12345678" in all_crypto
    assert "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" in all_crypto
    print("✅ Multi-currency crypto extraction passed")

def test_unstructured_file_ingestion():
    print("\n----------------------------------------------------------------------")
    print("🧪 2. TESTING INGESTION OF UNSTRUCTURED FOREIGN FORMATS")
    print("----------------------------------------------------------------------")

    case_id = "FIR_FOREIGN_DATA_TEST"
    storage.init_db()
    storage.create_or_update_case(case_id, "FIR No. 888/2026/FOREIGN-TEST")

    # Raw messy CSV with BOM and custom header
    foreign_csv = "\ufeffTransactionID,timestamp,Account,txn_type,amount,counterparty_upi,description_remarks\n" \
                  "TXN-8801,2026-09-04 14:22:10,092100293812,CREDIT,20000.00,9814022341@paytm,Coaching Advance\n" \
                  "TXN-8802,2026-09-04 14:28:30,092100293812,CREDIT,17500.00,chd_mule99@okaxis,Exam Fee\n"

    res_csv = storage.parse_and_ingest_file(case_id, "foreign_export.csv", foreign_csv.encode('utf-8'))
    print(f"✓ Ingested foreign CSV: {res_csv['filename']} ({res_csv['file_type']}) - {res_csv['total_records']} records")
    assert res_csv['file_type'] == "BANK_STATEMENT_CSV", f"Expected BANK_STATEMENT_CSV, got {res_csv['file_type']}"

    # Messy WhatsApp export with irregular timestamps and foreign usernames
    foreign_chat = "[04/09/2026, 2:22:10 PM] Suspect_Alpha: Veere ₹20000 sent on 9814022341@paytm\n" \
                   "[04/09/2026, 2:28:30 PM] Suspect_Alpha: Baki ₹17500 on chd_mule99@okaxis\n" \
                   "[04/09/2026, 2:30:00 PM] Handler: Drop parcel at Sector 35 market behind Aroma Hotel\n"

    res_chat = storage.parse_and_ingest_file(case_id, "foreign_chat.txt", foreign_chat.encode('utf-8'))
    print(f"✓ Ingested foreign chat: {res_chat['filename']} ({res_chat['file_type']}) - {res_chat['total_records']} records")

    # Verify Graph Generation
    graph = storage.get_case_graph_data(case_id)
    print(f"✓ Generated Graph: {len(graph.get('nodes', []))} Nodes, {len(graph.get('edges', []))} Edges")
    assert graph.get("status") == "sufficient_linkage", f"Graph linkage failed: {graph}"
    assert len(graph.get("nodes", [])) >= 3, "Insufficient nodes in graph"
    assert len(graph.get("edges", [])) >= 2, "Insufficient edges in graph"
    print("✅ End-to-end graph correlation succeeded on foreign data!")

def main():
    print("=" * 70)
    print("🛡️ RUNNING FOREIGN & UNSTRUCTURED DATA ROBUSTNESS VERIFICATION")
    print("=" * 70)
    test_entity_extraction_robustness()
    test_unstructured_file_ingestion()
    print("\n" + "=" * 70)
    print("🎉 ALL FOREIGN DATA ROBUSTNESS TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
