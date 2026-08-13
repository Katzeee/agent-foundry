---
name: wayfinder
description: Plan a huge chunk of work — more than one agent session can hold — as a shared map of decision tickets on your issue tracker, and resolve them one at a time until the way to the destination is clear.
disable-model-invocation: true
---

A loose idea has arrived — too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **shared map** on the repo's issue tracker, then works its **decision tickets** — questions whose resolution is a decision, not slices of a build to execute — one at a time until the route is clear.

The destination varies per effort, and naming it is the first act of charting — it shapes every ticket. It might be a spec to hand off and iterate on, a decision to lock before planning starts, or a change made in place like a data-structure migration. The map is domain-agnostic — engineering work, course content, whatever fits the shape.

## Plan, don't do

Wayfinder is **planning** by default: each ticket resolves a decision, and the map is done when the way is clear — nothing left to decide before someone goes and does the thing. The pull to just do the work is usually the signal you've reached the edge of the map and it's time to hand off. An effort can override this in its **Notes** — carrying execution into the map itself — but absent that, produce decisions, not deliverables.

## Refer by name

Every map and ticket has a **name** — its title. In everything the human reads — narration, the map's Decisions-so-far — refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The tracker identity and link don't vanish — a name wraps its link — but they ride *inside* the name, never stand in for it.

## The Map

The map is the canonical tracker artifact for an effort. Its tickets are children of the map, and its `domain.md` holds the effort's shared language.

The map is an **index**, not a store. It lists the decisions made and points at the tickets that hold their detail; a decision lives in exactly one place — its ticket — so the map never restates it, only gists it and links.

A map stays **open** until its destination is **reached**, and the tracker records which. Read arrival from that record, never from an empty frontier — an uncharted map has one too. Reaching it is final: work that surfaces afterwards belongs to a new map, not to a resumption.

**Where the map, its child tickets, blocking, and frontier queries physically live is tracker-specific.** Run the bundled [setup validator](scripts/validate_setup.py) before loading repository-local configuration. If it fails, or the user asks to configure Wayfinder, follow [setup](references/setup.md) and rerun it. Then consult the configured Wayfinding methods, Tracker operations, and Ticket Types before interpreting the user's request, and collect the tracker-wide map index.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are **not** listed — they are open children, found through the tracker.

```markdown
## Destination

<what reaching the end of this map looks like — the spec, decision, or change this effort is finding its way to. One or two lines; every session orients to it before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this effort>

## Decisions so far

<!-- the index — one line per closed ticket: enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [<closed ticket title>](link) — <one-line gist of the answer>

## Not yet specified

<!-- see "Fog of war": in-scope fog you can't ticket yet; graduates as the frontier advances -->

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a map child identified by the tracker. Its question is sized to one 100K token agent session:

```markdown
## Question

