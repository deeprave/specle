# Requirements: Remove dead code

## Problem

Vulture has exposed production helpers that are not reached by the Specle command-line application. Two have no references anywhere in the repository, while the remainder are invoked only by their own unit tests. Test coverage demonstrates that a helper can run, but is not evidence that the delivered product requires it.

Specle currently declares only the `specle` console command as its public package interface. No documentation or packaging metadata establishes a supported Python API for these helpers. Retaining unreachable implementation makes refactoring residue harder to identify and shifts its discovery to later review.

## Desired outcome

Remove unused production code and its obsolete tests unless there is a specific, supported reason to retain it. Make Vulture a durable pre-commit gate at a confidence level that detects this class of unused function. A versioned Python whitelist may exempt only deliberately retained, otherwise-unused production names, with each exemption justified in source.

## User stories and acceptance criteria

### 1. Remove unreachable production helpers

As a maintainer, I want unused production helpers removed, so that the package contains only behaviour needed by the delivered command-line application or an explicitly supported contract.

1. The change SHALL review the functions reported by Vulture from `src/specle/`: `selected_change`, `packaged_skills_root`, `packaged_policies_root`, `read_skill_metadata`, `discover_skills`, `discover_installed_specle_skills`, `compare_installed_distribution`, `discover_delivery_sidecars`, `validate_installed_skill_inventory`, `validate_lifecycle_graph`, `normalize_change_timestamp`, and `record_sidecar_relationship`.
2. A function with no production caller, documented supported Python API, or other concrete product requirement SHALL be removed, together with tests whose sole purpose is to exercise that removed helper.
3. The change SHALL preserve and test the observable command-line behaviour that depended on any removed internal composition.
4. Unit-test-only invocation SHALL not by itself justify retaining a production helper.

### 2. Gate future dead code

As a contributor, I want unused production code detected before review, so refactoring residue cannot quietly accumulate.

1. The pre-commit configuration SHALL run Vulture over the complete `src` and `tests` trees, independent of the staged filename set.
2. The Vulture confidence threshold SHALL detect the unused-function class identified in this change, including the default 60% findings reported from the production tree.
3. Vulture SHALL remain host-provided through pre-commit and SHALL not become a project runtime or development dependency.
4. The repository's pre-commit checks SHALL pass after the cleanup.

### 3. Keep justified exceptions explicit

As a maintainer, I want every retained unused production name to have an auditable reason, so a whitelist cannot silently conceal dead code.

1. If—and only if—a reviewed function must remain despite having no in-repository production caller, the change SHALL add a versioned Python Vulture whitelist module and include it in the hook invocation.
2. Each whitelist entry SHALL identify the exact retained name and include a nearby explanation of its concrete supported use or compatibility commitment.
3. The whitelist SHALL not exempt a function merely because tests call it or because it might be useful in a hypothetical future integration.
4. If no reviewed function meets that standard, no whitelist module SHALL be added.

## Boundaries

- This change does not establish a general supported Python API for Specle.
- It does not remove a function solely because static analysis cannot see a documented, deliberate runtime use.
- It does not lower unrelated quality gates or add Vulture to the package dependency groups.
- It does not alter lifecycle semantics, skill content, or command-line behaviour except to remove code that has no supported effect.
