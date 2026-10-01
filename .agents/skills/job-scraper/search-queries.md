# Search Queries for Job Scraper

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first:
- `linkedin-search`
- `freehire-search`
- (and any additional portal added via `/add-portal`)

## Query Categories

### Priority 1: Fullstack / Software Engineer (Junior – Mid)
These match your strongest core stack: Next.js, TypeScript, Go, PostgreSQL.

```text
site:linkedin.com/jobs "Software Engineer" (TypeScript OR Go OR Next.js) Indonesia
site:linkedin.com/jobs "Fullstack Developer" (Next.js OR React) Indonesia
site:linkedin.com/jobs "Junior Fullstack" OR "Junior Software Engineer" Indonesia
site:linkedin.com/jobs "Software Engineer" remote Indonesia
```

### Priority 2: Backend Engineer (Go / Node.js)
Focused on Go (Golang), Express/Node.js, Spring Boot, and PostgreSQL.

```text
site:linkedin.com/jobs "Backend Engineer" (Golang OR Go OR Node.js) Indonesia
site:linkedin.com/jobs "Backend Developer" Go remote
site:linkedin.com/jobs "Junior Backend Developer" Indonesia
```

### Priority 3: Mobile & Frontend (Flutter / React / Swift)
Mobile app development and modern web apps.

```text
site:linkedin.com/jobs "Flutter Developer" Indonesia
site:linkedin.com/jobs "Mobile Developer" (Flutter OR "React Native") Indonesia
site:linkedin.com/jobs "Frontend Developer" (Next.js OR React) Indonesia
```

### Priority 4: Global / APAC Remote (English-speaking)
Junior to Mid remote roles with international teams.

```text
site:linkedin.com/jobs "Software Engineer" remote "Southeast Asia"
site:linkedin.com/jobs "Full Stack Developer" remote worldwide (React OR Go OR TypeScript)
```

## Filters & Constraints

### 1. Compensation Gate
- **Minimum Base Salary:** **IDR 8.000.000 / month** (atau equivalent ~$550–$600+ USD/month untuk remote/international).
- Lowongan di bawah batas minimum ini akan ditandai atau diexclude dari prioritas apply.

### 2. Experience Level
- **Target:** Junior, Associate, Mid-level (1 - 4 years experience).
- **Exclude / Flag:** Lead, Principal, Director, Staff roles requiring 7+ years.

### 3. Location Filter
- **Remote:** Worldwide, APAC, Indonesia.
- **Onsite / Hybrid:** Yogyakarta (lokasi domisili) atau Jakarta / Bandung jika sistem hybrid memungkinkan.

### 4. Language Filter
- English & Indonesian. Lowongan yang mewajibkan bahasa asing lain yang tidak dikuasai (misal: Mandarin fluent, German C1) akan di-exclude.

### 5. Date Filter
- Lowongan diposting dalam 14 hari terakhir.
