# /social-search — Social Media Job Discovery

You discover fresh job postings on social media (LinkedIn, Threads, X) for
Ismail Nur Alam. Args: `$ARGUMENTS` = optional focus (category/platform/location),
e.g. "backend remote", "threads fullstack", "" (default: all).

## Steps

1. **Build queries:**
   ```bash
   python3 tools/social_search.py [--platform X] [--category Y] [--loc Z]
   ```
   Categories: fullstack | backend | frontend | mobile | all
   Platforms: linkedin | threads | x | web ; Loc: indonesia | remote | global
2. **Run searches** using google_search / web_search with the generated
   queries — batch 3-5 queries per round; do not hammer.
3. **Inspect hits.** For each promising post: open, extract JD text verbatim
   into `/tmp/jd_<n>.txt`.
4. **Score each:**
   ```bash
   python3 tools/ats_scorer.py --file /tmp/jd_<n>.txt --json
   ```
5. **Dedupe** against `.agents/skills/job-scraper/seen_jobs.json`
   (use tools/job_key.py logic).
6. **Report table** to user: Company | Role | Platform | Score | Verdict | Link.
   Recommend top 2-3 for /tailor-cv. Do not contact or apply automatically.
