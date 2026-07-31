---
name: domain-modeling
description: Build and sharpen domain language. Use when Wayfinder needs a domain model scoped to its active map, or when the user explicitly asks to create or maintain a persistent project domain model or ubiquitous language.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary down the moment terms crystallise. (Merely reading a glossary for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## Choose the mode

Select one mode before persisting.

Use **Wayfinder mode** while Wayfinder is clarifying a destination, mapping a frontier, or resolving a ticket. Scope persistence to the active map's existing `domain.md`, beside its `map.md`.

Use **persistent mode** when the user explicitly asks to create or maintain a project-level domain model or ubiquitous language. Scope persistence to the applicable project-level `CONTEXT.md` files.

Use [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md) for the glossary structure and rules in both modes. In persistent mode, also follow its single- and multi-context discovery rules. When neither mode applies, remain read-only.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the active glossary, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update the glossary inline

When a term is resolved, update the active mode's glossary right there. Don't batch these up — capture them as they happen. In Wayfinder mode, update the existing `domain.md`; in persistent mode, update the applicable `CONTEXT.md`.

The glossary should be totally devoid of implementation details. Do not treat it as a spec, scratch pad, decision log, or implementation document. It is a glossary and nothing else.
