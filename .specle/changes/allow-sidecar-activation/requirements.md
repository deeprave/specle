# Requirements: Allow sidecar activation

## Why

`activate <name>` is the entry point for starting normal changes and spikes, but it rejects bugfixes and refactors. Prepared abbreviated work instead requires a different, kind-specific command, and `build` is currently limited to normal changes. This splits a common lifecycle operation across workflows even though the target's kind and state identify the appropriate preparation and execution path.

Make activation a kind-aware entry point for supported change types, and make named build execution available for prepared bugfixes and refactors. Align lifecycle policy, skill instructions and metadata, and next-action reporting with that behaviour.

## Scope and boundaries

- Preserve the existing selection and preparation behaviour for normal changes and spikes. Activation of a selected, defined spike remains a supported way to start it; reporting `activate` for that state is valid.
- Bugfixes and refactors remain explicitly named, non-selected work. Activating them must not change `.specle/current-change`, including when no change is selected.
- Preserve the existing requirements for explicit reciprocal relationships when abbreviated work is delivered alongside a selected parent. Do not infer concurrent delivery from activation, ordering, or shared files.
- Keep kind-specific bugfix reproduction and regression coverage, refactor behavioural invariants and baseline, and the existing delivery and verification boundaries. Do not duplicate independent execution flows.
- Other supported kinds must have an explicit, appropriate route or a clear unsupported diagnostic; do not silently treat them as normal changes or invent workflow ownership. Determine their actual supported activation behaviour from the lifecycle policy and existing skills during design.
- This work is independent of `refactor-change-record`, `consolidate-state-enums`, and the current changes-listing delivery. It must work with the implementation available when undertaken and must not assume those queued changes have been delivered.

## Requirements

### 1. Activate according to kind and lifecycle state

**User story:** As a developer, I want one named activation command to begin eligible work so that I need not remember a different starting command for each kind.

1. WHEN `activate <name>` names an eligible active change, THE workflow SHALL inspect its kind and lifecycle state and dispatch the appropriate preparation or owning workflow.
2. WHEN a normal change is activated, THE workflow SHALL retain its selection and required estimate, size-dependent design, tasks, and build progression.
3. WHEN a defined or spiking spike is activated, THE workflow SHALL select or retain it and invoke the spike workflow. Activating an already selected defined spike SHALL be supported.
4. WHEN a defined or planned bugfix or refactor is activated, THE workflow SHALL leave the existing selection unchanged, complete any missing kind-specific prerequisites, and invoke `build <name>` when ready.
5. WHEN the target is archived, missing, in an ineligible lifecycle state, or has a kind without a supported activation route, THE workflow SHALL report the condition without selecting or implementing unrelated work.
6. WHEN abbreviated work is to accompany a selected parent, THE workflow SHALL require the explicit reciprocal relationship under the existing concurrent-delivery policy and SHALL NOT create or infer that relationship merely from activation.

### 2. Build named abbreviated work

**User story:** As a developer, I want `build <name>` to execute prepared bugfixes and refactors so execution has one consistent entry point while retaining each kind's safeguards.

1. WHEN a named bugfix or refactor has its required specification and task plan and is eligible to build, THE build workflow SHALL execute that target without changing `.specle/current-change`.
2. THE build workflow SHALL apply bugfix-specific reproduction and regression requirements or refactor-specific behavioural invariants and baseline requirements as applicable, and update the named target's task progress and lifecycle state.
3. WHEN required preparation is missing or inconsistent, THE workflow SHALL identify and complete the applicable prerequisites through their owning workflow before building, or report why the target cannot proceed; it SHALL NOT treat missing work as completed.
4. THE change SHALL reconcile the roles of `prepare`, `bugfix`, `refactor`, `activate`, `build`, `verify`, and review so their instructions and lifecycle metadata consistently describe preparation, execution, and continuation without duplicating competing implementations.
5. Existing normal-change build confirmation and other established authorisation and delivery boundaries SHALL remain effective.

### 3. Keep next actions and lifecycle guidance consistent

**User story:** As a developer, I want reported next actions to match commands that actually work for a change's kind and state.

1. THE lifecycle policy, packaged skill instructions and metadata, installed skill copies, and relevant entrypoint documentation SHALL agree on activation, selection, preparation, and build ownership.
2. THE next-action resolver and change-listing output SHALL reflect the applicable kind, status, selection, and preparation state, including activation of unselected prepared bugfixes and refactors and the supported selected defined spike activation.
3. WHEN an abbreviated change is already being built or has progressed to verification, review, or delivery, THE next action SHALL reflect its actual lifecycle stage rather than restarting preparation.
4. THE reporting contract SHALL retain action names without embedding arguments where the existing output format specifies action names.

## Verification direction

Exercise activation and next-action decisions for normal changes, spikes, bugfixes, and refactors across eligible states, including selected and unselected spikes, missing prerequisites, named sidecars with and without an existing selection, and explicit concurrent-delivery relationships. Verify that building named abbreviated work uses the correct kind-specific safeguards, never changes selection, and advances only the intended record. Confirm that unsupported kinds and invalid states produce clear diagnostics and that existing normal-change and spike behaviour remains intact. Run the project's documented quality gates.