<the decision or investigation this ticket resolves>
```

Each ticket has one Type (see [configured Ticket Types](references/setup.md#b-ticket-types)), which define its interaction and resolution behavior.

A session **claims** a ticket, **first**, before any work, so concurrent sessions skip it.

Blocking follows the tracker's dependency convention. A ticket is **unblocked** when every ticket blocking it is closed; the **frontier** is the open, unblocked children — the edge of the known.

The answer is recorded when the ticket resolves (see [Work through the map](#work-through-the-map)). Assets created while resolving a ticket are linked from it, not pasted in.

## Fog of war

The map is _deliberately_ incomplete: don't chart what you can't yet see. Beyond the live tickets lies the **fog of war** — the dim view of decisions and investigations you can tell are coming but can't yet pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever's now specifiable into fresh tickets — one at a time, until the way to the destination is clear and no tickets remain.

The map's **Not yet specified** section is where that dim view is written down: the suspected question, the area to revisit later. It's the undiscovered frontier _toward_ the destination — everything here is in scope, just not sharp enough to ticket. Write as loosely or as fully as the view allows; it doubles as a signpost for collaborators reading where the effort is headed.

**Fog or ticket?** The test is whether you can state the question precisely now — _not_ whether you can answer it now.

- **Ticket when** the question is already sharp — even if it's blocked and you can't act on it yet.
- **Not yet specified when** you can't yet phrase it that sharply. Don't pre-slice the fog into ticket-sized pieces: it's coarser than a ticket, and one patch may graduate into several tickets, or none, once the frontier reaches it.

**Not yet specified** excludes what's already decided (Decisions so far), what's already a live ticket, and what's out of scope (the next section).

## Out of scope

Fog only ever gathers _toward_ the destination. The destination fixes the scope, so work beyond it is **out of scope** — it isn't fog, and it doesn't belong in **Not yet specified**. It gets its own **Out of scope** section on the map: work you've consciously ruled out of _this_ effort. Scope, not sharpness, lands it here.

Out-of-scope work never graduates — the frontier stops at the destination — so it returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

Ruling something out of scope is a scoping act, not a step on the route. When a ticket that already exists turns out to sit past the destination — mis-scoped in while charting, or exposed by a resolution — **rule it out of scope**. It stays out of **Decisions so far**, which records the route actually walked — a scope boundary isn't a step on it.

## Invocation

Select one path:

- Neither an idea nor a map → summarize what is in progress from the collected tracker context and recommend what the user could do next; change nothing until they choose.
- A loose idea → **Chart the map**.
- An **open** map → **Work through the map**.
- A **reached** map → report that its destination was reached, and stop.

Whichever path, **never resolve more than one ticket per session** unless its type definition explicitly says otherwise.

### Chart the map

1. **Name the destination.** Clarify with the user to pin down what this map is finding its way to — the spec, decision, or change. The destination fixes the scope, so it's settled first.
2. **Map the frontier.** Clarify again, **breadth-first** this time: fan out across the whole space rather than deep on any one thread, surfacing the open decisions and the first steps takeable now. **If this surfaces no fog** — the way to the destination is already clear, the whole journey small enough for one session — you don't need a map. Stop and ask the user how they'd like to proceed.
3. **Create the map**: create its templates, then fill `map.md` with Destination and Notes, an empty Decisions-so-far, and the fog sketched into **Not yet specified**. Fill `domain.md` with the domain language confirmed while clarifying.
4. **Choose each ticket's Type from its configured `Use when`, then create a child ticket for each question you can specify now** — then wire blocking edges in a **second pass** (tickets need tracker identities before they can reference each other). Wiring sorts them into the frontier and the blocked; everything you can't yet specify stays in the fog — the **Not yet specified** section.
5. Follow any `After creation` behavior specified by the new tickets' Type definitions.
6. Stop — charting is one session's work; it hand-resolves nothing.

### Work through the map

A ticket is **optional** — without one, you pick the next decision, not the user.

1. Load the **map** — the low-res view, not every ticket body. With no active ticket there is no decision left to pick: skip to **Check arrival**.
2. Choose the ticket. If the user named one, use it. Otherwise take the first frontier ticket in order. **Claim it** before any work. Then read the Ticket and let the human know which question comes next.
3. Resolve it — **zoom as needed**: fetch the full body of any related or closed ticket on demand; invoke the skills the `## Notes` block names. If in doubt, Clarify it.
4. **Record its resolution using the tracker.**
5. Add newly-surfaced tickets (create-then-wire); graduate any fog the answer has made specifiable, clearing each graduated patch from **Not yet specified** so it lives only as its new ticket. If the answer reveals a ticket — this one or another — sits beyond the destination, **rule it out of scope** rather than resolving it on the route. If the decision invalidates other parts of the map, update or delete those tickets.
6. When this resolution leaves no active ticket, go straight on to **Check arrival** — the same session finishes what it just emptied.

The user may run unblocked tickets in parallel, so expect other sessions to be editing the tracker concurrently.

#### Check arrival

Arriving is the accumulated decisions actually forming a way to the destination. Each session saw only its own ticket, so eyes that carried none of it walk the whole route once before it is declared clear.

1. **Walk the route.** Dispatch one read-only subagent over `map.md`, `domain.md`, and every closed ticket — one, because a contradiction lives in a *pair*, and split walkers hide the pairs that cross between them. It hunts **contradiction** (two decisions that cannot both hold), **gap** (the destination needs a decision no ticket made), and **drift** (a decision that no longer serves the destination), **zooming as needed**: every `## Answer` first so the whole route sits in context, then the bodies against it, then a linked asset only when a finding hangs on it. Every finding comes back with its evidence: it reports, you judge. Dismiss any finding its evidence does not support, with a stated reason; handle the rest below.
2. **Supersede every contradiction already decided, and ticket the rest.** A later ticket that overturned an earlier one decided it, and the earlier answer was simply never propagated: rewrite that ticket's `## Answer` to name the ticket that replaced it, and match its gist in **Decisions so far**, where it stays because it was walked. When both decisions are still live, someone must choose between them — that is a new decision, and the winner gets picked in its ticket.
3. **Clarify every gap into a ticket, or rule it out of scope.** Each patch of **Not yet specified** leaves as one or the other.
4. **Rule every drift out of scope** — its entry moves from **Decisions so far** into **Out of scope**.
5. **Fix bookkeeping in place** — a gist that no longer matches its answer, a dead link, fog that graduated but was never cleared. Nothing is decided, so nothing needs a ticket.
6. **Close the map** when nothing became a ticket. Anything that did leaves the map open, with a frontier for the next session to work.

**Completion:** every closed ticket was read; every finding is superseded, ticketed, ruled out of scope, fixed in place, or dismissed with a stated reason; no fog is left on the map; and the map is recorded as reached, or it stays open on the tickets this check created.
