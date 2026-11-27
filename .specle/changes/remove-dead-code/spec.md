# Remove dead code

## Motivation

Vulture's 60% analysis reports internal helpers that are not reached by the delivered `specle` command. The existing 100% pre-commit threshold is useful for certain unambiguous findings, but does not catch this dead-function class. The repository has no supported Python API contract for these names.

## Goal

Remove production helpers that have no concrete current purpose, retain only demonstrably required exceptions, and make Vulture prevent equivalent residue from returning before review.

## Scope and approach

Audit the reported functions against command-line composition, package metadata, documentation, and supported compatibility commitments. Delete helpers and test cases that exist only to exercise deleted helpers, while preserving end-to-end and observable behaviour coverage.

Configure the existing pre-commit Vulture integration to scan `src` and `tests` independently of staged filenames at the confidence level needed to detect these 60% unused-function reports. Keep the tool supplied by pre-commit rather than the project environment.

Only when a concrete retention requirement exists, add a small versioned Python whitelist module to the Vulture invocation. Each exemption must name the retained symbol and explain its supported reason; test-only use and hypothetical external use are insufficient.

## Verification

Run Vulture at the configured gate threshold across the repository, demonstrate that the reported dead helpers are removed or explicitly justified, run the complete pre-commit suite, and run the project's pytest, Ruff, formatting, type-check, and Specle validation gates. Confirm that the command-line inventory, validation, lifecycle, timestamp, and sidecar behaviours remain covered through their actual consumers.
