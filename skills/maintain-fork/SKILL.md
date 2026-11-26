---
name: maintain-fork
description: Develop in a long-lived fork. Use when branching or merging work in a fork, syncing upstream, resolving upstream conflicts, or deciding where fork-only code goes.
---

# maintain-fork

A fork stays maintainable when its changes read like upstream's own code, its persisted data cannot collide with upstream's, and upstream is merged in small steps.

## Branches

- The mirror branch takes the name of upstream's development branch (`main`, or `develop` where upstream develops there) and tracks it. It only fast-forwards; fork commits never land on it.
- The integration branch is upstream plus every fork change, and stays buildable. Builds, releases, and tags come from it. The repo's docs name it; `fork-main` unless they say otherwise.
- Work happens on short-lived branches cut from the integration branch, one per feature, carrying every commit of that feature: a type prefix names the kind of work (`feat/`, `fix/`, `chore/`, ...) and `sync/*` is for upstream syncs.
- History on the integration branch is semi-linear: a mostly straight line, where a multi-commit feature shows as one bubble and a single commit sits directly on the line.
- A work branch takes in upstream changes by rebasing onto the integration branch after a sync, and force-pushing it is fine. `sync/*` is the exception: it is itself a merge of upstream, and a rebase flattens it.
- The integration branch is published, so it only moves forward: by fast-forward or merge.

Run `git config rerere.enabled true` once per clone so a conflict resolved once resolves itself on the next sync.

## Add a feature

1. Branch `<type>/<name>` from the integration branch. A follow-up to a feature still on its branch commits there instead.
2. Edit upstream code in place, written the way upstream would write it. A self-contained module goes in new files that call upstream code rather than copy it.
3. Keep each edit to an upstream file to the change itself, with upstream's formatting and structure left as they are.
4. Give persisted identifiers (storage type ids, box names, setting keys, database migrations) a namespace upstream cannot reach, such as a high id range or a fork prefix. A collision there corrupts data silently.
5. Rebase onto the latest integration branch and fold fixups into the commit they fix. Land it on the integration branch once the analyzer and the build are green on the rebased branch and every hunk in an upstream file belongs to the change: fast-forward only (`--ff-only`) when it holds one commit, a merge commit (`--no-ff`) when it holds several. The tree that lands is the tree that was verified: when the integration branch moves before landing, rebase onto its new tip and verify again.

## Sync upstream

Sync every one to two weeks or per upstream release while work is ongoing. When work comes in bursts, sync at the start of each burst, before branching.

1. Fetch upstream and fast-forward the mirror branch to it. Its new tip is the sync's upstream commit.
2. Cut `sync/upstream-<date>` from the integration branch and merge the sync's upstream commit into it. If the integration branch advances before landing, redo the merge from its new tip using the same upstream commit and carry forward any build fixes that still apply.
3. Resolve conflicts in favour of upstream's structure, then re-apply the fork's changes on top. Build fixes may add commits.
4. Run the analyzer and the build; check whether upstream changed the toolchain (SDK version, pinned patches, lockfiles) and move with it.
5. A clean merge says nothing about behavior: exercise the fork's changed paths and open its persisted data on the merged build.
6. Fast-forward the integration branch to the verified sync commit. Delete the branch and push. The sync is done when the integration branch contains the sync's upstream commit and steps 4 and 5 passed on that same tree.

## Shrink the fork

A generic fix or small feature that is not fork-specific goes upstream as a PR. Each merged PR is one less difference to carry.
