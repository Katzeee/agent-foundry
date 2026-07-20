# Issue tracker

Tracker root: `<tracker-root>`

Each map lives at `<tracker-root>/<map>/map.md`; its child tickets live at `<tracker-root>/<map>/issues/NN-<slug>.md`. A ticket's number is unique within its map and is its identity.

## Wayfinding operations

- **Collect context**: run `python skills/wayfinder/scripts/tracker.py collect`. It creates the Tracker root if needed and prints a low-resolution index across all maps, newest activity first. Choose a map from that index, then read its `map.md`. Frontier tickets are ordered by number.
- **Read map**: read `<tracker-root>/<map>/map.md` after choosing a map from the collected index.
- **Read ticket**: read `<tracker-root>/<map>/issues/NN-<slug>.md` when a ticket's question, answer, or other detail is needed.
- **Create map**: run `python skills/wayfinder/scripts/tracker.py create-map <slug> --title "<title>" --destination "<destination>" [--notes "<notes>"] [--not-yet-specified "<fog>"] [--out-of-scope "<scope exclusions>"]`.
- **Create child ticket**: run `python skills/wayfinder/scripts/tracker.py create-ticket <map> <slug> --title "<title>" --question "<question>"`.
- **Wire blocking**: run `python skills/wayfinder/scripts/tracker.py add-blocker <map> <ticket> <blocker>`. Both ticket references are numbers from the same map. Use `remove-blocker` with the same arguments to remove an edge.
- **Claim**: run `python skills/wayfinder/scripts/tracker.py claim-ticket <map> <ticket> [--actor <name>]` as the session's first write. The ticket must be open, unclaimed, and unblocked. Use `release-ticket` to relinquish a claim without closing the ticket.
- **Resolve**: run `python skills/wayfinder/scripts/tracker.py resolve-ticket <map> <ticket> --answer "<answer>" --gist "<one-line gist>"`. The command records the answer, closes the ticket, and adds its linked gist to the map's **Decisions so far**.
- **Rule out of scope**: run `python skills/wayfinder/scripts/tracker.py exclude-ticket <map> <ticket> --reason "<reason>" --gist "<one-line gist>"`. The command records the reason, closes the ticket, and adds its linked gist to the map's **Out of scope**. It does not add the ticket to **Decisions so far**.
- **Validate**: run `python skills/wayfinder/scripts/tracker.py validate [map]` after a sequence of Tracker operations; repair every reported error.

Ticket fields:

- `State`: `open` or `closed`
- `Claimed by`: empty when unclaimed; otherwise the claim owner
- `Blocked by`: comma-separated ticket numbers from the same map

`State` and `Claimed by` are independent: claiming an open ticket does not create a third lifecycle state. The frontier is derived from open tickets that have no claim and whose blockers are all closed.
