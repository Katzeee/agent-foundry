# Setup Wayfinder

Wayfinder's repository-local configuration lives under `docs/agents/wayfinder/`:

- `wayfinder.md` defines Wayfinding methods, Tracker operations, and the Tracker root.
- `ticket-types.md` defines Ticket Types.

Complete Wayfinder setup first, then Ticket Types setup. Preserve a structurally usable document; show an unusable document before replacing it.

Run the bundled [setup validator](../scripts/validate_setup.py). Use its diagnostics to repair document structure, and check Skill availability separately. Run it again after both sections are complete.

A path is **local-only** when it is untracked and ignored by every version control system that applies to it.

## A. Wayfinder

1. Use the setup validator's diagnostics for `docs/agents/wayfinder/wayfinder.md`. Read the [Wayfinder template](../templates/wayfinder.md) only when creating or repairing the document.
2. If the document is structurally usable, select it unchanged. Otherwise, show it if it exists and draft a replacement from the template, preserving any valid Tracker root, method, or operation from the existing document.
3. If the draft has no valid Tracker root, use a user-supplied repository-relative root after confirming it stays inside the repository. Without one, inspect the repository's version control systems and recommend a `.scratch/` child of a suitable local-only directory. When none exists, recommend `.scratch/` at the repository root and explain which ignore rules must be added. Ask one question to confirm the recommendation or collect another repository-relative path.
4. When creating or replacing `Clarify`, inspect the Skills currently available, then ask how Wayfinder should implement it: use the recommended `/grilling` plus `/domain-modeling`, use other available Skills, or use a self-contained procedure. It must work with the user one focused question at a time and never answer for them.
5. For the recommended choice, keep the template's `Clarify` definition. For other Skills, read them and replace the definition accordingly. For a self-contained choice, draft the definition and show it once for confirmation.
6. Inspect every Skill named by the selected document. If recommended Clarify Skills are missing, ask once for permission to run all applicable commands, then verify each installation:
   - `npx skills@latest add mattpocock/skills --skill=grilling`
   - `npx skills@latest add Katzeee/agent-foundry --skill=domain-modeling`
   For any other missing Skill, collect an installation command and permission, substitute an available Skill, or revise the affected method or operation to be self-contained.
7. Make the configured Tracker root local-only, adding the narrowest applicable ignore rules when needed. If this cannot be checked or done safely, stop and ask the user how to proceed.
8. Write a new or revised document to `docs/agents/wayfinder/wayfinder.md`.

## B. Ticket Types

1. Use the setup validator's diagnostics for `docs/agents/wayfinder/ticket-types.md`.
2. If `docs/agents/wayfinder/ticket-types.md` is structurally usable, select it unchanged. Otherwise, show it if it exists, then read the [Ticket Types template](../templates/ticket-types.md). Discover its default Types, resolver Skills, and per-Skill installation recipes from the file itself; never encode that catalog in this setup process. Inspect the Skills currently available, present the discovered default Types and any missing resolver Skills, then ask whether to use the defaults, customize them, or define a new catalog.
3. On the default branch, select the template unchanged except for removing every `wayfinder-setup` comment.
4. On a customization branch, let the user add, remove, or revise Types and resolver bindings in one response. Read any referenced available Skills, draft `Interaction`, `Use when`, `Resolve`, and optional `After creation`, then show the complete draft once for confirmation. A `Resolve` without a Skill must be self-contained.
5. Inspect every Skill named by the selected catalog. If any are missing, read the Ticket Types template if needed to find their recipes, ask once for permission to install every missing Skill with an available recipe, run those recipes, and verify the Skills became available. If installation is declined, or a missing Skill has no recipe, ask the user to substitute another available Skill in `Resolve`, replace `Resolve` with a self-contained procedure, remove the Type, or provide and approve an installation command.
6. Write a new or revised catalog to `docs/agents/wayfinder/ticket-types.md` without setup-only comments.
7. Run `python <setup-validator>` and repair every reported error before finishing.

Setup is complete when both documents are structurally usable, the Tracker root is local-only, and every Skill named by the configured methods, Tracker operations, or a confirmed `Resolve` is available. The tracker CLI creates the Tracker root on first use.
