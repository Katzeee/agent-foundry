# Agent Foundry source

This is the editable source branch for the Agent Foundry skill and plugin catalog. The `main` branch is a generated, directly installable distribution and must not be edited by hand.

## Catalog model

`catalog.json` is the source of truth:

- Every directory under `skills/` must have one entry in `catalog.skills`.
- `skills.<name>.publish: true` publishes that skill independently under `main:skills/<name>`.
- Each entry in `catalog.plugins` assembles its listed skills into one self-contained Codex and Claude Code plugin under `main:plugins/<plugin>`.
- A skill may be independently published, included in one or more plugins, or kept plugin-only with `publish: false`.

For example:

```json
{
  "skills": {
    "standalone-skill": { "publish": true },
    "plugin-internal-skill": { "publish": false }
  },
  "plugins": [
    {
      "name": "example-plugin",
      "skills": ["standalone-skill", "plugin-internal-skill"]
    }
  ]
}
```

## Local workflow

Node.js 22 or newer is required. The build has no third-party dependencies.

```bash
npm run validate
npm run build
npm run validate:dist
```

`npm run check` runs all three steps. Generated files go to the ignored `dist/` directory.

Each generated plugin contains one shared `skills/` tree plus both platform manifests:

```text
plugins/<name>/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
└── skills/
```

The distribution also contains `.agents/plugins/marketplace.json` for Codex and `.claude-plugin/marketplace.json` for Claude Code. Claude versions are intentionally omitted so Claude Code resolves updates by the marketplace Git commit instead of requiring a version bump during active iteration.

## Publishing

Pull requests and edits target `source`. Pushes do not run GitHub Actions. The workflow checks `source` every day at 10:17 Asia/Shanghai time and exits after checkout when its commit is already recorded in `main:build-manifest.json`. When an unpublished commit exists, it validates the source, replaces the `main` worktree with `dist/`, and creates a release commit.

The workflow can also be run manually from the Actions tab. Its `force` input rebuilds an already-published source commit.

The repository must allow the workflow `GITHUB_TOKEN` to write repository contents. If `main` has branch protection, allow this publishing workflow or its GitHub Actions bot to update the branch.

Never merge `source` into `main`: they are different projections of the repository.
