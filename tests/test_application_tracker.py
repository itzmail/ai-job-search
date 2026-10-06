"""
Tests for Application Tracker (tools/application_tracker.py)
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.application_tracker import (
    normalize_email,
    extract_domain,
    is_already_applied,
    record_application,
    load_tracker,
    save_tracker,
    list_applications,
)


class TestApplicationTracker(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tracker_file = Path(self.temp_dir.name) / "applied_jobs.json"
        self.patcher_file = patch("tools.application_tracker.TRACKER_FILE", self.tracker_file)
        self.patcher_dir = patch("tools.application_tracker.DATA_DIR", Path(self.temp_dir.name))
        self.patcher_file.start()
        self.patcher_dir.start()

    def tearDown(self):
        self.patcher_file.stop()
        self.patcher_dir.stop()
        self.temp_dir.cleanup()

    def test_normalize_email(self):
        self.assertEqual(normalize_email("Ismail <ismail@gmail.com>"), "ismail@gmail.com")
        self.assertEqual(normalize_email("HR@Company.MY"), "hr@company.my")
        self.assertEqual(normalize_email(""), "")

    def test_extract_domain(self):
        self.assertEqual(extract_domain("hr@veecotech.com.my"), "veecotech.com.my")
        self.assertEqual(extract_domain("test@gmail.com"), "gmail.com")

    def test_record_and_check_duplicate(self):
        found, _ = is_already_applied("hr@veecotech.com.my")
        self.assertFalse(found)

        record_application(
            to_email="hr@veecotech.com.my",
            subject="Application: Mobile Dev",
            company="VeecoTech",
            role="Mobile Developer",
            status="applied",
        )

        found, rec = is_already_applied("hr@veecotech.com.my")
        self.assertTrue(found)
        self.assertEqual(rec["company"], "VeecoTech")
        self.assertEqual(rec["status"], "applied")

        # Test domain match check
        found_domain, rec_domain = is_already_applied("careers@veecotech.com.my")
        self.assertTrue(found_domain)
        self.assertEqual(rec_domain["company"], "VeecoTech")

    def test_list_applications(self):
        record_application("a@corp.com", "Subj A", status="applied")
        record_application("b@corp.com", "Subj B", status="drafted")

        all_apps = list_applications()
        self.assertEqual(len(all_apps), 2)

        drafted = list_applications("drafted")
        self.assertEqual(len(drafted), 1)
        self.assertEqual(drafted[0]["email"], "b@corp.com")


if __name__ == "__main__":
    unittest.main()
