# Design: document-validation

## Overview

Add a local `document-validation` Specle skill and a separate pull-request workflow that check the source documentation inventory with Markdownlint, CSpell, Vale, and `specle validate`. The change supplies repository-owned configuration tuned to both agent skill Markdown and human repository documentation.

## Architecture

```text
document-validation skill
  │
  ├── source documentation inventory
  │     ├── README.md
  │     ├── docs/**/*.md
  │     └── src/specle/blueprints/**/*.md
  │
  ├── Markdownlint + repository configuration     → fail on structural defects
  ├── CSpell + repository configuration           → fail on spelling defects
  ├── specle validate <repository root>            → fail on lifecycle defects
  └── Vale + repository configuration and styles   → report advisory findings

pull-request workflow
  └── same source inventory and configuration
        ├── Markdownlint, CSpell, specle validate  → fail on diagnostics
        └── Vale                                  → show advisory suggestions

pre-commit hooks
  ├── staged source-documentation files
  │     ├── Markdownlint                           → block structural defects
  │     ├── CSpell                                → block spelling defects
  │     └── Vale                                  → show advisory suggestions
  └── specle validate .                           → validate inventory-wide lifecycle state
```

Installed `.agents/` copies and `.specle/` runtime artefacts are excluded from every documentation tool. The lifecycle command remains the existing Python CLI's responsibility; the new skill orchestrates it alongside document checks.

## Configuration design

Repository-root configuration files own the repeatable tool policy:

- Markdownlint configuration preserves unwrapped prose and supports the blueprint's YAML frontmatter and fenced examples, while retaining structural checks.
- CSpell configuration uses `en-GB`, software terminology, and a narrow, justified project dictionary.
- Vale configuration uses narrow repository-owned styles for concise instructional Markdown and remains advisory.

The validation skill and workflow own the explicit source-documentation inventory passed to every command. Shared configuration applies across skills and documentation by default. If tuning proves a genuine convention differs by scope, add a documented, narrow override rather than weakening shared checks or excluding a class of documents. The workflow installs its tools without adding project dependencies and runs no formatter or fixer.

The generated skill index is portable inventory data, not a filesystem resolver. It retains the index schema and ordered groups, but each group declares its name once and each entry contains only `name`, `description`, and `usage`. The builder, schema, tests, and committed installed index must reject or omit installation-specific resource URIs and redundant per-entry groups.

Pre-commit hooks receive staged filenames and use a source-inventory file filter, providing faster feedback than the full local or CI runs. Markdownlint and CSpell use their maintained upstream hooks; Vale uses its maintained hook and remains advisory at its configured suggestion level. `specle validate` is the single local system hook: it uses `uv run --frozen`, accepts no filenames, and always runs because lifecycle declarations can be affected by relationships across the inventory. No hook uses a formatter, fixer, or write-capable command.

## Skill behaviour

The `document-validation` skill:

1. Reads the relevant source inventory and repository-owned configurations.
2. Runs Markdownlint, CSpell, and `specle validate` with explicit paths and reports their failures as blocking local validation failures.
3. Runs Vale against the same document inventory and presents findings as advisory, grouped separately from failures.
4. Supports selected-file validation through the same configuration, so maintainers can tune a rule or dictionary without changing scope semantics.
5. Never edits content, manages dependencies, installs tools, or changes lifecycle state.

## Pull-request workflow

The workflow runs only for pull-request events. It invokes the same source-documentation inventory and repository-owned configuration as the local skill. Markdownlint, CSpell, and lifecycle diagnostics fail their steps. Vale emits advisory output and a non-zero step result when it finds suggestions; the resulting workflow check remains non-required by repository rules and separate from `Verify`.

## Language guidance

Add `language.md` to the project overlay and onboarding inventory. It records the repository's established UK/AU spelling and accepted software terminology. The document-validation configuration uses that policy but remains source-controlled and reusable without reading a target project's overlay.

## Failure handling

| Condition | Behaviour |
| --- | --- |
| Markdownlint, CSpell, or lifecycle failure | Report the tool, file or lifecycle diagnostic, and non-zero result; do not hide the failure. |
| Vale finding | Present as advisory feedback; do not fail local validation. |
| Local tool unavailable | Report the missing installed tool and stop; do not install a dependency or substitute another tool. |
| CI tool setup failure | Fail the affected workflow step with the setup diagnostic; do not add a project dependency as a workaround. |
| Configuration false positive | Identify the affected convention, tune the narrowest applicable configuration or dictionary entry, and re-run the same command. |
| Requested file outside the source inventory | Report that it is out of scope; do not silently validate installed or runtime artefacts. |
| Pre-commit Markdownlint or CSpell finding | Fail the commit with the staged-file diagnostic; do not modify the staged files. |
| Pre-commit Vale finding | Display the suggestion without blocking the commit. |
| Pre-commit lifecycle finding | Fail the commit with the inventory-wide diagnostic; do not infer safety from the changed-file list. |
| Generated index contains an installation-specific location or redundant group field | Fail lifecycle validation with an index diagnostic; regenerate the portable index from the installed inventory. |

## Test strategy

- Exercise each tool against representative skill, policy, README, and `docs/` files.
- Confirm intended conventions pass without broad disabling of checks.
- Introduce focused temporary invalid Markdown, spelling, and lifecycle fixtures or controlled inputs to confirm blocking diagnostics.
- Confirm Vale findings remain advisory.
- Confirm selected-file invocations use the same configuration and scope rules.
- Confirm the pull-request workflow runs read-only checks using the same configuration and paths, remains separate from `Verify`, and is non-required by repository rules.
- Confirm pre-commit restricts prose checks to staged source-inventory files, reuses the repository configuration, preserves advisory Vale behaviour, and runs lifecycle validation without file arguments.
- Confirm an index generated for one target validates from another target location and contains only the agreed group and entry fields.
- Run the project quality gates through `uv`: pytest, Ruff check, Ruff format check, and Ty check.
