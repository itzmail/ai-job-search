import unittest
from pathlib import Path
import subprocess
import json

REPO_ROOT = Path(__file__).resolve().parent.parent

SAMPLE_JD_PASS = """
Fullstack Developer (Next.js & Golang) - Remote Indonesia
We are looking for a Junior to Mid-level Fullstack Developer to join our team.
Requirements:
- 2+ years of experience with TypeScript, Next.js, and React.
- Solid experience with Go (Golang) backend microservices and PostgreSQL.
- Experience building RESTful APIs, OAuth 2.0 authentication, and CI/CD pipelines.
- Mobile development experience in Flutter is a huge plus.
- Agile/Scrum delivery environment.
- Good English communication skills.
Salary: IDR 12.000.000 - 18.000.000 / month.
"""

SAMPLE_JD_DEALBREAKER = """
Senior Principal Architect (Danish Speaker Only)
Location: Onsite Copenhagen
Requirements: 10+ years experience with Kubernetes, Rust, C++. Fluent Danish required.
"""

class TestATSAndTailor(unittest.TestCase):
    def test_ats_scorer_pass(self):
        proc = subprocess.run(
            ["python3", str(REPO_ROOT / "tools" / "ats_scorer.py"), SAMPLE_JD_PASS, "--json"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertGreaterEqual(data["score"], 80)
        self.assertEqual(data["verdict"], "APPLY")
        self.assertIn("go", data["breakdown"]["tech_stack"]["matched"])
        self.assertIn("next.js", data["breakdown"]["tech_stack"]["matched"])
        self.assertIn("postgresql", data["breakdown"]["tech_stack"]["matched"])
        self.assertEqual(len(data["dealbreakers"]), 0)

    def test_ats_scorer_dealbreaker(self):
        proc = subprocess.run(
            ["python3", str(REPO_ROOT / "tools" / "ats_scorer.py"), SAMPLE_JD_DEALBREAKER, "--json"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertIn("REJECT", data["verdict"])
        self.assertTrue(len(data["dealbreakers"]) > 0)

    def test_social_search_query_builder(self):
        proc = subprocess.run(
            ["python3", str(REPO_ROOT / "tools" / "social_search.py"), "--platform", "threads", "--category", "backend", "--json"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertIn("threads", data["queries"])
        self.assertTrue(len(data["queries"]["threads"]) > 0)

    def test_tailor_cv_and_audit(self):
        jd_file = REPO_ROOT / "tests" / "temp_jd.txt"
        out_tex = REPO_ROOT / "cv" / "main_testco_fullstack.tex"
        try:
            jd_file.write_text(SAMPLE_JD_PASS, encoding="utf-8")
            proc = subprocess.run(
                ["python3", str(REPO_ROOT / "tools" / "tailor_cv.py"),
                 "--jd", str(jd_file),
                 "--company", "TestCo",
                 "--role", "Fullstack Developer",
                 "--out", str(out_tex)],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("PASS: all bullets verbatim from master", proc.stdout)
            self.assertTrue(out_tex.exists())
        finally:
            if jd_file.exists():
                jd_file.unlink()
            if out_tex.exists():
                out_tex.unlink()

    def test_email_drafter(self):
        jd_file = REPO_ROOT / "tests" / "temp_jd2.txt"
        try:
            jd_file.write_text(SAMPLE_JD_PASS, encoding="utf-8")
            proc = subprocess.run(
                ["python3", str(REPO_ROOT / "tools" / "email_drafter.py"),
                 "--jd", str(jd_file),
                 "--company", "TestCo",
                 "--role", "Fullstack Developer",
                 "--json"],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertIn("Fullstack Developer", data["subject"])
            self.assertIn("Ismail Nur Alam", data["body"])
            self.assertTrue(len(data["grounded_points_used"]) > 0)
        finally:
            if jd_file.exists():
                jd_file.unlink()

if __name__ == "__main__":
    unittest.main()
