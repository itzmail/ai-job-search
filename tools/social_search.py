#!/usr/bin/env python3
"""
Social job search query builder — generates search-engine-ready queries for
job posts on social platforms (LinkedIn, Threads, X/Twitter) plus web job boards.

Usage:
  python3 tools/social_search.py                      # run all categories
  python3 tools/social_search.py --category fullstack # one category
  python3 tools/social_search.py --category threads --limit 5
  python3 tools/social_search.py --json

The queries are meant to be executed by the AI agent via google_search /
web_search (grounding), or pasted into a browser. This tool is the single
place where the query vocabulary lives — keep it in sync with 01-candidate-profile.md.
"""

import argparse
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- query design

ROLE_SYNONYMS = {
    "fullstack": ["fullstack developer", "full-stack developer", "software engineer"],
    "backend":   ["backend engineer", "backend developer", "golang developer", "nodejs developer"],
    "frontend":  ["frontend engineer", "frontend developer", "react developer"],
    "mobile":    ["mobile developer", "flutter developer", "ios developer", "android developer", "react native developer"],
}

STACK_TERMS = ["Next.js", "TypeScript", "Golang", "Go", "React", "Flutter", "React Native",
               "PostgreSQL", "Node.js", "Swift"]

# Hiring-signal phrases per platform.
PLATFORM_PATTERNS = {
    "linkedin": {
        "domain": "site:linkedin.com/jobs",
        "phrases": ["hiring", "we're hiring", "join our team", "is hiring"],
    },
    "threads": {
        "domain": "(site:threads.net OR site:threads.com)",
        "phrases": ["hiring", "job opening", "we're hiring", "lowongan kerja", "chat me / DM me"],
    },
    "x": {
        "domain": "(site:x.com OR site:twitter.com)",
        "phrases": ["hiring", "job alert", "job opening", "remote job", "lowongan"],
    },
    "web": {
        "domain": "-site:linkedin.com -site:x.com",  # everything else (ATS boards, company blogs)
        "phrases": ["we're hiring", "job opening", "carreer", "join our team"],
    },
}

# Categories -> role synonyms
CATEGORIES = {
    "fullstack": ROLE_SYNONYMS["fullstack"],
    "backend":   ROLE_SYNONYMS["backend"],
    "frontend":  ROLE_SYNONYMS["frontend"],
    "mobile":    ROLE_SYNONYMS["mobile"],
    "all":       None,  # every category
}

LOCS = {
    "indonesia": ["Indonesia", "Yogyakarta", "Jakarta", "Bandung"],
    "remote":    ["remote", "work from anywhere", "APAC remote"],
    "global":    [],
}


def build_queries(platform: str, category: str, loc: str, limit: int):
    """Return list of platform-restricted search queries."""
    roles = CATEGORIES.get(category) or ROLE_SYNONYMS["fullstack"] + \
        ROLE_SYNONYMS["backend"] + ROLE_SYNONYMS["frontend"] + ROLE_SYNONYMS["mobile"]
    domain = PLATFORM_PATTERNS[platform]["domain"]
    phrases = PLATFORM_PATTERNS[platform]["phrases"]
    locs = LOCS.get(loc, LOCS["indonesia"])

    queries = []
    seen = set()
    for role in roles:
        for phrase in phrases[:2]:  # top-2 hiring phrases per role keeps volume sane
            for l in locs[:2]:      # top-2 locations per phrase
                q = f'{domain} "{role}" "{phrase}" {l}'
                stack = random.choice(STACK_TERMS)
                q += f' "{stack}"'
                if q not in seen:
                    seen.add(q)
                    queries.append(q)
                if len(queries) >= limit:
                    return queries
    return queries[:limit]


def main():
    ap = argparse.ArgumentParser(description="Build social job-search queries")
    ap.add_argument("--platform", choices=list(PLATFORM_PATTERNS.keys()), default=None,
                    help="One platform, or omit for all")
    ap.add_argument("--category", choices=list(CATEGORIES.keys()), default="all")
    ap.add_argument("--loc", choices=list(LOCS.keys()), default="indonesia")
    ap.add_argument("--limit", type=int, default=8, help="Queries per platform")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()

    platforms = [args.platform] if args.platform else list(PLATFORM_PATTERNS.keys())
    out = {}
    for plat in platforms:
        out[plat] = build_queries(plat, args.category, args.loc, args.limit)

    if args.json:
        print(json.dumps({"category": args.category, "loc": args.loc, "queries": out},
                         indent=2, ensure_ascii=False))
    else:
        for plat, queries in out.items():
            print(f"### {plat.upper()} ({args.category}, {args.loc})")
            for q in queries:
                print(f"  - {q}")
            print()


if __name__ == "__main__":
    main()
