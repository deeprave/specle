# Tasks: Add Specle status

- [x] 1. Add the `status` CLI entry point and read-only selected-change reporting using existing state and lifecycle readers, including missing, invalid and archived selectors and durable timestamps (`src/specle/main.py`, status reporting module).
- [x] 2. Report locally registered sidecars with labelled kind, status and next action (`src/specle/` status reporting).
- [x] 3. Inspect Git asynchronously and render branch or detached HEAD and compact porcelain status counts, preserving partial results on individual failures (`src/specle/` status reporting).
- [x] 4. Integrate and document the human-readable status output and CLI usage while preserving the read-only and no-path-disclosure boundaries (`src/specle/main.py`, relevant documentation).
- [x] 5. Summarise optional context milestones, todos and other lists with date-only grouped fields and indented lines shorter than 80 characters (`src/specle/` status reporting).
- [x] 6. Align installed and packaged status skill instructions with the CLI status and context information (`.agents/skills/status/SKILL.md`, `src/specle/blueprints/skills/status/SKILL.md`).
- [x] 7. Add Markdown source output to the status CLI with headings and grouped context bullets (`src/specle/main.py`, `src/specle/status_report.py`).
