# Tasks: document-validation

- [x] 1. Establish the source-documentation inventory and Markdownlint configuration
  - [x] 1.1 Define the repository documentation paths: `README.md`, `docs/**/*.md`, and `src/specle/blueprints/**/*.md`.
  - [x] 1.2 Add repository-owned Markdownlint configuration that supports frontmatter, fenced examples, and unwrapped prose without disabling structural checks broadly.
  - [x] 1.3 Run Markdownlint against representative inventory files and tune only justified configuration details.

- [x] 2. Establish spelling and advisory prose configuration
  - [x] 2.1 Add CSpell configuration for `en-GB`, software terminology, and a narrow project dictionary.
  - [x] 2.2 Add Vale configuration and narrow repository-owned rules suitable for concise skill and documentation prose.
  - [x] 2.3 Run CSpell and Vale against representative inventory files, resolving genuine defects and documenting any justified exceptions.

- [x] 3. Add the local document-validation skill
  - [x] 3.1 Add the canonical `document-validation` blueprint with explicit source scope, blocking checks, advisory Vale reporting, and selected-file support.
  - [x] 3.2 Synchronise the managed active skill inventory and rebuild its index.
  - [x] 3.3 Exercise full-inventory and selected-file validation, confirming installed/runtime artefacts are out of scope and `specle validate` is reused for lifecycle checks.

- [x] 4. Record language policy and onboarding support
  - [x] 4.1 Add this repository's `.agents/project/language.md` with UK/AU spelling and accepted software terminology.
  - [x] 4.2 Update canonical and active onboarding guidance to inventory and elicit `language.md` without requiring language rules in `AGENTS.md`.

- [x] 5. Verify local configuration and safeguards
  - [x] 5.1 Confirm no project dependency, lockfile, or local tool-installation step was introduced.
  - [x] 5.2 Run document validation and project quality gates through their documented commands.

- [x] 6. Remove duplicate language guidance
  - [x] 6.1 Remove the root `AGENTS.md` language directive now represented by `.agents/project/language.md`.
  - [x] 6.2 Confirm project language guidance remains the sole repository authority.

- [x] 7. Add pull-request document validation
  - [x] 7.1 Add a dedicated pull-request workflow that installs the validation tools without adding project dependencies.
  - [x] 7.2 Run Markdownlint, CSpell, and lifecycle validation with the same configuration and source-documentation inventory as the local skill.
  - [x] 7.3 Publish Vale suggestions with a non-zero advisory step result while keeping the workflow separate from `Verify` and non-required by repository rules.
  - [x] 7.4 Validate the PR-only trigger, read-only commands, and non-required delivery configuration; confirm runtime execution after delivery.

- [x] 8. Add pre-commit document validation
  - [x] 8.1 Add maintained Markdownlint, CSpell, and Vale hooks restricted to staged source-documentation files and their shared repository configuration.
  - [x] 8.2 Add an always-run local `specle validate` hook with no file arguments.
  - [x] 8.3 Confirm Markdownlint, CSpell, and lifecycle findings block commits; confirm Vale suggestions remain advisory; and confirm no hook modifies staged files.

- [x] 9. Make the generated skill index portable and minimal
  - [x] 9.1 Remove installation-specific resource URIs and redundant per-entry group fields from the index builder, model, and JSON Schema.
  - [x] 9.2 Update focused index and initialisation tests to assert the portable group-and-entry contract across different installation locations.
  - [x] 9.3 Regenerate the managed active index and confirm local and CI-equivalent lifecycle validation pass from distinct checkout paths.

- [x] 10. Reconcile pull-request validation with review findings
  - [x] 10.1 Restrict Checks API write permission to same-repository Vale reporting and preserve read-only lifecycle validation.
  - [x] 10.2 Keep local Vale and its pre-commit hook advisory while retaining CI's non-required failing signal for suggestions.
  - [x] 10.3 Run Vale safely for fork-originated pull requests without a write-dependent check reporter.
  - [x] 10.4 Align the local Markdownlint command with CI's explicit source-documentation glob and synchronise the active skill.
  - [x] 10.5 Exercise the workflow and hook configuration, then re-run document validation and project quality gates.
