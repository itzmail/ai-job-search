#!/usr/bin/env python3
"""
Email Drafter - generates a pre-send cold-apply / application email draft.

The draft is grounded: it only references facts that exist in the master CV
(my_profile/cv_master_text.txt / cv/master_ismail.tex) and the JD itself.

Usage:
  python3 tools/email_drafter.py --jd jd.txt --company Acme --role "Backend Engineer" \
      [--to jobs@acme.com] [--contact "Hiring Team"]

Output:
  Human-readable email draft (subject, greeting, body, closing) to stdout,
  plus --json for structured output. The user copy-pastes or proceeds manually;
  this tool NEVER sends anything.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MASTER_TEXT = REPO_ROOT / "my_profile" / "cv_master_text.txt"
PROFILE_MD = REPO_ROOT / ".agents" / "skills" / "job-application-assistant" / "01-candidate-profile.md"

DRIVE_CV_LINKS = {
    "software": "https://docs.google.com/document/d/1Sv-EDZHrRwCgYRPWwwoyBJXZgBsClJrG/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
    "fullstack": "https://docs.google.com/document/d/1Sv-EDZHrRwCgYRPWwwoyBJXZgBsClJrG/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
    "mobile": "https://docs.google.com/document/d/1nxpETgS_NOk5fk3WkMfSBIvqAVzvqF72/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
    "frontend": "https://docs.google.com/document/d/15GtUzVBvlZQ0LJwsDng0tyyALUuvzVSB/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
    "fe": "https://docs.google.com/document/d/15GtUzVBvlZQ0LJwsDng0tyyALUuvzVSB/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
    "backend": "https://docs.google.com/document/d/1uEksaTI2cevFpM-pt9xoJb6aFLm48KBR/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
    "be": "https://docs.google.com/document/d/1uEksaTI2cevFpM-pt9xoJb6aFLm48KBR/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true",
}

CANDIDATE = {
    "name": "Ismail Nur Alam",
    "email": "ismailnuralam@gmail.com",
    "phone": "+6289611112146",
    "portfolio": "https://itsmail.dev",
    "github": "https://github.com/itzmail",
}

# Mapping: JD keyword -> 1-sentence grounded value proposition (all facts from CV).
VALUE_POINTS = {
    "typescript":   "hands-on TypeScript across web and mobile codebases",
    "javascript":   "hands-on JavaScript across web and mobile codebases",
    "go":           "production experience building Golang background schedulers and scoring/reporting modules",
    "java":         "backend work across Java (Spring Boot) services",
    "dart":         "Dart/Flutter mobile development",
    "swift":        "native iOS upgrades in Swift published to the App Store",
    "next.js":      "building scalable web applications in Next.js",
    "react":        "building web portals and UIs in React.js",
    "react native": "cross-platform mobile apps in React Native",
    "flutter":      "cross-platform mobile apps in Flutter",
    "express.js":   "backend architecture on Express.js",
    "spring boot":  "backend architecture on Spring Boot",
    "postgresql":   "PostgreSQL performance tuning, including resolving N+1 query bottlenecks",
    "mysql":        "MySQL database work",
    "mongodb":      "MongoDB database work",
    "oauth":        "designing and securing REST APIs with OAuth authentication",
    "rest":         "designing and securing RESTful APIs",
    "ci/cd":        "building CI/CD pipelines (Bitbucket Pipelines) for automated releases",
    "git":          "Git-based team workflows",
    "ios":          "end-to-end iOS App Store publishing",
    "android":      "end-to-end Google Play Store publishing",
    "performance":  "database and API performance optimization",
    "security":     "API security (OAuth 2.0)",
    "testing":      "testing and debugging mobile and web applications",
    "agile/scrum":  "Agile/Scrum delivery",
}


def extract_keywords(jd_text: str, cap: int = None) -> list:
    """JD keywords that also map to a grounded VALUE_POINT."""
    hi = [k for k, p in KEYWORD_PATTERNS().items()
          if any(re.search(p, jd_text, re.IGNORECASE) for p in [re.escape(k)])]
    return hi[:cap] if cap else hi


def KEYWORD_PATTERNS():
    return {k: re.escape(k) for k in VALUE_POINTS.keys()}


def pick_top_points(jd_text: str, n: int = 3) -> list:
    """Return up to n grounded value points ranked by keyword presence in JD."""
    hits = []
    for kw, vp in VALUE_POINTS.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", jd_text, re.IGNORECASE):
            hits.append((kw, vp))
    return hits[:n]


def load_yoe() -> int:
    """Years of experience from the master CV (3+ hardcoded fallback)."""
    t = MASTER_TEXT.read_text(encoding="utf-8")
    m = re.search(r"(\d+)\+?\s*years", t, re.IGNORECASE)
    return int(m.group(1)) if m else 3


def detect_role_category(role: str, jd_text: str = "") -> str:
    combined = f"{role} {jd_text}".lower()
    if any(k in combined for k in ["mobile", "flutter", "react native", "swift", "ios", "android"]):
        return "mobile"
    if any(k in combined for k in ["frontend", "front-end", "front end", "react.js", "next.js", "ui developer"]):
        return "frontend"
    if any(k in combined for k in ["backend", "back-end", "back end", "golang", "go developer", "spring boot", "database"]):
        return "backend"
    return "software"


def build_email(jd_text: str, company: str, role: str, to: str = None,
                contact: str = None, variant: str = None) -> dict:
    contact = contact or "Hiring Team"
    yoe = load_yoe()
    points = pick_top_points(jd_text, 3)
    cat = variant.lower() if variant else detect_role_category(role, jd_text)
    drive_link = DRIVE_CV_LINKS.get(cat, DRIVE_CV_LINKS["software"])

    bullets = [f"- {vp}" for _, vp in points] or [
        "- full-stack delivery experience across web and mobile",
        "- backend architectures in Go, Node.js, and Java (Spring Boot)",
        "- PostgreSQL performance optimization in production systems"]
    subject = f"Application: {role}" + (f" — {company}" if company else "")
    body = f"""Dear {contact},

