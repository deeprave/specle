# Complexity estimate: address security findings

## T-shirt size

**M**

## Breakdown

- **New files:** approximately 0–1 — focused regression coverage may fit existing test modules; otherwise add a dedicated validation-input test module.
- **Modified files:** approximately 5–7 — the Dependabot workflow, validation read helpers and their callers, and focused workflow/CLI tests.
- **Estimated tasks:** approximately 4–6 — establish the safe-read boundary, migrate validation reads, add regression coverage, defer the App token until the merge step, and validate the workflow semantics.
- **Key risks:** the ordinary workflow token must be sufficient for Dependabot metadata and required-check polling; regular-file checks must consistently follow intentional symlinks while rejecting special files before a read; every validation read path must use the shared boundary.

## Confidence

**Medium.** The required behaviour is narrow and evidenced by the assessment, but the exact GitHub permissions needed by `dependabot/fetch-metadata` and `gh pr checks` require design-level confirmation.

## Recommendation

Continue through design. Keep the workflow change limited to credential timing, not eligibility or ruleset policy. Centralise regular-file validation so all current and future validation readers receive the same behaviour.

## Similar past work

`202611191142-enable-automerge` introduced the required-check-gated Dependabot workflow. `202611191221-add-specle-validate` introduced installed-target validation and its runtime readers.
