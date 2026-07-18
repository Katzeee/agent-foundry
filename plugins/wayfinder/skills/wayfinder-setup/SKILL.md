---
name: wayfinder-setup
description: Configure or relocate Wayfinder's repository-local issue tracker. Use when Wayfinder has not been set up, its tracker document is unusable, or the user wants to change the Tracker root.
---

# Setup Wayfinder

Choose the repository-relative directory where Wayfinder maps and tickets live, ensure Git ignores it, and record its operations in `docs/agents/issue-tracker.md`.

## Process

1. If the user supplied a Tracker root, confirm it stays inside the repository and use it.
2. Otherwise, inspect the repository and its applicable `.gitignore` files. Recommend a `.scratch/` child of a suitable ignored directory; if none exists, recommend `.scratch/` at the repository root and say that it will be added to `.gitignore`.
3. Ask one question to confirm the recommendation or collect another repository-relative path.
4. Ensure the confirmed path is ignored, adding the narrowest root `.gitignore` rule when needed.
5. Write `docs/agents/issue-tracker.md` from [issue-tracker.md](./issue-tracker.md), replacing `<tracker-root>` with the confirmed path. Replace an existing tracker document only after showing its current setting.

Setup is complete when Git ignores the configured path and `docs/agents/issue-tracker.md` records it. The Tracker CLI creates the directory on first use.
