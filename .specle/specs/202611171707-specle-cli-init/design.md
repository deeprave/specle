# Technical design: Specle CLI initialisation

## Overview

Replace the current per-skill `install` and current-directory `update` commands with one explicit-target command:

```text
specle init <target-directory> [--force]
```

The target must already exist and resolve to a directory. Initialisation installs only the packaged skill and steering inventories beneath `<target>/.agents/`; it does not install `.agents/AGENTS.md`, `.agents/project/`, `.specle/`, a shell launcher, or any client integration. The index is generated as part of successful initialisation through reusable inventory code, but no standalone `index` command exists in this change.

## Architecture

```text
argparse: init <target> [--force]
        |
        v
async main() -- anyio.to_thread.run_sync --> initialise_distribution()
                                                    |
                                                    +-- discover packaged skills + steering
                                                    +-- validate metadata and build index data
                                                    +-- preflight exact managed destinations
                                                    +-- create all temporary siblings
                                                    +-- replace managed skills and steering
                                                    +-- replace generated index last
```

`main.py` owns synchronous argument parsing and dispatches filesystem work through the existing AnyIO entry point. `inventory.py` owns discovery, metadata parsing, installation planning, staging, replacement, and index construction. The public CLI exposes only `init`; the existing `install` and `update` commands are removed rather than retained as undocumented compatibility commands.

## Distribution layout and ownership

For a target `/work/example`, the managed destinations are:

```text
/work/example/.agents/
  skills/
    <every packaged Specle skill>/SKILL.md
    specle/index.json
  steering/
    <every packaged steering Markdown file>
```

The package source consists only of `src/specle/skills/` and `src/specle/steering/`. The portable `.agents/AGENTS.md` entry point and all project guidance are out of scope for this initialiser. This follows the distribution boundary: skills and steering are Specle-owned; `.agents/project/` and `.specle/` are never planned, preflighted as replaceable, or written.

The same layout applies when the supplied target is the user's home directory, yielding `~/.agents/`. No project is inferred from that user-level installation.

## Initialisation plan and replacement

`initialise_distribution(source_root, target_directory, force)` accepts injectable source and target paths for tests. It expands and resolves the target, requires an existing directory, and derives its `.agents` destination paths.

It discovers every source skill directory and every steering Markdown file. Each skill must pass the existing name and `specle_group` validation. The preflight enumerates the exact managed destinations: each packaged skill directory, each packaged steering file, and `skills/specle/index.json`.

Without `--force`, any existing exact managed destination raises an installation error before the initialiser creates directories, temporary files, or writes target content. Unrelated skill directories and all project-owned paths are not destinations and are left untouched.

With `--force`, each managed destination is staged as a temporary sibling in the same parent directory. After every temporary sibling and the future index have been created successfully, each destination is replaced in this order: skills, steering files, then the index. Replacing a destination means creating its temporary sibling first, deleting the old destination only after staging succeeds, and renaming the temporary sibling into place. The index is always replaced last, so a preparation or earlier replacement failure cannot replace a previous index with a partial inventory.

Temporary paths use a unique `.specle-tmp-*` name and are cleaned up on preparation failure. Existing unrelated skill directories are preserved; `--force` authorises replacement only of a colliding packaged skill directory.

## Skill index

Create a reusable `build_skill_index()` service separate from CLI dispatch. It accepts validated skill metadata and the target skills root, returning JSON-compatible data. A later `index` command will call the same service after reading installed skills.

The generated resource has this shape:

```json
{
  "groups": [
    {
      "name": "Planning",
      "skills": [
        {
          "name": "spec",
          "specle_group": "Planning",
          "description": "Create normal feature specifications.",
          "usage": "Use to start a normal unit of work.",
          "resource": "file:///work/example/.agents/skills/spec/SKILL.md"
        }
      ]
    }
  ]
}
```

The builder includes only non-empty `specle_group` skills, uses the established Specle group order with unfamiliar groups following in lexical order, sorts skills by name within a group, and derives filesystem resource identifiers from the installed target path. Frontmatter parsing is extended to obtain the existing `description` and `usage` values without adding a general YAML dependency.

During init, the index is built from the validated source metadata and the planned installed paths, then written into the staged `specle` skill directory. It is therefore present as soon as that directory is installed, while its builder remains reusable by later work.

## Errors and output

| Condition | Result |
| --- | --- |
| Missing or non-directory target | Clear CLI error; no paths created. |
| Missing packaged skill or steering source | Clear packaging error; no target changes. |
| Invalid skill metadata | Clear metadata error naming the source; no target changes. |
| Managed destination exists without `--force` | Clear collision error naming the destination; no target changes. |
| Staging/index construction fails | Remove temporary siblings; leave managed destinations and previous index unchanged. |
| Replacement fails | Report the destination; leave the index unchanged unless its own replacement succeeded. |

On success, print the managed destinations installed or replaced. The command does not report or manipulate project-owned paths.

## Package resources

The packaged-resource lookup expands from skills-only discovery to a distribution root that also exposes `steering/`. Package configuration must ensure both directories are included in built distributions, not merely present in an editable checkout.

## Test strategy

- Parser tests: `init` requires its target argument, accepts `--force`, and rejects the removed commands.
- Inventory tests: complete skill and steering discovery, target validation, source metadata validation, and stable index group ordering and fields.
- Initialisation tests: fresh project target, user-home-like target, index resource contents, and no current-directory fallback.
- Ownership tests: retain existing `.agents/project/`, `.specle/`, and unrelated skill directories.
- Force tests: collision preflight makes no writes without `--force`; forced replacement changes only exact managed destinations.
- Failure tests: staging or index-building failure leaves the prior index intact and removes temporary siblings.
- Run `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run ty check` before verification.
