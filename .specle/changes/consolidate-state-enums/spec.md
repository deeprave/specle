# Consolidate state enums

Specle currently spreads change-status and change-kind validation between an open-ended JSON Schema, lifecycle metadata tuples, and runtime checks. This can let arbitrary status strings appear as schema-valid change state. Define string-valued enum classes for top-level change status and kind, and centralise each value's validation and conversion in its enum.

Align the versioned change-status schema and lifecycle/frontmatter consumers with those definitions. Preserve the existing string wire representation and valid recorded states, while diagnosing unsupported status and kind values. The initial kinds include `change`, `bugfix`, `refactor`, `spike`, `docs`, and `release`; this intentionally replaces the documented acceptance of unknown kinds with a closed supported vocabulary.

Also define a string-valued enum covering all packaged Specle-managed skills, and consolidate relevant runtime skill-name references around it. Keep the enum aligned with packaged inventory, skill directories and metadata, dependencies, lifecycle references, and generated indexes, with actionable detection of inconsistencies. This makes a future coordinated rename, such as adding a `specle-` prefix to avoid collisions, easier; the current change retains existing names, paths, and collision and unrelated-skill behaviour. Design must establish how the enum and distribution stay aligned as the skill inventory changes.

The schema compatibility/versioning approach and treatment of any incompatible existing records must be established during design without casually rewriting immutable archives. Delivery events and all other JSON keys and specialised nested fields remain out of scope. This is unselected, independent work; it does not alter the current changes-listing delivery or require it as a dependency.

Verification should cover enum conversion and rejection, schema and runtime agreement, existing records, CLI diagnostics, unchanged delivery-event behaviour, skill inventory coverage and drift, and unchanged installation and update behaviour.
