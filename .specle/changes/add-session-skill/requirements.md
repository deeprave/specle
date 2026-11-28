# Requirements: Add a session skill

## Why

Working on one Specle change should not prevent a developer from starting another in a separate interactive agent session. The existing workflow refers to separate Git worktrees for independent work, but does not provide a consistent way to create a new user-accessible session for a named change with its own branch and checkout while leaving the current session and worktree undisturbed.

Provide a portable `session` skill that expresses this outcome independently of a particular agent host, and uses the available host's supported session-creation and worktree mechanisms where they can fulfil it.

## Scope and boundaries

- The primary outcome is a separate, user-accessible session for a named existing change, not merely a worktree, a subagent, or a switch of the current session's checkout.
- Research the actual supported capabilities and invocation mechanisms for Codex, Claude, Cursor, and Antigravity. Do not assume a host can create or target an independently interactive session from an agent merely because its UI supports worktrees. Document verified support, limitations, and any user-performed steps.
- Keep the common workflow agent-agnostic; isolate host-specific integration where necessary. When the active host cannot create the requested session, report that limitation and provide concrete host-appropriate next steps rather than silently substituting a worktree or subagent.
- Use the project's configured delivery base and branch naming policy. For this repository the expected example is `feature/<change-name>` from an up-to-date `origin/main`; other projects may use different policy.
- A new checkout sees committed content from its base, not uncommitted changes in the current worktree. Do not silently copy, commit, stash, or migrate local work, or copy `.specle/context.json` between worktrees.
- This is independent of `add-client-link`, which concerns discovering installed skills in clients, and `allow-sidecar-activation`, which concerns lifecycle routing. Neither is a prerequisite.

## Requirements

### 1. Start isolated named work

**User story:** As a developer, I want a separate interactive session for a named change so I can work on it while continuing in my current session.

1. WHEN a user invokes `session <change-name>`, THE skill SHALL identify the explicitly named change and determine its kind, current state, and applicable project delivery policy.
2. WHEN the host supports the requested operation and the change is available in the intended base, THE skill SHALL create a separate user-accessible session with its own Git worktree and branch following project policy, based on the current configured delivery base.
3. THE original session, its checkout, branch, selected change, and uncommitted or staged files SHALL remain unchanged. THE new session SHALL be independently accessible to the user, not merely a delegated subagent within the current session.
4. THE skill SHALL report the new session, worktree path, branch, base, and change name when the host exposes them, and SHALL clearly distinguish a request still being created from a ready session.
5. THE skill SHALL pass enough context for the new session to find the named change and follow its applicable Specle workflow; it SHALL NOT silently begin implementation or delivery beyond the user's requested scope.

### 2. Handle Git state and collisions explicitly

**User story:** As a developer, I want the new session to start from the intended committed state without losing or unintentionally importing work.

1. THE skill SHALL establish the configured base ref and check whether its local view is current before creating the branch; it SHALL use an up-to-date remote base when project policy requires one.
2. WHEN the named change is absent from the base, including when its definition exists only as local uncommitted or unmerged work, THE skill SHALL explain the mismatch and offer appropriate explicit next steps without silently copying or committing it.
3. WHEN the intended branch or worktree already exists, THE skill SHALL report the existing state and use or create an alternative only when the user has directed that choice; it SHALL NOT reset, overwrite, or force-delete existing work.
4. WHEN the new checkout or session cannot be created or bound as requested, THE skill SHALL report the actual outcome and any resources already created, without claiming success or modifying the current checkout to compensate.

### 3. Support host-specific capabilities without coupling the workflow

**User story:** As a developer using different agents, I want the same intent to work where supported and a clear explanation where it does not.

1. THE design SHALL research and record current documented capabilities for creating a separate user-accessible session in Codex, Claude, Cursor, and Antigravity, distinguishing agent-callable operations from user-interface-only operations.
2. THE skill SHALL use verified host-native session and worktree capabilities when available, without assuming that a subagent or a detached worktree is equivalent to an independently interactive session.
3. WHEN a required capability is unavailable or cannot be invoked by the active agent, THE skill SHALL state the missing capability and offer concrete manual instructions appropriate to that host, without claiming to have created a session.
4. THE packaged skill, installed inventory, and applicable workflow and discovery documentation SHALL identify and expose the new skill in the normal Specle distribution.

## Verification direction

Verify host capability research against current documentation and exercise the portable decision points: a committed named change on an up-to-date base, an absent or uncommitted definition, existing branch or worktree collisions, unsupported host operations, pending or failed creation, and unchanged original checkout and selection. Validate that a supported host yields an independently accessible session with the intended branch, checkout, and context. Follow the project's documented quality gates.
