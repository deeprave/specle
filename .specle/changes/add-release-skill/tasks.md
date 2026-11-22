# Tasks: Add release skill

- [x] 1. Add the repository-local release skill
  - [x] 1.1 Create `.agents/skills/release/SKILL.md` with concise release-focused frontmatter and workflow instructions; record its local-only ownership only in this change's requirements.
  - [x] 1.2 Document the read-only selected-change and open-PR preflight, including clear stop behaviour.
- [x] 2. Define release preparation
  - [x] 2.1 Document canonical PEP 440 version validation, manifest-format acceptance, and strict greater-than comparison with the checked-out `pyproject.toml`.
  - [x] 2.2 Document delivery-branch synchronisation, canonical release-branch creation, `pyproject.toml` update, and metadata-verified `uv run specle manifest src/specle/blueprints/manifest` invocation.
- [x] 3. Define the release commit boundary
  - [x] 3.1 Document the full candidate-diff display and explicit commit authorisation.
  - [x] 3.2 Document broad staging of tracked and non-ignored untracked files, one release commit, and the deliberate stop before push, PR, tags, publishing, or release creation.
- [x] 4. Verify the local workflow
  - [x] 4.1 Review the skill against all requirements, delivery policy, and managed-inventory exclusion.
  - [x] 4.2 Run applicable repository quality gates and confirm no managed blueprint or manifest resource was added for `release`.
