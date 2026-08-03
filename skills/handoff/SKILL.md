---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.

Save the document as `HANDOFF.md`. Use a local-work directory inside the current workspace when one is identified by the user, project guidance, or repository conventions and the file is untracked and ignored by every applicable version control system. Dependency, build, cache, and version-control directories do not qualify. Otherwise use `<os-temp>/agent-foundry/<workspace-id>/HANDOFF.md`, deriving the workspace ID from the absolute workspace path.

Start the file with `<!-- agent-foundry:handoff -->`. Replace an existing marked handoff without asking. If the target is an unmarked file or a symlink, use the temporary fallback instead. Report the absolute path and whether an existing handoff was replaced.
