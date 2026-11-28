# Add a session skill

Add a portable `session <change-name>` workflow for starting a separate, user-accessible agent session for an existing named change on its own Git branch and worktree. The original session, checkout, branch, selection, and local edits remain undisturbed. The new session receives the change name and enough context to follow its applicable Specle workflow without assuming implementation or delivery is authorised.

Use the configured project delivery base and branch conventions. In Specle itself, the expected example is `feature/<change-name>` from the latest `origin/main`. Check that the change definition exists in the chosen committed base; if it is only local or unmerged, explain the limitation instead of silently copying or committing it. Handle existing branches and worktrees, failed or pending creation, and other collisions explicitly without overwriting work.

Keep the common skill agent-agnostic and research real session-creation capabilities for Codex, Claude, Cursor, and Antigravity. A host's interactive UI support does not by itself prove that an agent can create a separate user-owned session programmatically. Use documented host-native capabilities where available; otherwise report the limitation and appropriate manual steps, rather than substituting a subagent or a worktree attached to the current session. Design determines the host-specific integration and available support.

This change is independent of client skill linking and sidecar activation. Verification covers supported and unsupported hosts, separate session accessibility, branch and base correctness, change availability, collision and failure handling, and preservation of the original worktree and selection.
