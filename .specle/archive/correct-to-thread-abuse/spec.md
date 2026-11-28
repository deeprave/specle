# Bugfix: Correct thread-wrapper abuse

## Bug

The asynchronous Specle CLI uses `anyio.to_thread.run_sync` to wrap ordinary filesystem reads,
writes, scans, and validation work. This has spread through `src/specle/main.py` despite the
repository convention that asynchronous code uses `await` and `anyio.Path` for filesystem work.

## Expected behaviour

Production asynchronous code performs filesystem operations through AnyIO's asynchronous path and
file APIs. It does not introduce or retain `anyio.to_thread.run_sync` as a wrapper for synchronous
filesystem operations.

## Actual behaviour

`src/specle/main.py` contains multiple `anyio.to_thread.run_sync` calls around manifest, update,
schema export, initialisation, and validation filesystem operations.

## Reproduction

Run `rg 'anyio\.to_thread\.run_sync' src/specle`. The current production matches demonstrate the
prohibited wrapper use.

## Root cause

Synchronous path-oriented helpers were retained under the asynchronous CLI and progressively
offloaded to worker threads for convenience, rather than being converted to async AnyIO path and
file operations.

## Fix approach

Convert the affected filesystem helpers and command paths in place to native asynchronous
implementations using `anyio.Path` and async file operations. Retain established function names:
the `async def` declaration and awaited call sites express their asynchronous contract, so do not
add `_async` name suffixes. Keep existing command behaviour, error contracts, atomic replacement
guarantees, and validation semantics unchanged. Do not add a source-inspection test; existing
behavioural coverage must continue to pass.

## Regression-test evidence

Run the existing behavioural CLI and filesystem coverage, then the complete quality gate after
converting the affected paths. Do not add a source-inspection test for this refactor.
