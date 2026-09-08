"""
tests/test_deletions.py - Verification suite for CRUD deletion endpoints
Chandigarh Police Hackathon 2026 - PS-3
"""

import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage

class TestForensicDeletions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        storage.init_db()

    def test_01_purge_test_cases(self):
        # Create a dummy test case
        c_res = storage.create_or_update_case(
            case_id="TEST_CASE_PURGE_ME_99",
            fir_number="FIR No. 9999/2026/CYBER-TEST",
            police_station="PS Cyber Crime, Chandigarh",
            io_name="Insp. Vikramjit Singh"
        )
        self.assertEqual(c_res["case_id"], "TEST_CASE_PURGE_ME_99")

        # Verify it exists
        cases_before = [c["case_id"] for c in storage.get_all_cases()]
        self.assertIn("TEST_CASE_PURGE_ME_99", cases_before)

        # Purge test cases
        purge_res = storage.purge_test_cases(performed_by="Unit Tester")
        self.assertEqual(purge_res["status"], "success")
        self.assertIn("TEST_CASE_PURGE_ME_99", purge_res["purged_cases"])

        # Verify it is gone
        cases_after = [c["case_id"] for c in storage.get_all_cases()]
        self.assertNotIn("TEST_CASE_PURGE_ME_99", cases_after)
        # Ensure benchmark cases are still intact
        self.assertIn("FIR_104_2026", cases_after)
        self.assertIn("FIR_999_ADVERSARIAL", cases_after)

    def test_02_delete_custom_case_cascading(self):
        cid = "CASE_DELETE_CASCADING_123"
        storage.create_or_update_case(cid, "FIR No. 1234/2026/CYBER", "PS Sector 17", "Insp. Vikramjit Singh")
        
        # Ingest a mock file with records
        f_res = storage.parse_and_ingest_file(
            case_id=cid,
            filename="mock_suspect_chat.txt",
            content_bytes=b"08/09/2026, 12:00 - Suspect: Transfer 50000 on test_mule@upi immediately for ice tea.\n08/09/2026, 12:05 - Mule: Done, utr is 123456789012",
            skip_ocr=True
        )
        self.assertGreater(f_res["total_records"], 0)

        # Verify files and records exist
        files = storage.get_case_files(cid)
        self.assertEqual(len(files), 1)
        records = storage.get_file_records(files[0]["file_id"])
        self.assertGreater(len(records), 0)

        # Expunge case
        del_res = storage.delete_case(cid, performed_by="Insp. Vikramjit Singh")
        self.assertEqual(del_res["status"], "success")
        self.assertEqual(del_res["case_id"], cid)

        # Verify cascade
        con = storage.get_db()
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM cases WHERE case_id = ?", (cid,))
        self.assertEqual(cur.fetchone()[0], 0)
        cur.execute("SELECT COUNT(*) FROM evidence_files WHERE case_id = ?", (cid,))
        self.assertEqual(cur.fetchone()[0], 0)
        cur.execute("SELECT COUNT(*) FROM evidence_records WHERE case_id = ?", (cid,))
        self.assertEqual(cur.fetchone()[0], 0)
        cur.execute("SELECT COUNT(*) FROM entity_mentions WHERE record_id = ?", (records[0]["record_id"],))
        self.assertEqual(cur.fetchone()[0], 0)
        con.close()

    def test_03_delete_individual_exhibit(self):
        cid = "FIR_104_2026"
        # Ingest a temporary dummy file
        f_res = storage.parse_and_ingest_file(
            case_id=cid,
            filename="temporary_wrong_upload.txt",
            content_bytes=b"This is a mistake upload with phone 9876543210 and upi accidental@paytm",
            skip_ocr=True
        )
        fid = f_res["file_id"]

        # Verify file is listed
        files_before = [f["file_id"] for f in storage.get_case_files(cid)]
        self.assertIn(fid, files_before)

        # Purge exhibit
        del_res = storage.delete_evidence_file(fid, case_id=cid, performed_by="Insp. Vikramjit Singh")
        self.assertEqual(del_res["status"], "success")
        self.assertEqual(del_res["file_id"], fid)

        # Verify file is no longer listed
        files_after = [f["file_id"] for f in storage.get_case_files(cid)]
        self.assertNotIn(fid, files_after)

    def test_04_delete_custom_officer_profile(self):
        # Create a custom officer
        prof = storage.create_officer("SI Temporary Officer", "Belt #999-UT", "Sub-Inspector", "IO", "PS Sector 19")
        oid = prof["officer_id"]

        officers_before = [o["officer_id"] for o in storage.get_officers()]
        self.assertIn(oid, officers_before)

        # Delete custom officer
        del_res = storage.delete_officer_profile(oid, performed_by="SP Balwinder Singh")
        self.assertEqual(del_res["status"], "success")

        officers_after = [o["officer_id"] for o in storage.get_officers()]
        self.assertNotIn(oid, officers_after)

    def test_05_protected_roles_and_cases(self):
        # Attempt to delete core benchmark case without force
        res_case = storage.delete_case("FIR_104_2026", performed_by="Hacker", force=False)
        self.assertEqual(res_case["status"], "error")

        # Attempt to delete core statutory officer
        res_off = storage.delete_officer_profile("OFFICER_IO_01", performed_by="Hacker")
        self.assertEqual(res_off["status"], "error")

if __name__ == "__main__":
    unittest.main()
