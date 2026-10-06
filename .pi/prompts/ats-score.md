# /ats-score — Deterministic Job Fit Score

Args: `$ARGUMENTS` = JD text or URL.

1. Resolve JD text (fetch URL if needed) and save to `/tmp/jd.txt`.
2. Run: `python3 tools/ats_scorer.py --file /tmp/jd.txt`
3. Report: score/verdict → dealbreakers → matched/missing keywords →
   tailoring focus. Recommend `/tailor-cv` when verdict is APPLY.
4. Never inflate the score; the tool is keyword-based and imperfect — say so.
