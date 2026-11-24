---
name: second-pass
description: After a feature or refactor, use the diff to find a better structure for the next change of the same kind.
disable-model-invocation: true
---

# Second Pass

**Goal:** clear abstractions unify related behavior and make the next change of the same kind more focused. A change's **radius** is the set of files it had to touch. That radius is evidence about structure: each touched file either owns the changed rule, or depends on it through a deliberate seam, or reveals that some rule, identity or decision is spread across places that should defer to one owner.

Use the change just finished as the entry point, not the boundary. Investigate however you judge best: read the diff, trace why each file had to move, then follow each concept outward to everywhere it lives. For each concept, ask what structure would have made this change a one-place edit, and design that structure. A better model may be a new abstraction, a merged pair of structures, a deleted layer, or a reorganised module; propose it at whatever scale the evidence supports, larger restructurings included. Rank the proposals by how much future change they save against what they cost. The work is done when:

- every touched file is explained by the concept that forced it to change;
- every concept spread across places has a designed single owner; any rejected consolidation demonstrates concretely why that design fails;
- each proposal states:
  - which structures it introduces, reshapes, or removes;
  - which files the next similar change would touch afterwards;
  - which behaviour, if any, would differ.

Report the verdict, then stop until the user picks what to act on:

- **contained**: the structure already has one owner per concept;
- **spread**: the concepts that need consolidating, each with its proposal;
- **inherent**: the change is genuinely cross-cutting.

## Judging

- Distinguish a rule repeated across files from consumers depending on its single owner. Consolidate the former; verify the latter share the same rule.
- Smells to recognise:
  - a value threaded separately through layers;
  - a cost hidden behind something that looks cheap, such as I/O inside a property or per-item work inside a loop.
- A consolidation may widen the radius once. Judge it by unified rules, clear responsibilities, and a more focused next change; file count and deletion volume are evidence, not goals.
