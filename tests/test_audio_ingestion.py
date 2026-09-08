"""
tests/test_audio_ingestion.py - Verification suite for heterogeneous voice note & audio evidence ingestion
Chandigarh Police Hackathon 2026 - PS-3
"""

import unittest
import os
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage
import audio_worker

class TestAudioIngestion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        storage.init_db()

    def test_01_audio_detection_and_formats(self):
        self.assertTrue(audio_worker.is_audio_data("voice_deal.ogg"))
        self.assertTrue(audio_worker.is_audio_data("suspect_call.opus"))
        self.assertTrue(audio_worker.is_audio_data("intercept.wav"))
        self.assertTrue(audio_worker.is_audio_data("recording.mp3"))
        self.assertTrue(audio_worker.is_audio_data("memo.m4a"))
        self.assertFalse(audio_worker.is_audio_data("chat.txt"))
        self.assertFalse(audio_worker.is_audio_data("bank.csv"))

    def test_02_audio_worker_transcribe_and_entities(self):
        demo_voice = os.path.join(BASE_DIR, "data", "raw", "seized_voice_note_deal.ogg")
        self.assertTrue(os.path.isfile(demo_voice), f"Missing demo audio {demo_voice}")

        with open(demo_voice, "rb") as f:
            raw_bytes = f.read()

        payload_res = audio_worker.transcribe_audio_payload(raw_bytes, "seized_voice_note_deal.ogg", case_id="FIR_104_2026")
        self.assertEqual(payload_res["status"], "success")
        self.assertIn("duration_sec", payload_res["metadata"])
        self.assertGreater(payload_res["total_records"], 0)

    def test_03_ingest_audio_into_storage(self):
        cid = "CASE_AUDIO_TEST_2026"
        storage.create_or_update_case(cid, "FIR No. 888/2026/CYBER-TEST", "PS Cyber Crime, Chandigarh", "Insp. Vikramjit Singh")

        demo_voice = os.path.join(BASE_DIR, "data", "raw", "seized_voice_note_deal.ogg")
        with open(demo_voice, "rb") as f:
            raw_bytes = f.read()

        res = storage.parse_and_ingest_file(
            case_id=cid,
            filename="seized_voice_note_deal.ogg",
            content_bytes=raw_bytes
        )

        self.assertIn("file_id", res)
        self.assertIn("VOICE", res["file_type"])
        self.assertGreater(res["total_records"], 0)

        # Verify records have source_type = VOICE_NOTE
        records = storage.get_file_records(res["file_id"])
        self.assertTrue(any(r["source_type"] == "VOICE_NOTE" for r in records))

        # Check audio path lookup
        audio_path = storage.get_evidence_audio_path(res["file_id"])
        self.assertIsNotNone(audio_path)
        self.assertTrue(os.path.isfile(audio_path))

        # Check triage leads generated from spoken content
        leads = storage.get_dynamic_triage_leads(cid)
        self.assertGreater(len(leads), 0)

        # Cleanup test case
        del_res = storage.delete_case(cid, performed_by="Unit Test", force=True)
        self.assertEqual(del_res["status"], "success")
        self.assertIsNone(storage.get_evidence_audio_path(res["file_id"]))

if __name__ == "__main__":
    unittest.main()
