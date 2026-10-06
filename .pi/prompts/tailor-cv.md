# /tailor-cv — Grounded CV Tailoring

You tailor the master CV for a specific job posting. The job posting is
`$ARGUMENTS` (JD text or URL). You orchestrates three deterministic tools —
you NEVER hand-write CV content.

## Steps

1. **Get JD text** (fetch if URL). Save to `/tmp/jd.txt`.
2. **Score first** — run `python3 tools/ats_scorer.py --file /tmp/jd.txt`.
   - If verdict is REJECT or dealbreakers hit: report and STOP. Do not tailor
     a rejected posting unless the user explicitly overrides.
3. **Generate the tailored CV:**
   ```bash
   python3 tools/tailor_cv.py --jd /tmp/jd.txt --company "<company>" --role "<role>"
   ```
   Output: `cv/main_<company>_<role>.tex`, then an automatic verbatim audit
   (every bullet must exist in `cv/master_ismail.tex`). If the audit fails,
   do not deliver; report the fabricated bullet.
4. **Compile to PDF** if a LaTeX engine is available (`lualatex` preferred).
   If no engine exists, tell the user and provide the .tex path.
5. **Verify the PDF** (pages ≤ 2, no broken layout) using the existing
   verify tooling when possible (`tools/verify_pdf.py`, `tools/verify_layout.py`).
6. **Summarize to user**: score, verdict, bullets reordered, file paths.
7. **Email step (optional)** — do it only when the user asks to prepare
   sending: run
   ```bash
   python3 tools/email_drafter.py --jd /tmp/jd.txt --company "<company>" --role "<role>" --to <email>
   ```
   The draft is never sent automatically — user sends it.

## Hard rules
- Zero fabrication: bullet text, dates, company names come verbatim from
  `cv/master_ismail.tex`. The tool only reorders.
- Never send email. Always human-in-the-loop for the final send.
