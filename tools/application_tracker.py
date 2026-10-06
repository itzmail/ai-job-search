#!/usr/bin/env python3
"""
Application Tracker for AI Job Search.

Compact, token-efficient, file-based tracker for all job applications
(Email, LinkedIn, Web forms, etc.).
Prevents duplicate drafts, tracks application status, and syncs with Gmail sent box.

Storage: data/applied_jobs.json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
TRACKER_FILE = DATA_DIR / "applied_jobs.json"


def normalize_email(email_str: str) -> str:
    """Normalize and clean email address."""
    if not email_str:
        return ""
    # Extract email from formats like "Name <email@domain.com>"
    m = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", email_str)
    return m.group(0).lower().strip() if m else email_str.lower().strip()


def extract_domain(email_str: str) -> str:
    """Extract domain from email."""
    norm = normalize_email(email_str)
    if "@" in norm:
        return norm.split("@")[-1]
    return ""


def load_tracker() -> dict:
    """Load application records from JSON."""
    if not TRACKER_FILE.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        initial = {"version": "1.0", "updated_at": datetime.now().isoformat(), "applications": {}}
        TRACKER_FILE.write_text(json.dumps(initial, indent=2), encoding="utf-8")
        return initial

    try:
        data = json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
        if "applications" not in data:
            data["applications"] = {}
        return data
    except Exception:
        return {"version": "1.0", "updated_at": datetime.now().isoformat(), "applications": {}}


def save_tracker(data: dict):
    """Save application records to JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now().isoformat()
    TRACKER_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def is_already_applied(email_or_domain: str) -> tuple:
    """Check if an email or domain is already tracked. Returns (bool, record)."""
    norm = normalize_email(email_or_domain)
    domain = extract_domain(norm) or email_or_domain.lower().strip()

    tracker = load_tracker()
    apps = tracker.get("applications", {})

    # Check exact email
    if norm in apps:
        return True, apps[norm]

    # Check domain if not generic email provider
    generic_domains = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"}
    if domain and domain not in generic_domains:
        for rec in apps.values():
            if rec.get("domain") == domain:
                return True, rec

    return False, None


def record_application(
    to_email: str,
    subject: str,
    company: str = "",
    role: str = "",
    status: str = "applied",
    notes: str = "",
    date_str: str = None,
) -> dict:
    """Add or update an application in the tracker."""
    norm = normalize_email(to_email)
    domain = extract_domain(norm)
    tracker = load_tracker()

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # If company not provided, try to infer from domain
    if not company and domain:
        company = domain.split(".")[0].capitalize()

    record = {
        "email": norm,
        "domain": domain,
        "company": company,
        "role": role,
        "subject": subject,
        "status": status,
        "date": date_str,
        "notes": notes,
        "last_updated": datetime.now().isoformat(),
    }

    tracker["applications"][norm] = record
    save_tracker(tracker)
    return record


def sync_from_gmail(max_scan: int = 50) -> int:
    """Sync all job application emails from Gmail in:sent box."""
    try:
        from tools.gmail_client import get_service
    except ImportError:
        sys.path.insert(0, str(REPO_ROOT))
        from tools.gmail_client import get_service

    service = get_service()
    res = service.users().messages().list(userId="me", q="in:sent", maxResults=max_scan).execute()
    messages = res.get("messages", [])

    synced_count = 0
    tracker = load_tracker()

    for m in messages:
        msg = service.users().messages().get(
            userId="me",
            id=m["id"],
            format="metadata",
            metadataHeaders=["To", "Subject", "Date"],
        ).execute()
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        to_val = headers.get("To", "")
        subj_val = headers.get("Subject", "")
        date_raw = headers.get("Date", "")

        norm_email = normalize_email(to_val)
        if not norm_email:
            continue

        # Filter for job applications
        is_job = any(k in subj_val.lower() for k in [
            "application", "developer", "engineer", "flutter", "react", "golang", "backend", "frontend", "mobile"
        ])

        if is_job:
            domain = extract_domain(norm_email)
            company_guess = domain.split(".")[0].capitalize() if domain else ""

            # Check if already present
            existing = tracker["applications"].get(norm_email)
            if not existing or existing.get("status") != "applied":
                tracker["applications"][norm_email] = {
                    "email": norm_email,
                    "domain": domain,
                    "company": existing.get("company") if existing else company_guess,
                    "role": existing.get("role") if existing else "",
                    "subject": subj_val,
                    "status": "applied",
                    "date": date_raw,
                    "last_updated": datetime.now().isoformat(),
                }
                synced_count += 1

    save_tracker(tracker)
    return synced_count


def list_applications(status_filter: str = None) -> list:
    """List tracked applications."""
    tracker = load_tracker()
    apps = list(tracker.get("applications", {}).values())
    if status_filter:
        apps = [a for a in apps if a.get("status") == status_filter]
    return sorted(apps, key=lambda x: x.get("date", ""), reverse=True)


def main():
    parser = argparse.ArgumentParser(description="Job Application Tracker")
    subparsers = parser.add_subparsers(dest="command")

    # check command
    check_p = subparsers.add_parser("check", help="Check if email/company already applied")
    check_p.add_argument("target", help="Email or domain to check")

    # add command
    add_p = subparsers.add_parser("add", help="Record an application")
    add_p.add_argument("--to", required=True, help="Recipient email")
    add_p.add_argument("--subject", required=True, help="Email subject")
    add_p.add_argument("--company", default="", help="Company name")
    add_p.add_argument("--role", default="", help="Job role")
    add_p.add_argument("--status", default="applied", choices=["drafted", "applied", "interviewing", "rejected", "offered"])
    add_p.add_argument("--notes", default="")

    # sync command
    sync_p = subparsers.add_parser("sync", help="Sync applications from Gmail sent box")
    sync_p.add_argument("--limit", type=int, default=50, help="Max emails to scan")

    # list command
    list_p = subparsers.add_parser("list", help="List all tracked applications")
    list_p.add_argument("--status", help="Filter by status")
    list_p.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "check":
        found, rec = is_already_applied(args.target)
        if found:
            print(f"[ALREADY TRACKED] {args.target}")
            print(f"  Status: {rec.get('status')}")
            print(f"  Date: {rec.get('date')}")
            print(f"  Subject: {rec.get('subject')}")
            print(f"  Email: {rec.get('email')}")
            sys.exit(0)
        else:
            print(f"[CLEAN / NOT APPLIED] {args.target}")
            sys.exit(1)

    elif args.command == "add":
        rec = record_application(
            to_email=args.to,
            subject=args.subject,
            company=args.company,
            role=args.role,
            status=args.status,
            notes=args.notes,
        )
        print(f"Recorded application to {rec['email']} (Status: {rec['status']})")

    elif args.command == "sync":
        print("Scanning Gmail sent box and syncing tracker...")
        count = sync_from_gmail(max_scan=args.limit)
        total = len(load_tracker().get("applications", {}))
        print(f"Synced {count} new application(s). Total tracked: {total}")

    elif args.command == "list":
        apps = list_applications(args.status)
        if args.json:
            print(json.dumps(apps, indent=2, ensure_ascii=False))
        else:
            print(f"=== TRACKED APPLICATIONS ({len(apps)}) ===")
            for a in apps:
                print(f"[{a.get('status', '').upper()}] {a.get('email')} ({a.get('company', '')}) - {a.get('date', '')}")
                print(f"   Subject: {a.get('subject', '')}\n")


if __name__ == "__main__":
    main()
