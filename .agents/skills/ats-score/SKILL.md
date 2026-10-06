---
name: ats-score
description: >
  Scores a job description against the user's master CV using the grounded ATS
  scorer (tools/ats_scorer.py). Returns 0-100 match score, verdict
  (APPLY/CAUTION/REJECT), matched/missing keywords, dealbreaker hits, and a
  tailoring focus list. Use when the user asks: "how well does my CV fit this
  job?", "ATS score this", "job fit", "score this JD", or pastes a JD asking
  for fit analysis.
---

# ATS Score

Score job description fit with a deterministic tool — never estimate by eye.

## When to use
- User pastes a JD (or URL) and asks about fit, match, or application worthiness
- Before running /apply or /tailor-cv (the score decides whether to draft)

## Steps

1. **Get the JD text.** If it is a URL, fetch it first (google_search /
   web_fetch). Never draft from just the title.
2. **Save JD to a temp file** (e.g. `/tmp/jd.txt`).
3. **Run the scorer:**
   ```bash
   python3 tools/ats_scorer.py --file /tmp/jd.txt
   ```
   Use `--json` for machine-readable output, `--min-score 60` to change the threshold.
4. **Report to the user, in this order:**
   - Score + verdict
   - Dealbreakers first (if any — these veto everything)
   - Matched vs missing tech keywords
   - Tailoring focus (what the tailored CV should emphasize)
5. **Interpret limits.** The scorer is keyword-based, not a real ATS. Flag to
   the user that a high score means "worth applying", not "guaranteed pass".

## Hard rules
- The scorer reads ground truth from `cv/master_ismail.tex` and
  `my_profile/cv_master_text.txt`. If either is missing, stop and tell the
  user to run profile sync first.
- Never edit the JD, profile, or outputs to improve the score. The tool
  measures; the human decides.
