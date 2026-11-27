---
name: second-pass
description: After a feature or refactor, or before implementing a plan, find a better structure that replaces the old design.
disable-model-invocation: true
---

# Second Pass

**Goal:** clear abstractions unify related behavior and make the next change of the same kind more focused. A change's **radius** is the set of files it had to touch. That radius is evidence about structure: each touched file either owns the changed rule, or depends on it through a deliberate seam, or reveals that some rule, identity or decision is spread across places that should defer to one owner.

Use the change just finished, or the plan about to be implemented, as the entry point, not the boundary. Investigate however you judge best: read the diff or trace the plan against the current code, trace why each file had to move, then follow each concept outward to everywhere it lives. For each concept, ask what structure would have made this change a one-place edit, and design that structure. A better model may be a new abstraction, a merged pair of structures, a deleted layer, or a reorganised module; propose it at whatever scale the evidence supports, larger restructurings included. Rank the proposals by how much future change they save against what they cost. The work is done when:

- every touched file is explained by the concept that forced it to change;
- every concept spread across places has a designed single owner; any rejected consolidation demonstrates concretely why that design fails;
- each proposal states:
  - which structures it introduces, reshapes, or removes;
  - which files the next similar change would touch afterwards;
  - which behaviour, if any, would differ.

Report findings with every label that applies, then stop until the user picks what to act on:

- **contained**: every concept has one owner, and no spread or patched finding applies;
- **spread**: the concepts that need consolidating, each with its proposal;
- **patched**: the superseded design still constrains the change, with what to remove or reshape;

## Judging

- A change **replaces** the old design or **patches** it. It patches while the old design still constrains it: a compatibility path, callers left on the old route, a rule deferred to later, a new structure bent to fit the old one.
- Distinguish a rule repeated across files from consumers depending on its single owner. Consolidate the former; verify the latter share the same rule.
- Smells to recognise:
  - a value threaded separately through layers;
  - a cost hidden behind something that looks cheap, such as I/O inside a property or per-item work inside a loop.
- A consolidation may widen the radius once. Judge it by unified rules, clear responsibilities, and a more focused next change; file count and deletion volume are evidence, not goals.
- When a change spans responsibilities, explain which changes are necessary and why. If you propose a consolidation, explain which would still be necessary afterward.
