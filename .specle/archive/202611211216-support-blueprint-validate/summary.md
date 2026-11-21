# Summary: Validate Specle blueprints directly

## Summary

Specle now validates its packaged skill blueprints directly as part of the required Verify check, while installed targets are checked against that same inventory for missing or modified managed content.

## Outcome

Maintainers can detect invalid blueprint metadata, lifecycle declarations, generated index data, and incomplete package inventories before distribution. Repository owners can validate an installed Specle target and receive actionable diagnostics when its managed skills or policy documents have drifted.

## What changed

- Added `specle validate --blueprint` with verbose inventory and lifecycle reporting.
- Consolidated blueprint and installed-target inspection behind one managed-inventory scan that records metadata, checksums, lifecycle analysis, and package-completeness diagnostics.
- Added managed-policy ownership markers so only top-level package-owned Markdown policies participate in installation, comparison, and obsolete-file cleanup.
- Made the Test workflow's Verify job validate the packaged blueprints directly, leaving document validation focused on documentation checks.

## Key decisions and limits

Package policies remain a small, top-level Markdown-only collection. Unmarked policies and skills remain outside Specle's managed inventory.
