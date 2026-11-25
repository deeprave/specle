# Requirements: Cleanup complete

## Problem

Branch-and-pull-request delivery currently splits finalisation across an original delivery PR, a later archival completion PR, and `wrapup`. It attempts merge delivery before the durable archive update and makes normal correction and completion recovery hard to resume.

Direct delivery has no PR identity, yet the current completion wording applies PR-shaped evidence to every model. The branch design also needs a safe recovery if the original PR merges before its archive update and a CI path appropriate to a final metadata-only PR update.

## Desired outcome

`complete` is the sole normal finalisation workflow. Branch delivery archive-finalises on the original PR, requests auto-merge, and resumes against the exact delivery phase after interruption. A second `-complete` PR exists only as recovery when the original PR has already merged before archival delivery.

Direct delivery retains implementation-commit evidence established by `commit` and does not invent PR completion evidence. `delivery.completion` records immutable PR identity only; it has no final commit SHA. Existing archive records are updated to remove that retired field.

## User stories and acceptance criteria

### 1. Continue and correct branch delivery before final merge

As a developer with submitted work, I want an open delivery PR to remain in the correction loop until archive finalisation, so feedback does not strand the PR.

1. A committed branch-delivery change with an open PR SHALL permit named triage, resolve, revision or corrective work, verification, review, and commit iterations on that recorded PR.
2. `commit` SHALL update the existing recorded delivery PR after a corrective iteration rather than normally creating another PR.
3. `complete` SHALL require every current external finding to be resolved or terminal before archive finalisation.
4. Once archived, a change SHALL remain immutable. `triage` and `resolve` SHALL reject it; later defects SHALL use independent work. A resumed `complete` may only finalise an eligible PR merge and remove the matching selector after synchronisation.

### 2. Finalise branch delivery on one PR, with narrow recovery

As a developer completing reviewed branch work, I want archival finalisation to remain on the original PR unless that PR has already merged, so normal delivery has one review and merge path without becoming unrecoverable.

1. For an open original PR, `complete` SHALL validate delivery evidence and eligible sidecars, archive the delivery set, reconcile matching explicit dependencies, write immutable original-PR completion identity, and push that update to the same PR before requesting authorised auto-merge.
2. Completion identity SHALL contain only archival PR reference, head branch, and target branch; it SHALL not contain an event or archival commit field.
3. If the original PR is already merged before archival delivery, `complete` SHALL synchronise the recorded target branch, then create or reuse `<delivery-branch>-complete` for archival finalisation. If tracked work prevents the branch switch, it SHALL stop and leave preservation to the user. It SHALL archive and commit there, push, and open an auto-merge recovery PR. That recovery PR SHALL only deliver the missed archive commit; it SHALL not write or amend `delivery.completion`.
4. The normal original-PR path SHALL not create a second PR.
5. Resumed completion SHALL require the current phase branch: original PR head before recovery, recovery branch after recovery begins. On another branch it SHALL report current and expected branches and stop without stashing or switching.

### 3. Resume incomplete finalisation precisely

As a developer whose completion operation was interrupted, I want `complete` to continue only the missing delivery step, so it does not duplicate commits, PRs, or archive mutations.

1. An explicit resumed `complete <change-name>` SHALL determine whether archival commit, push, normal-path immutable completion identity, auto-merge request, recovery branch, or recovery PR remains missing and perform only that step. Recovery SHALL not write completion identity.
2. A resumed complete operation SHALL report exact external CI, review, merge-eligibility, or push conditions without polling or notifications.
3. After the relevant original or recovery PR merges, `complete` SHALL synchronise the target branch and clear only the matching selector.

### 4. Preserve direct delivery semantics

As a developer using local-only or direct shared-upstream delivery, I want predictable finalisation without fabricated PR fields.

1. Direct-delivery `commit` evidence SHALL retain the implementation commit and applicable delivery branch recorded before final archive commit.
2. Direct-delivery `complete` SHALL archive and synchronise finalisation without writing `delivery.completion` or requiring PR reference, branch, or event fields.

### 5. Make completion evidence strict

As a maintainer, I want archived completion records to be immutable and structurally unambiguous.

1. The current change-status schema SHALL remove `delivery.completion.commit` without a schema version bump.
2. Every existing archived status record containing `delivery.completion.commit` SHALL remove that field in this change.
3. The workflow SHALL not rewrite an archived status record to add final commit evidence; Git history identifies the archival commit.

### 6. Fast-track archive-only PR updates

As a developer finalising delivery, I want the metadata-only archival update to receive a quick relevant CI result, so auto-merge does not wait for unaffected implementation checks.

1. For a newly pushed PR update that changes only approved `.specle/changes/**` and `.specle/archive/**` paths, CI SHALL run `uv run --frozen specle validate .` rather than the full PR suite.
2. Any changed path outside those paths, unavailable comparison base, or unclassifiable update SHALL run the full suite.
3. The workflow SHALL retain required `Verify` and make it succeed only for the applicable successful full or metadata path; it SHALL not use a top-level path filter that omits the required check.
4. Every push to `main`, including an archive-only merge, SHALL retain full lint, format, type-check, multi-version test, and blueprint validation. Future publishing depends on that full exact-merge-commit result.
5. Archive-only validation SHALL fail closed unless the immediately preceding PR revision has successful full validation against the unchanged PR base. The classifier SHALL be a repository-local reusable action and SHALL be verified with `act` and observed PR runs rather than recurring workflow tests.

## Scope and boundaries

- Replace normal two-stage `complete` plus `wrapup` across skills, policies, schema, inventory, documentation, workflow CI, and tests.
- Preserve explicit sidecar validation and exact dependency removal; dependencies appear unblocked once the delivery branch contains the prerequisite, while activation remains controlled by selected-change completion state.
- Preserve precise re-read state updates and unchanged `updated_at` for relationship-only edits.
- Do not add a delivery store, polling, notifications, inferred branch relationships, or automatic branch deletion.
- The exceptional recovery PR is permitted only after premature original-PR merge; it is not normal branch completion.
