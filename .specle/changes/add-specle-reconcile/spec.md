# Add Specle reconcile

## Problem

Branch merges can leave active and archived copies of one stable spec name. Existing validation can detect the conflict, but agents need a safe, evidence-based way to understand and resolve it.

## Goal

Add `specle reconcile <spec-name>` as a read-only-by-default, machine-readable diagnostic and explicitly confirmed recovery operation.

## Direction

The command will compare both durable copies, inventory and diff artifacts, inspect local Git history, and present conservative candidate remedies. Ordinary workflows block on ambiguity. Apply modes are explicit, confirmation-gated, staged, and restricted to a user-selected winner; divergent copies never resolve automatically.

## Verification

Test duplicate detection, read-only reports, exact-copy remediation, divergent-copy blocking, failure recovery, and restored validation after resolution.
