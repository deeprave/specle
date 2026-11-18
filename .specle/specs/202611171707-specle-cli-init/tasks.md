# Tasks: Specle CLI initialisation

- [x] 1. Add parser tests in `tests/test_main.py` for `specle init <target-directory>`, required target validation, `--force`, and rejection of the retired `install` and `update` commands.
- [x] 2. Add distribution-discovery and metadata tests in `tests/test_inventory_metadata.py` and `tests/test_inventory_resolution.py`, covering packaged skills and steering, required `description` and `usage` metadata, and clear invalid-source failures.
- [x] 3. Add index-builder tests in a new `tests/test_inventory_index.py`, covering marked-skill filtering, established group order, lexical fallback ordering, per-group skill ordering, metadata fields, and installed `file:` resource identifiers.
- [x] 4. Implement distribution discovery and richer constrained skill-frontmatter parsing in `src/specle/inventory.py`, including reusable index construction and packaged steering-resource access.
- [x] 5. Add initialisation tests in a new `tests/test_inventory_initialisation.py` for a fresh project target, a home-like target, generated index content, required existing target directories, and no current-working-directory fallback.
- [x] 6. Implement `initialise_distribution()` in `src/specle/inventory.py`: validate the complete source inventory, preflight every exact managed destination, stage temporary siblings, and install skills, steering, and the index in the defined replacement order.
- [x] 7. Extend the initialisation tests for ownership and collision safety: preserve `.agents/project/`, `.specle/`, and unrelated skills; make a collision leave no writes without `--force`; and replace only exact managed destinations with `--force`.
- [x] 8. Add failure-path tests for staging or index-generation failure, then complete temporary-sibling cleanup and index-last replacement handling in `src/specle/inventory.py`.
- [x] 9. Replace the CLI dispatch in `src/specle/main.py` with `init <target-directory> [--force]`, run the synchronous initialiser through the AnyIO entry point, and print the installed or replaced managed destinations.
- [x] 10. Add a packaged-distribution test and adjust `pyproject.toml` resource configuration as needed so built Specle distributions include both `skills/` and `steering/`.
- [x] 11. Update `README.md` and `src/specle/AGENTS.md` to document explicit-target initialisation, the managed-content boundary, and the intentionally deferred commands and launcher.
