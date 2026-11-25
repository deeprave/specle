# Add client link

## Problem

Managed Specle skills live in `.agents/skills`, while individual AI clients commonly use their own configuration directories and skill discovery rules.

## Goal

Add a safe `specle link` command that exposes managed skills to explicitly selected, researched clients using relative symlinks without replacing client-owned content.

## Direction

Define client locations as package data, research each supported client's current skills convention, and link only the inventory scanned from the selected local deployment. Handle comma-separated client names, existing correct links, client-owned collisions, whole-directory links to `.agents/skills`, verbose reporting, and platform limitations. The command is additive and conservative: it never overwrites, deletes, forces, or silently copies skills.

## Verification

Test argument normalisation, client-spec lookup, managed-only linking, relative targets, correct-link idempotence, collisions, whole-directory detection, verbose output, and unsupported-link platform behaviour. Run repository quality gates.
