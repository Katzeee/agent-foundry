---
name: to-goal
description: Write a compact goal document and a prompt to start it.
argument-hint: "Goal focus or reference paths"
disable-model-invocation: true
---

Turn the current conversation and its references into a compact entry point for the next agent. Keep the goal itself at the top of the information hierarchy and disclose supporting detail through links.

## Establish the goal

Read the current conversation as the primary source of intent, then read the documents and artifacts the user names or the goal depends on. Use arguments to focus that reading. When sources conflict, the user's latest explicit decision controls.

The goal is established when the material identifies one desired end state, its scope, the user's completion boundary, and every material constraint.

A missing or contradictory fact is a **critical gap** when resolving it could change any of those four elements. If a critical gap remains, stop before writing files and tell the user which reference or decision would resolve it.

## Build the reference layer

Resolve the goal document's location from the user's request or project guidance. If neither provides one, ask the user where to save it before writing files.

Use existing durable documents as the reference layer. Capture supporting detail that exists only in the conversation in the smallest useful set of documents: default to one `<goal-stem>-context.md` beside the goal, and split only when the subjects will be consulted independently.

Supporting documents hold context, evidence, decisions, and rationale. The reference layer is ready when the next agent can reach every detail needed beyond the goal itself through a link.

## Write the goal

Read and follow [goal-template.md](references/goal-template.md). It is the single source of truth for the goal document's contents. The goal is complete when every statement is supported by the established goal, every reference resolves, and the document remains a compact entry point rather than a specification or plan.

## Hand off

Report the goal document's absolute path, then give the user a concise prompt they can use to start the goal. The prompt should point the next agent to the document, ask it to complete the goal, and direct it to consult the references as needed.

End the invocation after presenting the path and prompt; execution belongs to the next agent.
