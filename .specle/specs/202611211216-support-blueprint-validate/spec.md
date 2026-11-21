# Support blueprint validate

## Problem

The `validate` CLI is an installed-target validator, but repository document validation invokes it against a tracked active mirror. That does not directly validate the source blueprints which define Specle’s workflows.

## Goal

Keep installed-target validation as the default, strengthen it to identify managed-inventory drift, and add `specle validate --blueprint` for direct package-inventory and lifecycle validation.

## Direction

Both modes use one inventory operation over their respective distribution roots. It performs the only managed-skill traversal, returning parsed metadata, dependency validation, resource checksums, package-completeness and policy-ownership diagnostics, and lifecycle graph analysis together. Index generation, installation, installed-target validation, and future reconciliation or lifecycle rendering consume this result rather than independently discovering skills. Installed mode compares its records with records scanned from the resolved package blueprint and reports missing, unexpected, or checksum-drifted content, including every expected skill when the installed managed inventory is empty. Package policies are marker-owned top-level Markdown files; unmarked user policy files and skills remain outside comparison and removal. Both validation modes present scanner failures as concise diagnostics. The Test workflow runs blueprint mode as part of Verify; the document-validation workflow stops running the installed-target command.

## Verification

Test equivalent blueprint and installed inventory records, checksum drift, empty and marker-stripped installed inventories, marker-owned policy preservation, package completeness, concise source-inspection failures, incompatible command arguments, and the updated workflow semantics.