I'm applying for the {role} position{" at " + company if company else ""}. I'm a software engineer with {yoe}+ years of experience shipping end-to-end web and mobile applications, and the role lines up closely with what I do day to day:

{chr(10).join(bullets)}

Most recently at PT Indoglobal Nusa Persada (Pintro) I built Golang background schedulers, optimized PostgreSQL queries, and shipped releases through Bitbucket CI/CD pipelines — for web products in Next.js and Flutter/Swift mobile apps.

CV (Google Drive): {drive_link}
Portfolio & Code: https://itsmail.dev | https://github.com/itzmail

I'd welcome the chance to talk about how I can contribute to {company or "your team"}.

Best regards,
Ismail Nur Alam
ismailnuralam@gmail.com | +6289611112146
https://itsmail.dev
"""
    return {
        "to": to,
        "subject": subject,
        "body": body,
        "grounded_points_used": [vp for _, vp in points],
        "category": cat,
        "drive_cv_link": drive_link,
        "attachment_hint": f"cv/main_<company>_<role>.pdf (optional if using Drive link)",
    }


def main():
    ap = argparse.ArgumentParser(description="Draft grounded application email")
    ap.add_argument("--jd", required=True, help="JD text file path")
    ap.add_argument("--company", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--to", help="Recipient email")
    ap.add_argument("--contact", help="Contact name, e.g. \"Hiring Team\"")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    jd_text = Path(args.jd).read_text(encoding="utf-8")
    draft = build_email(jd_text, args.company, args.role, args.to, args.contact)

    if args.json:
        print(json.dumps(draft, indent=2, ensure_ascii=False))
    else:
        print("=" * 62)
        print("EMAIL DRAFT (grounded — no invented facts)")
        print("=" * 62)
        if draft["to"]:
            print(f"To: {draft['to']}")
        print(f"Subject: {draft['subject']}")
        print("-" * 62)
        print(draft["body"])
        print("-" * 62)
        print("Grounded value points used:")
        for p in draft["grounded_points_used"]:
            print(f"  - {p}")
        print(f"Attach: {draft['attachment_hint']}")


if __name__ == "__main__":
    main()
