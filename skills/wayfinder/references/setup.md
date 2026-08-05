# Setup Wayfinder

Wayfinder's repository-local configuration lives under `docs/agents/wayfinder/`:

- `wayfinder.md` defines Wayfinding methods, Tracker operations, and the Tracker root.
- `ticket-types.md` defines Ticket Types.

Treat setup as **reconciling** the repository's current state with its **target setup**. Existing documents describe the current state, bundled templates describe the current defaults, and the user's request determines the target. The target may change document content, Skill availability, or both; keep usable configuration outside its scope.

Determine the request's scope before changing files or installing Skills. For each document, structural usability establishes the health of its current state; the target determines whether to keep it, adopt the current default, or customize it. When the request leaves that outcome unclear, inspect the relevant current and default states, summarize their difference, and ask one outcome-focused question. A document's target is settled when its intended content and Skill availability are explicit.

Reconcile Wayfinder first, then Ticket Types. Run the bundled [setup validator](../scripts/validate_setup.py) to inspect document structure, and check Skill availability only after selecting the target documents. Run the validator again when reconciliation is complete.

A path is **local-only** when it is untracked and ignored by every version control system that applies to it.

## A. Wayfinder

1. Inspect `docs/agents/wayfinder/wayfinder.md` using the setup validator's diagnostics. Read the [Wayfinder template](../templates/wayfinder.md) when the target uses the current default, the document is missing or needs repair, or a comparison is needed to settle the target. Continue when the current document's structural state and any required default comparison are known.
2. Select the target document. Keep a usable existing document when it matches the target. For the current default, draft from the template; for a customization, start from the usable existing document when possible and otherwise draft from the template. Show an unusable document before replacing it, and preserve every valid Tracker root, method, or operation compatible with the target. Continue when either the existing document is selected or a complete replacement draft exists.
3. If the target document has no valid Tracker root, use a user-supplied repository-relative root after confirming it stays inside the repository. Without one, inspect the repository's version control systems and recommend a `.scratch/` child of a suitable local-only directory. When none exists, recommend `.scratch/` at the repository root and explain which ignore rules must be added. The root is selected when the user confirms the recommendation or supplies another valid repository-relative path.
4. When the target creates or replaces `Clarify`, use an implementation settled by the request. When the request leaves it open, inspect the available Skills and ask whether to use the recommended `/grilling` plus `/domain-modeling`, other available Skills, or a self-contained procedure. Continue when one implementation is selected.
5. When the target creates or replaces `Clarify`, materialize the selected implementation: keep the template definition for the recommended implementation; for other Skills, read them and replace the definition accordingly; for a self-contained implementation, draft the definition and show it once for confirmation. The definition is complete when it works with the user one focused question at a time and requires the human to supply their own answers.
6. Inspect every Skill named by the target document. If recommended Clarify Skills are missing, ask once for permission to run all applicable commands, then verify each installation:
   - `npx skills@latest add mattpocock/skills --skill=grilling`
   - `npx skills@latest add Katzeee/agent-foundry --skill=domain-modeling`
   For any other missing Skill, collect an installation command and permission, substitute an available Skill, or revise the affected method or operation to be self-contained.
   Continue when every named Skill is available or its use has been revised away.
7. Make the configured Tracker root local-only, adding the narrowest applicable ignore rules when needed. If this cannot be checked or done safely, stop and ask the user how to proceed. Continue when the root is confirmed local-only.
8. Write a new or revised document to `docs/agents/wayfinder/wayfinder.md` when its target differs from the current document. Continue when the on-disk document matches the target.

## B. Ticket Types

1. Inspect `docs/agents/wayfinder/ticket-types.md` using the setup validator's diagnostics. Read the [Ticket Types template](../templates/ticket-types.md) when the target uses the current defaults, the catalog is missing or needs repair, or a comparison is needed to settle the target. Discover default Types, resolver Skills, and per-Skill installation recipes from the template itself. Continue when the current catalog's structural state and any required default comparison are known.
2. Choose the target catalog branch. Keep a usable existing catalog when it matches the target. For the current defaults, use the template without its `wayfinder-setup` comments. For a customization, start from the usable existing catalog when appropriate; for a new catalog, use the template only as a structural reference. Show an unusable catalog before replacing it. Continue when the current, default, custom, or new branch and its source are explicit.
3. For a customization or new catalog, let the user add, remove, or revise Types and resolver bindings in one response. Read any referenced available Skills; draft `Interaction`, `Use when`, `Resolve`, and optional `After creation`; then show the complete draft once for confirmation. A `Resolve` without a Skill must be self-contained. The catalog is selected when the exact current or default catalog is chosen, or a complete custom or new catalog is confirmed.
4. Inspect every Skill named by the target catalog. If any are missing, read the Ticket Types template if needed to find their recipes, ask once for permission to install every missing Skill with an available recipe, run those recipes, and verify the installations. If installation is declined, or a missing Skill has no recipe, ask the user to substitute another available Skill in `Resolve`, replace `Resolve` with a self-contained procedure, remove the Type, or provide and approve an installation command. Continue when every named Skill is available or its use has been revised away.
5. Write the target catalog to `docs/agents/wayfinder/ticket-types.md` without setup-only comments when it differs from the current catalog. Continue when the on-disk catalog matches the target.
6. Run `python <setup-validator>` and repair every reported error. Continue when it passes.

Setup is complete when both documents match the target and are structurally usable, the Tracker root is local-only, and every Skill named by the selected methods, Tracker operations, or a confirmed `Resolve` is available. The tracker CLI creates the Tracker root on first use.
