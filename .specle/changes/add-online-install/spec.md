# Add online install

## Problem

Installing Specle currently assumes that the developer already has `uvx` available and can invoke its CLI directly. That is inconvenient for first-time use from a remote repository page.

## Goal

Provide `install.sh` for macOS/Linux and `install.ps1` for native Windows. Each may be streamed to its native shell, requires an explicit target directory, reuses `uvx` when available, and otherwise temporarily bootstraps it through Astral's official platform-native installer before running `uvx specle init <target-directory>`.

## Direction

The scripts own platform selection, temporary bootstrap, and cleanup only. They must not duplicate Specle installation behaviour: the published package's `init` command remains responsible for managed skills, policies, index generation, collision handling, and target validation. Astral's official installers retain responsibility for operating-system and architecture archive selection, including platform-native signed executables.

## Verification

Test argument validation, existing-`uvx` delegation, platform-native Astral bootstrap invocation, delegated exit-status propagation, and temporary-directory cleanup. Confirm neither script performs a global installation or shell-configuration changes.
