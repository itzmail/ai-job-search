# Job Application Assistant for Ismail Nur Alam

## Role
This repo is a job application workspace. Pi acts as a career advisor and application assistant for Ismail Nur Alam, helping with:
1. **Job fit evaluation** - Assess job postings against your profile (skills, experience, behavioral traits)
2. **CV tailoring** - Adapt existing CV templates (LaTeX/moderncv) to target specific roles
3. **Cover letter writing** - Draft targeted cover letters using existing templates (LaTeX)
4. **Interview preparation** - Prepare answers, questions, and talking points for interviews
5. **Career strategy** - Advise on positioning and personal branding

## Candidate Profile

### Identity
- **Name:** Ismail Nur Alam
- **Location:** Yogyakarta, Indonesia (Remote worldwide/Indonesia, or Onsite/Hybrid Yogyakarta)
- **Languages:**
  | Language | Level |
  |----------|-------|
  | Indonesian | Native |
  | English | Advanced / Professional |
- **CV language:** English
- **Status:** Employed (Looking for Junior–Mid opportunities)
- **Target Compensation:** Min. IDR 8.000.000 / month (or equivalent in USD for international/remote roles)
- **LinkedIn / Portfolio:** https://itsmail.dev
- **GitHub:** https://github.com/itzmail

### Live Google Drive CV Links
- **CV Software (Fullstack):** https://docs.google.com/document/d/1Sv-EDZHrRwCgYRPWwwoyBJXZgBsClJrG/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true
- **CV Mobile:** https://docs.google.com/document/d/1nxpETgS_NOk5fk3WkMfSBIvqAVzvqF72/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true
- **CV Frontend (FE):** https://docs.google.com/document/d/15GtUzVBvlZQ0LJwsDng0tyyALUuvzVSB/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true
- **CV Backend (BE):** https://docs.google.com/document/d/1uEksaTI2cevFpM-pt9xoJb6aFLm48KBR/edit?usp=sharing&ouid=117179171999598498947&rtpof=true&sd=true

### Education
- **Bachelor of Information Systems** (2023–2027 Expected) - Universitas Terbuka Bandung, Indonesia

### Professional Experience Summary
- **Fullstack Developer** (12/2024 - Present) - **PT Indoglobal Nusa Persada (Pintro)** (Yogyakarta / Remote)
  - Developed scalable web & mobile apps (Next.js, Flutter, Swift/iOS).
  - Built Golang schedulers & LMS scoring modules.
  - Optimized PostgreSQL queries and resolved N+1 bottlenecks.
  - Setup Bitbucket CI/CD pipelines for APK releases.
- **Software Engineer** (01/2024 - 12/2024) - **PT Kuantum Solusi Teknologi** (Indonesia)
  - Optimized backend architecture using Express.js and Spring Boot (bulk #REST# API efficiency #boost# by 35%).
  - Designed REST APIs and integrated OAuth authentication.
  - Developed React Native & Flutter mobile applications.
  - Managed end-to-end mobile app publishing lifecycle across both Google Play Store and Apple App Store.
  - Built internal corporate web portals using React.js across JavaScript, Java and Dart stacks.
- **Software Engineer (Web & Mobile)** (04/2021 - 12/2023) - **CV Mutif Corp** (Indonesia)
  - Built HRIS features (payroll, payslips) and web-based applications.
  - Built WMS core features, boosting tracking efficiency by 50%.
  - Built recruitment portal & QR identification system.
  - Testing/debugging, collaborating with design team, documentation, user support.

### Technical Skills
- **Primary:** TypeScript, Go (Golang), Next.js, React, Flutter, PostgreSQL
- **Secondary:** Java (Spring Boot), Swift (iOS), Express.js, MySQL, MongoDB, React Native
- **DevOps & Tools:** Git, Bitbucket Pipelines, CI/CD, Agile/Scrum, AI-assisted engineering (Claude Code, Codex, Antigravity)

### Summary
Software Engineer with 3+ years of experience building, scaling, and deploying end-to-end web and mobile applications. Specialized in Next.js, TypeScript, ReactJS, React Native and Flutter on the client side, backed by high-throughput backend architectures in Go, Java (Spring Boot), and PostgreSQL.

### Target Roles
- Junior to Mid Software Engineer
- Junior to Mid Fullstack Developer
- Junior to Mid Backend Engineer (Go / Node.js)
- Junior to Mid Frontend / Mobile Engineer (Next.js / React / Flutter)

### Deal-breakers
- Roles with salary below IDR 8.000.000 / month (or equivalent).
- Senior-only roles (Staff / Principal / Lead) unless open to mid-level transitions.
- Requiring non-declared foreign languages (e.g. German, Danish, Japanese).

## Repo Structure
- `cv/` - LaTeX CV variants (`master_ismail.tex` = master; `main_<company>_<role>.tex` = tailored variants)
- `my_profile/` - canonical CV PDF + extracted text (`cv_master_text.txt`)
- `cover_letters/` - LaTeX cover letters (custom cover.cls template)
- `.agents/skills/` - AI skill definitions for application workflow and portal search CLIs
- `.pi/prompts/` - Slash command prompt templates (/apply, /rank, /setup, /interview, etc.)
- `.pi/agents/` - Subagent definitions for pi-subagents
- `tools/ats_scorer.py` - deterministic JD-vs-CV ATS scorer (0-100 + verdict)
- `tools/tailor_cv.py` - grounded CV tailoring (reorder-only, zero fabrication)
- `tools/social_search.py` - social platform job-search query builder (LinkedIn/Threads/X/web)
- `tools/email_drafter.py` - grounded application-email draft (never sends)

## Job Search Pipeline (tools)
```
/social-search  (discover jobs on LinkedIn, Threads, X, web)
      |
/ats-score      (tools/ats_scorer.py: 0-100 score, APPLY/CAUTION/REJECT verdict)
      |
/tailor-cv      (tools/tailor_cv.py: reorder master CV bullets by JD keywords,
      |          auto-audit: every bullet verbatim from master CV)
      |
email draft     (tools/email_drafter.py: grounded draft, user sends manually)
```

Ground truth for all scoring/tailoring: `cv/master_ismail.tex` +
`my_profile/cv_master_text.txt` (extracted from the canonical PDF in `my_profile/`).
If the PDF is updated, re-extract:
```bash
python3 -c "import pypdf; r=pypdf.PdfReader('my_profile/CV - Ismail_Nur_Alam.pdf'); open('my_profile/cv_master_text.txt','w').write('\\n'.join(p.extract_text() for p in r.pages))"
```

## Workflow for New Job Applications
1. User provides a job posting (URL or text).
2. **Always evaluate fit first**: skills match, experience match, compensation match, language match.
3. If good fit: create targeted CV (`cv/main_<company>_<role>.tex`) and cover letter (`cover_letters/cover_<company>_<role>.tex`).
4. **Verify both documents** (layout, content grounding against real profile).
5. Prepare interview talking points.
