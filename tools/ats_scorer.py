#!/usr/bin/env python3
"""
ATS Scorer - scores a job description against the candidate's master profile.

Usage:
  python3 tools/ats_scorer.py "<job description text>"
  python3 tools/ats_scorer.py --file jd.txt [--json] [--min-score 60]

Ground truth (source of truth for all facts):
  - cv/master_ismail.tex            (master CV)
  - my_profile/cv_master_text.txt   (text extracted from the canonical PDF)

Output:
  - Human-readable report; JSON report with --json.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES = [
    REPO_ROOT / "cv" / "master_ismail.tex",
    REPO_ROOT / "my_profile" / "cv_master_text.txt",
]

# --- Scoring weights (sum = 100) ---
W_TECH = 45      # tech stack keyword match
W_SENIORITY = 20  # junior/mid fit
W_DOMAIN = 20    # role/domain fit
W_SOFT = 15      # soft keywords (Agile, REST, testing, etc.)

# --- Tech keywords: canonical name -> [patterns] found in JD text ---
TECH_KEYWORDS = {
    "typescript":   [r"typescript"],
    "javascript":   [r"javascript"],
    "go":           [r"\bgolang\b", r"\bgo\b(?=\s*(?:micro|dev|developer|development|engineer|lang\b|programming|services|backend|developer))", r"\bgopher\b"],
    "java":         [r"\bjava\b", r"spring\s*boot"],
    "dart":         [r"\bdart\b"],
    "swift":        [r"\bswift\b"],
    "next.js":      [r"next\.?js", r"nextjs"],
    "react":        [r"\breact\.?js\b", r"\breact\b"],
    "react native": [r"react\s*native"],
    "flutter":      [r"\bflutter\b"],
    "express.js":   [r"express\.?js", r"\bexpress\b"],
    "spring boot":  [r"spring\s*boot"],
    "svelte":       [r"\bsvelte\b"],
    "astro":        [r"\bastro\b"],
    "tailwind":     [r"tailwind"],
    "node.js":      [r"node\.?js", r"\bnode\b"],
    "postgresql":   [r"postgres(?:ql)?", r"\bpg\b"],
    "mysql":        [r"\bmy\s?sql\b"],
    "mongodb":      [r"mongo(?:db)?"],
    "oauth":        [r"\boauth\b"],
    "rest":         [r"\brest(?:ful)?\b(?=\s*(api|api)?)", r"restful"],
    "graphql":      [r"\bgraphql\b"],
    "grpc":         [r"\bgrpc\b"],
    "ci/cd":        [r"\bci/?cd\b", r"continuous\s+integration", r"pipelines?"],
    "git":          [r"\bgit\b"],
    "gitlab":       [r"\bgitlab\b"],
    "github":       [r"\bgithub\b"],
    "bitbucket":    [r"\bbitbucket\b"],
    "docker":       [r"\bdocker\b"],
    "kubernetes":   [r"\bkubernetes\b", r"\bk8s\b"],
    "aws":          [r"\baws\b", r"amazon web services"],
    "gcp":          [r"\bgcp\b", r"google cloud"],
    "azure":        [r"\bazure\b"],
    "redis":        [r"\bredis\b"],
    "xcode":        [r"\bxcode\b"],
    "android studio": [r"android\s*studio"],
    "ios":          [r"\bios\b"],
    "android":      [r"\bandroid\b"],
}

# JD keyword -> profile-side match aliases (grounded in master CV).
PROFILE_ALIASES = {
    "go":           ["golang", "go "],
    "next.js":      ["next.js", "nextjs"],
    "express.js":   ["express.js", "express"],
    "rest":         ["rest"],
    "typescript":   ["typescript"],
    "postgresql":   ["postgresql", "postgres"],
    "mongodb":      ["mongodb", "mongo"],
    "mysql":        ["mysql"],
}

# --- Domain keywords (role/domain fit) ---
DOMAIN_KEYWORDS = {
    "fullstack":   [r"full[- ]?stack", r"fullstack"],
    "frontend":    [r"front[- ]?end", r"frontend", r"ui engineer"],
    "backend":     [r"back[- ]?end", r"backend"],
    "mobile":      [r"mobile", r"\bios\b", r"\bandroid\b", r"app developer"],
    "web":         [r"\bweb\b"],
    "saas":        [r"\bsaas\b"],
    "erp/hris":    [r"\bhris\b", r"\berp\b", r"payroll", r"inventory", r"warehouse"],
    "lms":         [r"\blms\b", r"learning management"],
}

# Profile's strongest domains (grounded in master CV experience).
PROFILE_DOMAINS = ["fullstack", "frontend", "backend", "mobile", "web", "erp/hris", "lms"]

# --- Soft keywords ---
SOFT_KEYWORDS = {
    "agile/scrum":  [r"\bscrum\b", r"\bagile\b"],
    "oop":          [r"\boop\b", r"object[- ]oriented"],
    "testing":      [r"testing", r"unit tests?", r"\bqa\b"],
    "code review":  [r"code\s*reviews?", r"peer\s*reviews?"],
    "mentoring":    [r"mentor", r"coach"],
    "documentation": [r"document"],
    "performance":  [r"performance", r"optimi[sz]ation", r"scalab"],
    "security":     [r"security", r"secur(ed|ing)"],
    "collaboration": [r"collaborat", r"cross-functional"],
}

SENIORITY_JUNIOR = [r"\bjunior\b", r"entry[- ]level", r"\bgraduate\b", r"\binternship\b", r"\btrainee\b"]
SENIORITY_MID = [r"\bmid[- ]?level\b", r"\bmiddle\b", r"\bintermediate\b", r"\bengineer\s*ii\b"]
SENIORITY_SENIOR = [r"\bsenior\b", r"\bstaff\b", r"\bprincipal\b", r"\blead\b", r"\barchitect\b", r"\bexpert\b"]

# Dealbreakers per CLAUDE.md: salary floor IDR 8,000,000/month; foreign-language
# requirement not in the candidate's language table (only EN/ID declared).
FOREIGN_LANGS = ["german", "danish", "japanese", "korean", "mandarin", "chinese",
                 "french", "spanish", "dutch", "swedish", "norwegian", "finnish",
                 "thai", "vietnamese", "russian", "polish"]

SALARY_FLOOR_USD = 600  # ~IDR 8jt/month equivalent
SALARY_FLOOR_IDR = 8_000_000


def read_profile_text() -> str:
    parts = []
    for src in SOURCES:
        if src.exists():
            parts.append(src.read_text(encoding="utf-8"))
    if not parts:
        raise FileNotFoundError(
            "No profile source found. Expected one of:\n  " +
            "\n  ".join(str(s) for s in SOURCES))
    return "\n".join(parts).lower()


def find_keywords(text: str, table: dict, aliases: dict = None) -> tuple[list, list]:
    """Return (matched, missing) canonical keywords found in text."""
    aliases = aliases or {}
    matched, missing = [], []
    for kw, patterns in table.items():
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            matched.append(kw)
        else:
            missing.append(kw)
    return matched, missing


def jd_tech_keywords(jd_text: str) -> tuple[list, list]:
    """Tech keywords mentioned in the JD (any of them)."""
    matched, missing = [], []
    for kw, patterns in TECH_KEYWORDS.items():
        if any(re.search(p, jd_text, re.IGNORECASE) for p in patterns):
            matched.append(kw)
        else:
            missing.append(kw)
    return matched, missing


def score_tech(jd_text: str, profile_text: str):
    """Out of all tech keywords found in the JD, how many survive in profile?"""
    jd_kw, _ = jd_tech_keywords(jd_text)
    if not jd_kw:
        return 0, [], [], []
    matched, missing = [], []
    for kw in jd_kw:
        aliases = PROFILE_ALIASES.get(kw, [kw])
        if any(a in profile_text for a in aliases):
            matched.append(kw)
        else:
            missing.append(kw)
    ratio = len(matched) / len(jd_kw)
    return round(ratio * W_TECH), matched, missing, jd_kw


def score_seniority(jd_text: str):
    """Seniority fit: full points for junior/mid; penalize senior-only roles."""
    def has(patterns):
        return any(re.search(p, jd_text, re.IGNORECASE) for p in patterns)

    if has(SENIORITY_SENIOR):
        # Senior lead-in outranks a stray word like "mentor junior devs".
        return int(W_SENIORITY * 0.4), "senior-only (dealbreaker risk)"
    if has(SENIORITY_JUNIOR) or has(SENIORITY_MID):
        return W_SENIORITY, "junior/mid"
    return int(W_SENIORITY * 0.8), "unspecified (assume ok)"


def score_domain(jd_text: str, profile_text: str):
    """Role/domain overlap between JD and grounded profile domains."""
    matched, missing = [], []
    for dom in PROFILE_DOMAINS:
        patterns = DOMAIN_KEYWORDS.get(dom, [])
        in_jd = any(re.search(p, jd_text, re.IGNORECASE) for p in patterns)
        in_prof = dom in profile_text
        if in_jd and in_prof:
            matched.append(dom)
        elif in_jd:
            missing.append(dom)
    if not matched:
        return 0, matched, missing
    return round((len(matched) / (len(matched) + len(missing))) * W_DOMAIN), matched, missing


def score_soft(jd_text: str, profile_text: str):
    matched, missing = [], []
    for kw, patterns in SOFT_KEYWORDS.items():
        in_jd = any(re.search(p, jd_text, re.IGNORECASE) for p in patterns)
        in_prof = kw.split("/")[0] in profile_text
        if in_jd and in_prof:
            matched.append(kw)
        elif in_jd:
            missing.append(kw)
    total = matched + missing
    if not total:
        return int(W_SOFT * 0.7), matched, missing  # nothing mentioned -> neutral
    return round((len(matched) / len(total)) * W_SOFT), matched, missing


def check_dealbreakers(jd_text: str) -> list:
    """Return list of dealbreaker strings hit by the JD (or empty)."""
    hits = []
    low = jd_text.lower()
    for lang in FOREIGN_LANGS:
        if re.search(r"\b" + lang + r"\b", low):
            hits.append(f"Requires foreign language: {lang}")
    # 1. IDR with juta / jt
    for m in re.finditer(r"(?:idr|rp\.?)?\s*(\d+(?:[.,]\d+)?)\s*(?:jt|juta)\b", low):
        val = float(m.group(1).replace(",", ".")) * 1_000_000
        if val < SALARY_FLOOR_IDR:
            hits.append(f"Salary below floor: IDR {val:,.0f} < IDR {SALARY_FLOOR_IDR:,}")
    # 2. Standard IDR / Rp (e.g. IDR 12.000.000 or Rp 6.000.000)
    for m in re.finditer(r"(?:idr|rp\.?)\s*(\d{1,3}(?:[.,]\d{3}){1,3})", low):
        raw = re.sub(r"[.,]", "", m.group(1))
        val = float(raw)
        if val < SALARY_FLOOR_IDR:
            hits.append(f"Salary below floor: IDR {val:,.0f} < IDR {SALARY_FLOOR_IDR:,}")
    # 3. USD with k (e.g. $1.2k, USD 0.5k)
    for m in re.finditer(r"(?:usd|\$)\s*(\d+(?:[.,]\d+)?)\s*k\b", low):
        val = float(m.group(1).replace(",", ".")) * 1_000
        if val < SALARY_FLOOR_USD:
            hits.append(f"Salary below floor: USD {val:g}/month < USD {SALARY_FLOOR_USD}")
    # 4. Standard USD (e.g. USD 500, $400, $1,200)
    for m in re.finditer(r"(?:usd|\$)\s*(\d{1,3}(?:,\d{3})*|\d+)(?!\s*k\b)", low):
        val = float(m.group(1).replace(",", ""))
        if 100 <= val < SALARY_FLOOR_USD:
            hits.append(f"Salary below floor: USD {val:g}/month < USD {SALARY_FLOOR_USD}")
    # Onsite-only cities outside Yogyakarta/remote
    if re.search(r"onsite[- ]only|on[- ]?site\s*required", low) and \
       not re.search(r"yogyakarta|remote|hybrid|jakarta", low):
        hits.append("Onsite-only outside Yogyakarta")
    return hits


def verdict(score: int, dealbreakers: list, min_score: int) -> str:
    if dealbreakers:
        return "REJECT (dealbreaker)"
    if score >= min_score + 20:
        return "APPLY"
    if score >= min_score:
        return "APPLY (with tailoring)"
    if score >= min_score - 15:
        return "CAUTION (big gaps)"
    return "REJECT (low fit)"


def main():
    ap = argparse.ArgumentParser(description="ATS-style JD vs profile scorer")
    ap.add_argument("jd", nargs="?", help="Job description text (or omit with --file)")
    ap.add_argument("--file", help="Path to a file with JD text")
    ap.add_argument("--json", action="store_true", help="Output JSON instead of text")
    ap.add_argument("--min-score", type=int, default=55, help="APPLY threshold (default 55)")
    args = ap.parse_args()

    if args.file:
        jd_text = Path(args.file).read_text(encoding="utf-8")
    elif args.jd:
        jd_text = args.jd
    else:
        ap.error("Provide JD text or --file")

    try:
        profile_text = read_profile_text()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    tech_n, tech_match, tech_miss, jd_tech = score_tech(jd_text, profile_text)
    sen_n, sen_note = score_seniority(jd_text)
    dom_n, dom_match, dom_miss = score_domain(jd_text, profile_text)
    soft_n, soft_match, soft_miss = score_soft(jd_text, profile_text)
    dealbreakers = check_dealbreakers(jd_text)

    # Route through Laya/rules for optimal CV variant
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    try:
        import laya_router
        routing = laya_router.route_job(jd_text)
    except Exception:
        routing = {"category": "fullstack", "cv_pdf_path": "my_profile/CV - Ismail_Nur_Alam.pdf", "drive_link": None}

    total = tech_n + sen_n + dom_n + soft_n
    v = verdict(total, dealbreakers, args.min_score)

    report = {
        "score": total,
        "max_score": 100,
        "verdict": v,
        "routing": routing,
        "breakdown": {
            "tech_stack": {"score": tech_n, "weight": W_TECH,
                            "jd_keywords": jd_tech,
                            "matched": tech_match, "missing": tech_miss},
            "seniority": {"score": sen_n, "weight": W_SENIORITY, "note": sen_note},
            "domain":    {"score": dom_n, "weight": W_DOMAIN,
                          "matched": dom_match, "missing": dom_miss},
            "soft":      {"score": soft_n, "weight": W_SOFT,
                          "matched": soft_match, "missing": soft_miss},
        },
        "dealbreakers": dealbreakers,
        "tailoring_focus": tech_miss[:8],
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        sys.exit(0)

    # --- Human-readable report ---
    print("=" * 62)
    print("ATS MATCH REPORT")
    print("=" * 62)
    print(f"SCORE: {total}/100 -> {v}")
    if "routing" in report and report["routing"].get("category"):
        rt = report["routing"]
        print(f"CV Variant   : {rt['category'].upper()} ({rt.get('cv_pdf_path')})")
        if rt.get("drive_link"):
            print(f"Drive CV Link: {rt['drive_link']}")
    print("-" * 62)
    b = report["breakdown"]
    print(f"[Tech stack   {tech_n:>3}/{W_TECH}]  "
          f"matched: {', '.join(tech_match) or '-'}")
    if tech_miss:
        print(f"{'':16}missing: {', '.join(tech_miss)}")
    print(f"[Seniority    {sen_n:>3}/{W_SENIORITY}]  {sen_note}")
    print(f"[Domain       {dom_n:>3}/{W_DOMAIN}]  "
          f"matched: {', '.join(dom_match) or '-'}")
    if dom_miss:
        print(f"{'':16}jd-only: {', '.join(dom_miss)}")
    print(f"[Soft         {soft_n:>3}/{W_SOFT}]  "
          f"matched: {', '.join(soft_match) or '-'}")
    print("-" * 62)
    if dealbreakers:
        print("DEALBREAKERS:")
        for d in dealbreakers:
            print(f"  - {d}")
        print("-" * 62)
    if tech_miss:
        print("TAILORING FOCUS (grounded keywords from CV to emphasize):")
        for t in tech_miss[:8]:
            print(f"  - {t}")
        print("-" * 62)
    print("Sources: cv/master_ismail.tex, my_profile/cv_master_text.txt")


if __name__ == "__main__":
    main()
