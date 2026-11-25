---
name: maintain-fork
description: Develop in a long-lived fork while syncing upstream. Use when branching or merging work in a fork, syncing upstream, resolving upstream conflicts, or deciding where fork-only code goes.
---

# maintain-fork

A fork stays maintainable when its changes read like upstream's own code, its persisted data cannot collide with upstream's, and upstream is merged in small steps.

## Branches

- The mirror branch takes the name of upstream's development branch (`main` below; some upstreams develop on `develop`) and tracks it. It only fast-forwards; fork commits never land on it.
- The integration branch is upstream plus every fork change, and stays buildable. Builds, releases, and tags come from it. The repo's docs name it; `fork-main` unless they say otherwise.
- Work happens on short-lived branches cut from the integration branch and merged back with a merge commit: a type prefix names the kind of work (`feat/`, `fix/`, `chore/`, ...) and `sync/*` is for upstream syncs.
- A work branch rebases onto the latest integration branch right before its merge, so the merge commit shows only that branch's work. Force-pushing a work branch is fine; a tidy branch is easier to keep. `sync/*` is the exception: it is itself a merge of upstream, and a rebase flattens it.

Run `git config rerere.enabled true` once per clone so a conflict resolved once resolves itself on the next sync.

## Add a feature

1. Branch `<type>/<name>` from the integration branch.
2. Edit upstream code in place, written the way upstream would write it. A self-contained module goes in new files that call upstream code rather than copy it.
3. Keep each edit to an upstream file to the change itself, with upstream's formatting and structure left as they are.
4. Give persisted identifiers (storage type ids, box names, setting keys, database migrations) a namespace upstream cannot reach, such as a high id range or a fork prefix. A collision there corrupts data silently.
5. Rebase onto the latest integration branch, then merge back once the analyzer and the build are green on the rebased branch and every hunk in an upstream file belongs to the change.

## Sync upstream

Sync every one to two weeks or per upstream release while work is ongoing. When work comes in bursts, sync at the start of each burst, before branching.

1. `git fetch upstream`, then fast-forward `main` with `git merge --ff-only upstream/main`.
2. Cut `sync/upstream-<date>` from the integration branch and merge `main` into it. Keep merging, never rebase: conflicts resolve once and the link to upstream's commits stays intact. The integration branch only ever receives merges. When it moves while the sync is open, merge it into the sync branch.
3. Resolve conflicts in favour of upstream's structure, then re-apply the fork's changes on top. Build fixes may add commits.
4. Run the analyzer and the build; check whether upstream changed the toolchain (SDK version, pinned patches, lockfiles) and move with it.
5. A clean merge says nothing about behavior: exercise the fork's changed paths and open its persisted data on the merged build.
6. Merge the sync branch into the integration branch with a merge commit, never a squash: a squash cuts the link to upstream's commits and the next sync conflicts again. Delete the branch and push. The sync is done when the build is green and `git log main..<integration> --no-merges` shows only fork commits.

## Shrink the fork

A generic fix or small feature that is not fork-specific goes upstream as a PR. Each merged PR is one less difference to carry.
