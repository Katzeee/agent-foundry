# Wayfinder

Tracker root: `<tracker-root>`

`<wayfinder-cli>` means the `scripts/tracker.py` bundled with the active Wayfinder skill, resolved relative to that skill's `SKILL.md`. It is not a path relative to this repository.

Each map lives at `<tracker-root>/<map>/map.md`; its child tickets live at `<tracker-root>/<map>/issues/NN-<slug>.md`. A ticket's number is unique within its map and is its identity.

## Wayfinding methods

- **Clarify**: use `/grilling` and `/domain-modeling` together.

## Tracker operations

- **Collect context**: run `python <wayfinder-cli> collect`. It creates the Tracker root if needed and prints a low-resolution index across all maps, newest activity first. Choose a map from that index, then read its `map.md`. Frontier tickets are ordered by number.
- **Read map**: read `<tracker-root>/<map>/map.md` after choosing a map from the collected index.
- **Read ticket**: read `<tracker-root>/<map>/issues/NN-<slug>.md` when a ticket's question, answer, or other detail is needed.
- **Create map**: run `python <wayfinder-cli> create-map <slug>`. It creates a Markdown template; fill every section in `map.md`.
- **Create child ticket**: run `python <wayfinder-cli> create-ticket <map> <slug>`. It allocates the next ticket number and creates a Markdown template; fill in the file.
- **Wire blocking**: set the target ticket's `Blocked by:` field to comma-separated ticket numbers from the same map. Create all referenced tickets before adding the edges.
- **Claim**: change an open frontier ticket's `State:` to `claimed` before beginning work. Change it back to `open` to release the claim without closing the ticket.
- **Resolve**: update the ticket and map as one coherent change: add a non-empty `## Answer`, change `State:` to `closed`, add its linked one-line gist to **Decisions so far**, and graduate any now-specific fog into new tickets.
- **Rule out of scope**: update the ticket and map as one coherent change: add the exclusion reason as its non-empty `## Answer`, change `State:` to `closed`, and add its linked gist plus exclusion reason to **Out of scope**. Do not add it to **Decisions so far**.
- **Validate**: run `python <wayfinder-cli> validate [map]`; repair every reported error before treating the map as a valid tracker state.

Ticket fields:

- `Type`: the Ticket Type name persisted for Wayfinder; the tracker does not define its vocabulary or behavior
- `State`: `open`, `claimed`, or `closed`
- `Blocked by`: comma-separated ticket numbers from the same map

The frontier is derived from open tickets whose blockers are all closed. A claimed ticket is active but excluded from the frontier until it is released or closed. A closed ticket has one non-empty `## Answer` and is linked exactly once from either **Decisions so far** or **Out of scope**.
