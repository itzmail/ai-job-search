#!/usr/bin/env python3
"""
Gmail Client for AI Job Search.
Provides authenticated access to Gmail API for:
  - Tracking job application responses (interviews, assessments, offers, rejections)
  - Creating draft emails (never auto-sends)

Usage:
  python3 tools/gmail_client.py auth                  # First-time browser login
  python3 tools/gmail_client.py test                  # Verify connection & show email address
  python3 tools/gmail_client.py search "<query>"       # Search emails
  python3 tools/gmail_client.py check-updates         # Scan for ATS & job application updates
  python3 tools/gmail_client.py draft --to <email> --subject <subj> --body <file_or_text>
"""

import argparse
import base64
import email
import json
import os
import sys
import warnings
from email.mime.text import MIMEText
from pathlib import Path

# Suppress Python version deprecation warnings from Google libraries
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")

REPO_ROOT = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = REPO_ROOT / "credentials.json"
TOKEN_FILE = REPO_ROOT / "token.json"

# Scopes needed: read mail (for status tracking) and compose drafts (for prepared applications)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]

# ATS & Job Board Sender Domains to track
ATS_DOMAINS = [
    "greenhouse.io",
    "lever.co",
    "myworkday.com",
    "ashbyhq.com",
    "smartrecruiters.com",
    "icims.com",
    "bamboohr.com",
    "workable.com",
    "recruitee.com",
    "jobvite.com",
    "linkedin.com",
]


def get_credentials():
    """Load or refresh OAuth2 credentials."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            print(f"Warning: Failed to load existing token: {e}", file=sys.stderr)
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"Credentials file not found at {CREDENTIALS_FILE}. "
                    "Please download OAuth Client ID credentials.json from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for subsequent runs
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return creds


def get_service():
    """Build and return Gmail API service instance."""
    from googleapiclient.discovery import build
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)


def get_user_profile():
    """Get authenticated user's email profile."""
    service = get_service()
    profile = service.users().getProfile(userId="me").execute()
    return profile


def search_messages(query: str, max_results: int = 20):
    """Search Gmail messages matching query."""
    service = get_service()
    response = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results,
    ).execute()

    messages = response.get("messages", [])
    results = []
    for msg_meta in messages:
        msg = service.users().messages().get(
            userId="me",
            id=msg_meta["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        results.append({
            "id": msg["id"],
            "threadId": msg.get("threadId"),
            "subject": headers.get("Subject", "(no subject)"),
            "from": headers.get("From", "(unknown)"),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        })
    return results


def check_job_updates(days: int = 14):
    """Scan recent emails from ATS platforms or mentioning job application terms."""
    ats_query = " OR ".join(f"from:{domain}" for domain in ATS_DOMAINS)
    keywords = '("interview" OR "application" OR "assessment" OR "offer" OR "status")'
    query = f"newer_than:{days}d ({ats_query} OR {keywords}) -in:sent -in:drafts"

    print(f"Scanning Gmail with query:\n  {query}\n")
    results = search_messages(query, max_results=30)
    return results


def create_draft(to_email: str, subject: str, body: str):
    """Create a draft message in user's Gmail box."""
    service = get_service()
    message = MIMEText(body, "plain", "utf-8")
    message["to"] = to_email
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw_message}},
    ).execute()

    return draft


def main():
    parser = argparse.ArgumentParser(description="Gmail Client for AI Job Search")
    subparsers = parser.add_subparsers(dest="command")

    # auth command
    subparsers.add_parser("auth", help="Run initial browser OAuth authentication")

    # test command
    subparsers.add_parser("test", help="Test connection & show account email")

    # search command
    search_p = subparsers.add_parser("search", help="Search emails")
    search_p.add_argument("query", help="Gmail search query")
    search_p.add_argument("--limit", type=int, default=10, help="Max results (default 10)")
    search_p.add_argument("--json", action="store_true", help="Output JSON")

    # check-updates command
    updates_p = subparsers.add_parser("check-updates", help="Check recent ATS/job status updates")
    updates_p.add_argument("--days", type=int, default=14, help="Lookback days (default 14)")
    updates_p.add_argument("--json", action="store_true", help="Output JSON")

    # draft command
    draft_p = subparsers.add_parser("draft", help="Create a draft email")
    draft_p.add_argument("--to", required=True, help="Recipient email")
    draft_p.add_argument("--subject", required=True, help="Subject line")
    draft_p.add_argument("--body", required=True, help="Body text or path to text file")
    draft_p.add_argument("--force", action="store_true", help="Force create draft even if already applied/drafted")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "auth":
            print("Authenticating with Google OAuth...")
            profile = get_user_profile()
            print(f"Success! Authenticated as: {profile.get('emailAddress')}")

        elif args.command == "test":
            profile = get_user_profile()
            print(f"Connected to Gmail: {profile.get('emailAddress')}")
            print(f"Total Messages: {profile.get('messagesTotal')}")
            print(f"Total Threads: {profile.get('threadsTotal')}")

        elif args.command == "search":
            results = search_messages(args.query, max_results=args.limit)
            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                print(f"Found {len(results)} message(s):")
                for r in results:
                    print(f"- [{r['date']}] {r['from']}")
                    print(f"  Subject: {r['subject']}")
                    print(f"  Snippet: {r['snippet'][:100]}...\n")

        elif args.command == "check-updates":
            results = check_job_updates(days=args.days)
            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                print(f"Found {len(results)} relevant job-related message(s):")
                for r in results:
                    print(f"- [{r['date']}] {r['from']}")
                    print(f"  Subject: {r['subject']}")
                    print(f"  Snippet: {r['snippet'][:120]}...\n")

        elif args.command == "draft":
            try:
                try:
                    from tools.application_tracker import is_already_applied, record_application
                except ImportError:
                    from application_tracker import is_already_applied, record_application

                already_applied, prev_rec = is_already_applied(args.to)
                if already_applied and not args.force:
                    print(
                        f"⚠️  ABORTED: Already tracked/applied to {args.to} (Status: {prev_rec.get('status')}, Date: {prev_rec.get('date')}).\n"
                        f"   Use --force if you intentionally want to draft a follow-up or duplicate.",
                        file=sys.stderr,
                    )
                    sys.exit(0)
            except SystemExit:
                sys.exit(0)
            except Exception as tracker_err:
                print(f"Warning: tracker check failed: {tracker_err}", file=sys.stderr)
                record_application = None

            body_text = args.body
            if os.path.exists(args.body):
                body_text = Path(args.body).read_text(encoding="utf-8")
            draft = create_draft(args.to, args.subject, body_text)
            print(f"Draft created successfully! Draft ID: {draft.get('id')}")

            if record_application:
                record_application(args.to, args.subject, status="drafted")
                print(f"Recorded in tracker: {args.to} (Status: drafted)")

            print(f"Open Gmail in your browser to review and send.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
