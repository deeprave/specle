# Requirements: Fast lane test

## Problem

The branch-and-pull-request completion model adds an archival finalisation commit to the existing delivery PR. That commit normally moves one change from `.specle/changes/` to `.specle/archive/`, updates its status and completion evidence, and may remove fulfilled names from other active changes' explicit dependency arrays. It changes no implementation, tests, package metadata, or managed blueprint content.

The current pull-request test workflow runs its complete lint, format, type-check, multi-version test, and blueprint-validation suite for every update. Consequently, the metadata-only finalisation commit repeats expensive checks before auto-merge can complete, despite the implementation having already passed them earlier in the same PR.

## Desired outcome

Use a fast CI path for a strictly identified metadata-only pull-request update while preserving the full suite for all implementation-affecting PR updates and for every merge to `main`. The fast path must retain the same required PR verdict and validate the active and archived Specle runtime records it changes. Publishing continues to depend on the full successful workflow for the exact merged `main` commit.

## User stories and acceptance criteria

### 1. Fast-track archive-only PR updates

As a developer finalising a delivery, I want an archive-only update to the existing PR to receive a quick, relevant CI result, so auto-merge is not delayed by rerunning unaffected language and package checks.

1. For a pull-request update whose newly pushed commit changes only approved `.specle/changes/**` and `.specle/archive/**` paths, the workflow SHALL run a metadata validation path instead of the full lint, format, type-check, multi-version test, and blueprint-validation jobs.
2. The metadata validation path SHALL run `uv run --frozen specle validate .` and SHALL fail if the changed runtime records, managed inventory, lifecycle graph, or generated skill index are invalid.
3. The workflow SHALL treat any changed path outside the approved completion-metadata paths, an unclassifiable event, or an unavailable comparison base as requiring the full suite.
4. The workflow SHALL preserve its existing required `Verify` check name and report it successfully only when the applicable full or metadata validation path succeeds.

### 2. Preserve release-quality evidence

As a maintainer, I want publishing to remain tied to full testing of the merged revision, so the PR fast lane cannot weaken release assurance.

1. Every push to `main`, including a merge of a metadata-only completion update, SHALL run the existing full lint, format, type-check, multi-version test, and blueprint-validation suite.
2. A publish workflow or later release automation SHALL depend on the successful full `main` workflow for the exact merged commit, not merely the PR fast-lane verdict.
3. The change SHALL not use a top-level GitHub Actions path filter that omits the required `Verify` check for an eligible PR update.

### 3. Keep the optimisation narrowly scoped

As a workflow maintainer, I want the shortcut to apply only to archival metadata, so an implementation or workflow change cannot accidentally bypass its normal CI coverage.

1. The path classification SHALL evaluate only the newly pushed PR update, not treat a PR with earlier implementation changes as permanently eligible for the fast path.
2. The workflow SHALL keep the full suite as the default and document the archive-only eligibility rule beside the CI implementation.
3. The change SHALL not alter archive lifecycle semantics, suppress post-merge `main` validation, or introduce a release or publishing workflow.

## Boundaries

- This change optimises the final metadata-only update of an existing PR; it does not remove the version-controlled archival commit.
- It does not automate local checkout synchronisation after a PR merge.
- It does not infer archive eligibility from commit messages, branch names, or a change's lifecycle status; eligibility is determined from the actual changed paths and event comparison data.
- It assumes the existing `push` trigger for `main` remains the full release-quality gate.
