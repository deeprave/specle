---
name: document-validation
specle_group: Quality
description: >-
  Validate Specle source documentation for Markdown structure, spelling, style, and lifecycle consistency.
usage: >-
  Use when checking or tuning README, docs, or blueprint Markdown locally; it validates only the source documentation inventory and does not change lifecycle state or CI.
---

# Validate source documentation

Validate Specle's source documentation inventory locally:

- `README.md`
- `docs/**/*.md`
- `src/specle/blueprints/**/*.md`

Do not validate installed `.agents/` copies, `.specle/` runtime artefacts, or arbitrary files outside this inventory.

## Workflow

1. Read the repository-owned Markdownlint, CSpell, and Vale configuration before running a check. Confirm that Markdownlint and CSpell use the established UK/AU spelling and Markdown conventions; Vale findings are advisory.
2. For a full run, execute:

   ```console
   markdownlint-cli2 README.md 'docs/**/*.md' 'src/specle/blueprints/**/*.md'
   cspell lint README.md docs 'src/specle/blueprints/**/*.md' --no-progress
   vale --no-exit README.md docs src/specle/blueprints
   uv run --frozen specle validate . --verbose
   ```

3. For a selected-file run, require that every named file is within the source documentation inventory. Run Markdownlint, CSpell, and Vale on those files with the same repository configuration. Still run `uv run --frozen specle validate . --verbose` when the selected files include blueprint skills or policies, because lifecycle declarations are inventory-wide.
4. Treat Markdownlint, CSpell, and `specle validate` failures as blocking local validation failures. Report each tool's actionable diagnostics without changing files or lifecycle state.
5. Present Vale findings separately as advisory suggestions. Do not call them failures or automatically rewrite prose.
6. When a finding exposes a genuine repository convention, update the narrowest relevant repository-owned configuration or dictionary entry, explain why it is justified, and re-run the same validation. Do not suppress broad categories of checks merely to make current files pass.

## Boundaries

- Do not install tools, add dependencies, create a CI workflow, or modify GitHub Actions.
- Do not treat validation as a substitute for `verify` on an implementation change.
- Do not change `.specle/current-spec`, a spec status, or project runtime artefacts.
- Do not expand the source inventory without an explicit requirement.

## Output

Report:

- blocking results for Markdownlint, CSpell, and lifecycle validation;
- advisory Vale findings, if any;
- the validated scope; and
- any configuration change made to recognise an intentional project convention.
