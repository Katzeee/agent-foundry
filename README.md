# XY Workflow source

This is the editable source branch for the XY Workflow skill and plugin catalog. The `main` branch is a generated, directly installable distribution and must not be edited by hand.

## Catalog model

`catalog.json` is the source of truth:

- Every directory under `skills/` must have one entry in `catalog.skills`.
- `skills.<name>.publish: true` publishes that skill independently under `main:skills/<name>`.
- Each entry in `catalog.plugins` assembles its listed skills into a self-contained Codex plugin under `main:plugins/<plugin>`.
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

## Publishing

Pull requests target `source`. Every push to `source` is validated by GitHub Actions; after validation, the workflow replaces the `main` worktree with `dist/` and creates a release commit.

The repository must allow the workflow `GITHUB_TOKEN` to write repository contents. If `main` has branch protection, allow this publishing workflow or its GitHub Actions bot to update the branch.

Never merge `source` into `main`: they are different projections of the repository.
