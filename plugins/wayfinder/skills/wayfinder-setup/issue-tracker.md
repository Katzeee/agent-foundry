# Issue tracker

Tracker root: `<tracker-root>`

Each map lives at `<tracker-root>/<map>/map.md`; its child tickets live at `<tracker-root>/<map>/issues/NN-<slug>.md`. A ticket's number is unique within its map and is its identity.

## Wayfinding operations

- **Collect context**: run `python skills/wayfinder/scripts/tracker.py collect`. It creates the Tracker root if needed and prints every map at low resolution, newest activity first. Activity is the latest modification of the map or any of its tickets; frontier tickets are ordered by number.
- **Create map**: run `python skills/wayfinder/scripts/tracker.py create-map <slug>`, then fill the generated `map.md`.
- **Create child ticket**: run `python skills/wayfinder/scripts/tracker.py create-issue <map> [slug]`, then fill the generated ticket.
- **Wire blocking**: set `Blocked by: NN, NN`. Blockers are ticket numbers from the same map.
- **Claim**: set `Status: claimed`. In this local tracker, that status is the claim; an `open` ticket is unclaimed.
- **Close**: append `## Answer`, set `Status: closed`, then append `- [<ticket title>](<relative link>) — <one-line gist>` to the map's **Decisions so far** section.
- **Rule out of scope**: append `## Answer` with the reason, set `Status: closed`, and append a linked gist with the reason to the map's **Out of scope** section. Do not add it to **Decisions so far**.
- **Validate**: run `python skills/wayfinder/scripts/tracker.py validate [map]` after editing Tracker files; repair every reported error.

Ticket fields:

- `Interaction`: `HITL` or `AFK`
- `Type`: `grilling`, `research`, `prototype`, or `task`
- `Status`: `open`, `claimed`, or `closed`
