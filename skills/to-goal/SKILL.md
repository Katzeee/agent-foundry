---
name: to-goal
description: Write a compact goal with a clear completion condition and a prompt to start it.
argument-hint: "Goal focus or reference paths"
disable-model-invocation: true
---

Turn the current conversation and its references into a clear goal for the next agent. A **completion contract** states the desired outcome and scope, the evidence-based conditions that make the entire goal complete, and the constraints or boundaries that must still hold. Keep this contract in the goal; disclose guidance and current state through a goal context when needed.

## Establish the goal

Read the current conversation as the primary source of intent, then read the documents and artifacts the user names or the goal depends on. Use arguments to focus that reading. When sources conflict, the user's latest explicit decision controls.

The goal is established when the material determines one completion contract. Preserve a verification procedure the user specifies; otherwise identify the evidence that can establish completion while leaving the agent executing the goal free to obtain it.

A missing or contradictory fact is a **critical gap** when resolving it could change the completion contract or leave completion unjudgeable. If a critical gap remains, stop before writing files and tell the user which reference or decision would resolve it.

## Prepare the documents

Resolve the goal document's location from the user's request or project guidance. If neither provides one, ask the user where to save it before writing files.

Use existing durable documents through links. When the next agent needs guidance or current state beyond the goal itself, read and follow [goal-context-template.md](references/goal-context-template.md) to create `<goal-stem>-context.md` beside the goal.

Keep substantial source material in its existing document or a focused supporting document. Link references that define or constrain the completion contract from the goal itself; link references that only guide how to pursue it from the context. Put any detail that changes the completion contract in the goal itself. Preparation is complete when the output location is resolved and any needed context lets the next agent apply the relevant guidance and understand the current state without relying on it to define the contract.

## Write the goal

Read and follow [goal-template.md](references/goal-template.md). It is the single source of truth for the goal document's contents. The document is complete when the next agent can understand the desired outcome, reach its governing sources, and judge whether the entire goal is complete without reading the context. Link the goal context when one was created.

## Hand off

Give the user a concise prompt that starts the entire goal as a persistent objective, with the goal document as its guide.

End the invocation after presenting the prompt; execution belongs to the next agent.
