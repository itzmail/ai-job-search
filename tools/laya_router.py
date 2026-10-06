#!/usr/bin/env python3
"""
Laya Semantic Router for Job Descriptions & Roles.

Connects to local Laya daemon (http://127.0.0.1:4141) to classify JDs
into categories: 'be' (Backend), 'fe' (Frontend), 'mobile' (Mobile), 'fullstack' (Software).
Falls back to fast deterministic regex matching when daemon is offline.

Usage:
  python3 tools/laya_router.py "Looking for a Golang backend engineer with PostgreSQL"
  python3 tools/laya_router.py --file jd.txt [--json]
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LAYA_URL = "http://127.0.0.1:4141"
TIMEOUT_SEC = 0.5  # Fast local timeout

DRIVE_CV_LINKS = {
    "fullstack": "https://docs.google.com/document/d/1Sv-EDZHrRwCgYRPWwwoyBJXZgBsClJrG/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
    "software":  "https://docs.google.com/document/d/1Sv-EDZHrRwCgYRPWwwoyBJXZgBsClJrG/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
    "mobile":    "https://docs.google.com/document/d/1nxpETgS_NOk5fk3WkMfSBIvqAVzvqF72/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
    "fe":        "https://docs.google.com/document/d/15GtUzVBvlZQ0LJwsDng0tyyALUuvzVSB/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
    "frontend":  "https://docs.google.com/document/d/15GtUzVBvlZQ0LJwsDng0tyyALUuvzVSB/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
    "be":        "https://docs.google.com/document/d/1uEksaTI2cevFpM-pt9xoJb6aFLm48KBR/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
    "backend":   "https://docs.google.com/document/d/1uEksaTI2cevFpM-pt9xoJb6aFLm48KBR/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
}

CV_TEXT_FILES = {
    "be":        REPO_ROOT / "my_profile" / "cv_be_text.txt",
    "backend":   REPO_ROOT / "my_profile" / "cv_be_text.txt",
    "fe":        REPO_ROOT / "my_profile" / "cv_fe_text.txt",
    "frontend":  REPO_ROOT / "my_profile" / "cv_fe_text.txt",
    "mobile":    REPO_ROOT / "my_profile" / "cv_mobile_text.txt",
    "fullstack": REPO_ROOT / "my_profile" / "cv_master_text.txt",
    "software":  REPO_ROOT / "my_profile" / "cv_master_text.txt",
}

CV_PDF_FILES = {
    "be":        REPO_ROOT / "my_profile" / "CV - Ismail_Nur_Alam_BE.pdf",
    "backend":   REPO_ROOT / "my_profile" / "CV - Ismail_Nur_Alam_BE.pdf",
    "fe":        REPO_ROOT / "my_profile" / "CV - Ismail_Nur_Alam_FE.pdf",
    "frontend":  REPO_ROOT / "my_profile" / "CV - Ismail_Nur_Alam_FE.pdf",
    "mobile":    REPO_ROOT / "my_profile" / "CV - Ismail_Nur_Alam_Mobile.pdf",
    "fullstack": REPO_ROOT / "my_profile" / "CV - Ismail_Nur_Alam.pdf",
    "software":  REPO_ROOT / "my_profile" / "CV - Ismail_Nur_Alam.pdf",
}


def is_laya_online() -> bool:
    """Check if local Laya daemon is responding."""
    try:
        req = urllib.request.Request(f"{LAYA_URL}/health", headers={"User-Agent": "pi-job-search"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            return resp.status == 200
    except Exception:
        return False


def route_via_laya(text: str) -> tuple[str, float, str]:
    """Call Laya router predict endpoint."""
    snippet = text[:500].strip()
    payload = json.dumps({"prompt": snippet, "text": snippet}).encode("utf-8")
    endpoints = [f"{LAYA_URL}/predict", f"{LAYA_URL}/route"]

    for ep in endpoints:
        try:
            req = urllib.request.Request(
                ep,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "pi-job-search"},
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cat = data.get("category") or data.get("route") or data.get("target") or "fullstack"
                conf = float(data.get("confidence") or data.get("score") or 1.0)
                return normalize_category(cat), conf, "laya-semantic"
        except Exception:
            continue

    return route_via_rules(text)


def route_via_rules(text: str) -> tuple[str, float, str]:
    """Deterministic keyword & regex fallback classifier."""
    low = text.lower()

    # Mobile indicators
    if any(re.search(p, low) for p in [r"\bmobile\b", r"\bflutter\b", r"react\s*native", r"\bswift\b", r"\bios\b", r"\bandroid\b"]):
        return "mobile", 0.90, "rule-based"

    # Frontend indicators
    if any(re.search(p, low) for p in [r"front[- ]?end", r"\bfrontend\b", r"next\.?js", r"\breact\.?js\b", r"\bui\s*(?:engineer|developer)\b"]):
        # Unless heavy backend terms dominate
        if not re.search(r"back[- ]?end|golang|spring\s*boot|distributed", low):
            return "fe", 0.88, "rule-based"

    # Backend indicators
    if any(re.search(p, low) for p in [r"back[- ]?end", r"\bbackend\b", r"\bgolang\b", r"spring\s*boot", r"database\s*engineer", r"microservices"]):
        return "be", 0.90, "rule-based"

    return "fullstack", 0.75, "rule-based"


def normalize_category(cat: str) -> str:
    c = cat.lower().strip()
    if c in ("be", "backend", "back-end", "go", "golang", "java"):
        return "be"
    if c in ("fe", "frontend", "front-end", "react", "nextjs"):
        return "fe"
    if c in ("mobile", "flutter", "ios", "android", "swift"):
        return "mobile"
    return "fullstack"


def route_job(text: str) -> dict:
    """Classify JD into role category and resolve matching CV assets."""
    if is_laya_online():
        cat, conf, engine = route_via_laya(text)
    else:
        cat, conf, engine = route_via_rules(text)

    cv_text_path = CV_TEXT_FILES.get(cat, CV_TEXT_FILES["fullstack"])
    cv_pdf_path = CV_PDF_FILES.get(cat, CV_PDF_FILES["fullstack"])
    drive_link = DRIVE_CV_LINKS.get(cat, DRIVE_CV_LINKS["fullstack"])

    label_map = {
        "be": "Backend Developer (Go / Spring / Postgres)",
        "fe": "Frontend Engineer (Next.js / React / TypeScript)",
        "mobile": "Mobile Developer (Flutter / Swift / Android)",
        "fullstack": "Fullstack / Software Engineer (Next.js / Go / Mobile)",
    }

    return {
        "category": cat,
        "label": label_map.get(cat, "Software Engineer"),
        "confidence": conf,
        "engine": engine,
        "cv_text_path": str(cv_text_path.relative_to(REPO_ROOT)) if cv_text_path.exists() else None,
        "cv_pdf_path": str(cv_pdf_path.relative_to(REPO_ROOT)) if cv_pdf_path.exists() else None,
        "drive_link": drive_link,
    }


def main():
    ap = argparse.ArgumentParser(description="Route JD to optimal CV variant using Laya or fallback")
    ap.add_argument("text", nargs="?", help="JD text / title snippet")
    ap.add_argument("--file", help="Path to JD file")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    args = ap.parse_args()

    if args.file:
        content = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        content = args.text
    else:
        ap.error("Provide text or --file")

    result = route_job(content)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("LAYA JOB ROUTER")
        print("=" * 60)
        print(f"Category   : {result['category'].upper()} ({result['label']})")
        print(f"Engine     : {result['engine']} (confidence: {result['confidence']:.2f})")
        print(f"CV PDF     : {result['cv_pdf_path']}")
        print(f"Drive Link : {result['drive_link']}")
        print("=" * 60)


if __name__ == "__main__":
    main()
