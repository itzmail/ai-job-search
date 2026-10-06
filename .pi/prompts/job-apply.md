# /job-apply — Unified End-to-End Application Workflow

You orchestrate the complete job application pipeline in a single flow:
Job Discovery → Laya CV Routing → ATS Scoring → Approval Gate → CV Tailoring & Email Draft in Gmail.

Arguments: `$ARGUMENTS` (e.g. `"backend remote"`, `"threads fullstack"`, or direct JD text / URL).

---

## Step 1: Input & Discovery

1. **If `$ARGUMENTS` is a direct JD or URL**:
   - Fetch URL if needed, save JD to `/tmp/current_jd.txt`, and proceed directly to Step 2.
2. **If `$ARGUMENTS` is a search query or empty**:
   - Generate query list with:
     ```bash
     python3 tools/social_search.py --category all --loc remote --limit 5
     ```
   - Run 2-3 search rounds via `google_search` / `web_search` for fresh job openings.
   - For the top 2-4 promising hits, fetch the JD text and save each to `/tmp/jd_1.txt`, `/tmp/jd_2.txt`, etc.

---

## Step 2: Laya Semantic Routing & ATS Scoring

For each candidate JD:
1. Run Laya router to classify category & select CV variant + Google Drive link:
   ```bash
   python3 tools/laya_router.py --file /tmp/jd_1.txt --json
   ```
2. Run ATS Scorer:
   ```bash
   python3 tools/ats_scorer.py --file /tmp/jd_1.txt --json
   ```
3. Skip any JD hitting dealbreakers (salary floor, foreign languages).

---

## Step 3: Human Approval Checkpoint (STOP & ASK)

Present the scored opportunities in a concise table:

```
| # | Company | Role | CV Variant | Score | Verdict | Drive CV Link |
|---|---|---|---|---|---|---|
| 1 | Acme Corp | Go Backend Engineer | BE | 93/100 | APPLY | [BE CV Drive Link] |
| 2 | Beta Inc | Fullstack Developer | Fullstack | 88/100 | APPLY | [Fullstack CV Link] |
```

**STOP HERE.** Ask the user: *"Which job do you want to prepare the application for? (e.g. '1', 'Acme', or 'all')*"

---

## Step 4: Grounded CV Tailoring & Audit

Once the user selects a job:
1. Generate the tailored CV LaTeX:
   ```bash
   python3 tools/tailor_cv.py --jd /tmp/jd_<selected>.txt --company "<Company>" --role "<Role>"
   ```
2. The tool automatically audits that **every bullet point exists verbatim** in `cv/master_ismail.tex`.

---

## Step 5: Draft Email in Gmail (Safe Drafts Only)

1. Generate the grounded email body with the correct Google Drive CV link:
   ```bash
   python3 tools/email_drafter.py --jd /tmp/jd_<selected>.txt --company "<Company>" --role "<Role>" --to "<HR_Email>"
   ```
2. If Gmail client is authenticated (`token.json` exists), create the draft directly in user's Gmail box:
   ```bash
   python3 tools/gmail_client.py draft --to "<HR_Email>" --subject "Application: <Role> — Ismail Nur Alam" --body /tmp/email_draft.txt
   ```
3. Report success to the user:
   - Tailored CV file: `cv/main_<company>_<role>.tex`
   - Google Drive CV Link included in email
   - Draft ready in **Gmail Drafts** folder for final human review & send.
