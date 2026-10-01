---
framework_version: 1.0.0
---

# Agent Guidelines: AI Job Search

@CLAUDE.md

This workspace is structured to manage job search activities, scraper tools, CVs, cover letters, and interview preparation.

## Thin-Pointer Design (Single Source of Truth)

To prevent duplication and configuration drift across different AI agent frameworks (Pi Coding Agent, Claude Code, Google Antigravity, Codex, Cursor, Gemini CLI, etc.), this workspace uses a unified thin-pointer design. All agent runtimes should load the canonical specifications and candidate profiles from the files and directories below:

1. **Personal Candidate Profile:**
   - The candidate profile, contact details, education, and target preferences are defined in [CLAUDE.md](CLAUDE.md) and the individual profile methodology files under [.agents/skills/job-application-assistant/](.agents/skills/job-application-assistant/) (specifically `01-*.md` etc.).
2. **Canonical Workflow Specifications & Prompts:**
   - The step-by-step instructions and prompts for tasks (setup, scrape, rank, apply, upskill, interview) are defined under `.pi/prompts/` (commands) and `.agents/skills/` (skills).
   - Custom agents are defined under `.pi/agents/` (or `.agents/agents/`).
3. **Portal Search Skills:**
   - Job-portal search CLIs and application assistant skills live under [.agents/skills/](.agents/skills/) in the portable Agent Skills format (with a `SKILL.md` per skill). Pi Coding Agent and other frameworks discover these automatically.
