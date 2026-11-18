# Complexity estimate: Specle CLI initialisation

## T-shirt size

**L**

## Breakdown

- **New files:** approximately 3–5, principally focused initialisation, index, and failure-safety tests.
- **Modified files:** approximately 5–8, including CLI parsing and dispatch, inventory services, package-resource configuration, documentation, and existing tests.
- **Estimated tasks:** 7–9 test-first tasks covering explicit target selection, full distribution planning, force preflight, staged replacement, index generation, project-content preservation, and error recovery.

## Key risks

- The current CLI installs one skill into the current directory; initialisation needs an explicit target and a complete distribution plan without retaining that unsafe default.
- Shared index generation must be usable by a later standalone `index` command while this change exposes it only through `init`.
- Temporary replacement needs a failure policy that preserves existing distribution files and never touches `.agents/project/` or `.specle/`.
- Package resources currently expose skills only; the design must establish how steering and any other distribution content are included in an installed package.
- The exact non-skill distribution contents remain an open design decision that affects the public installation contract.

## Confidence

**Medium.** The existing inventory and CLI provide a useful base, but this changes their installation model, introduces staged filesystem replacement, and requires package-resource and launcher decisions.

## Recommendation

Run `design` before task planning. Resolve the exact distribution contents, then define the installation plan, staged replacement semantics, and shared index-generation interface.

## Similar past work

`202611171130-add-skill-blueprints` established constrained skill metadata, dependency-aware individual installation, protected active skills, and the initial `argparse`/AnyIO CLI. This change replaces that per-skill current-directory workflow with complete explicit-target initialisation.
