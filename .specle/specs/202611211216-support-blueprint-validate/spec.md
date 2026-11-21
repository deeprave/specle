# Support blueprint validate

## Problem

The `validate` CLI is an installed-target validator, but repository document validation invokes it against a tracked active mirror. That does not directly validate the source blueprints which define Specle’s workflows.

## Goal

Keep installed-target validation as the default, strengthen it to identify managed-inventory drift, and add `specle validate --blueprint` for direct package-inventory and lifecycle validation.

## Direction

Both modes use one inventory operation over their respective distribution roots. It performs the only managed-skill traversal, returning parsed metadata, dependency validation, resource checksums, and lifecycle graph analysis together. Index generation, installation, installed-target validation, and future reconciliation or lifecycle rendering consume this result rather than independently discovering skills. Installed mode compares its records with records scanned from the resolved package blueprint and reports missing, unexpected, or checksum-drifted content. Unmarked user skills remain outside comparison. The Test workflow runs blueprint mode as part of Verify; the document-validation workflow stops running the installed-target command.

## Verification

Test equivalent blueprint and installed inventory records, checksum drift, unmarked local skills, missing and unexpected managed resources, source blueprint failures, incompatible command arguments, and the updated workflow semantics.
