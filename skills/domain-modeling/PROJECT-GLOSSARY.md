# Project glossaries

A project's standing language lives in a `CONTEXT.md` per **bounded context** — how to locate one, and how to create one when the user asks for a glossary.

## Locating

- A root `CONTEXT-MAP.md` means the repo holds several contexts: read it to find the glossary of the context the topic belongs to. Ask when the topic spans several.
- A root `CONTEXT.md` and no map means the repo holds one context.

## Creating

One context: create its glossary at the repo root.

Several contexts: create the glossary in the directory its context owns, and index it in a root `CONTEXT-MAP.md`, creating the map when the repo has none — a glossary the map does not list cannot be found again.

```md
# {Context name}

{One or two sentences: what this context is and why it exists.}

## Language
```

## Context maps

The map records where each glossary lives and how the contexts relate:

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md) — generates invoices and processes payments
- [Fulfillment](./src/fulfillment/CONTEXT.md) — manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```

A term belongs to exactly one context. Two contexts using the same word for different things is not a collision to settle — each glossary defines that word on its own terms.
