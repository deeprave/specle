# Remove spec stamp prefix

## Problem

Timestamp-prefixed change directories are cumbersome to name and reference, while the timestamp itself belongs in durable state. “Spec” is also overloaded between the work-item directory and its `spec.md` document.

## Goal

Use short unique change slugs across active and archived collections, record creation and activation time in `status.json`, update all tracked repository state, and call work items “changes”. Rename the `spec` creation skill to `define` while retaining its unselected-change creation behaviour.

## Direction

Replace `.specle/specs/` with `.specle/changes/` as the active collection and retain `.specle/archive/` for completed work. Enforce slug uniqueness across both and update every tracked reference without compatibility aliases or external-installation migration support. Add schema-validated `created_at` and nullable `activated_at` timestamps. Rename `spec-status` to `change-status`, machine-readable relationship and outcome fields to use `change`, and the local selector to `current-change`. Rename the distributable skill, its metadata, lifecycle declarations, references, and installed mirror, but leave uses of `spec.md` intact.

## Verification

Test slug creation and cross-collection collision rejection, status timestamp validation and activation preservation, named-command resolution, tracked-reference updates, skill/index consistency, and blueprint plus installed-target validation.
