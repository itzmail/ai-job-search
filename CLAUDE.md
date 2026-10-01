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

### Education
- **Bachelor of Information Systems** (2023–2027 Expected) - Universitas Terbuka Bandung, Indonesia

### Professional Experience
- **Fullstack Developer** (12/2024 - Present) - **PT Indoglobal Nusa Persada (Pintro)** (Yogyakarta / Remote)
  - Developed scalable web & mobile apps (Next.js, Flutter, Swift/iOS).
  - Built Golang schedulers & LMS scoring modules.
  - Optimized PostgreSQL queries and resolved N+1 bottlenecks.
  - Setup Bitbucket CI/CD pipelines for APK releases.
- **Software Engineer** (01/2024 - 12/2024) - **PT Kuantum Solusi Teknologi** (Indonesia)
  - Boosted REST API efficiency by 35% across Express.js and Spring Boot.
  - Architected OAuth 2.0 security.
  - Developed React Native & Flutter mobile applications.
- **Software Engineer (Web & Mobile)** (04/2021 - 12/2023) - **CV Mutif Corp** (Indonesia)
  - Enhanced HRIS features (payroll, payslips) boosting user satisfaction by 40%.
  - Built WMS core features, boosting tracking efficiency by 50%.
  - Built recruitment portal & QR identification web.

### Technical Skills
- **Primary:** TypeScript, Go (Golang), Next.js, React, Flutter, PostgreSQL
- **Secondary:** Java (Spring Boot), Swift (iOS), Express.js, MySQL, MongoDB, React Native
- **DevOps & Tools:** Git, Bitbucket Pipelines, CI/CD, Agile/Scrum, AI-assisted engineering workflows

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
- `cv/` - LaTeX CV variants (moderncv template, banking style)
- `cover_letters/` - LaTeX cover letters (custom cover.cls template)
- `.agents/skills/` - AI skill definitions for application workflow and portal search CLIs
- `.pi/prompts/` - Slash command prompt templates (/apply, /rank, /setup, /interview, etc.)
- `.pi/agents/` - Subagent definitions for pi-subagents

## Workflow for New Job Applications
1. User provides a job posting (URL or text).
2. **Always evaluate fit first**: skills match, experience match, compensation match, language match.
3. If good fit: create targeted CV (`cv/main_<company>_<role>.tex`) and cover letter (`cover_letters/cover_<company>_<role>.tex`).
4. **Verify both documents** (layout, content grounding against real profile).
5. Prepare interview talking points.
