---
name: to-goal
description: Write a compact goal with a clear completion condition and a prompt to start it.
argument-hint: "Goal focus or reference paths"
disable-model-invocation: true
---

Write a goal that makes the result the user wants unmistakable to the next agent. The goal must answer: what exactly should be true when this work is finished? Keep implementation guidance and current state in a goal context when needed.

## Establish the goal

Read the current conversation as the primary source of intent, then read the documents and artifacts the user names or the goal depends on. Use arguments to focus that reading. When sources conflict, the user's latest explicit decision controls.

Identify the result the user wants and its completion boundary. Keep confirmed constraints that affect whether the result counts as complete; place details that only guide how to achieve it in the goal context.

If missing or contradictory information leaves the intended result or its completion boundary materially ambiguous, stop before writing files and tell the user which reference or decision is missing. The goal is clear enough to write when the next agent can identify the intended result and its completion boundary without choosing between competing interpretations.

## Prepare the documents

Resolve the goal document's location from the user's request or project guidance. If neither provides one, ask the user where to save it before writing files.

Use existing durable documents through links. When the next agent needs guidance or current state beyond the goal itself, read and follow [goal-context-template.md](references/goal-context-template.md) to create `<goal-stem>-context.md` beside the goal.

Keep goal-defining details and references in the goal; place implementation guidance and its references in the context. Keep substantial source material in its existing document or a focused supporting document.

Preparation is complete when the output location is resolved and any needed context provides the guidance and current state without redefining the goal.

## Write the goal

Read and follow [goal-template.md](references/goal-template.md). It is the single source of truth for the goal document's contents. The document is complete when it states the intended result, its completion boundary, and any relevant constraints and governing references without relying on the context to explain what the goal is. Link the goal context when one was created.

## Check the goal

Reread the finished goal against the user's latest intent and its governing references. Revise it if anything the user wants is missing, anything they did not ask for has become part of the goal, or the completion boundary is ambiguous.

The check is complete when the next agent can tell exactly what must be true for the goal to be complete without choosing between competing interpretations.

## Hand off

Give the user a concise prompt that starts a persistent Goal for the entire result defined in the goal document.

End the invocation after presenting the prompt; execution belongs to the next agent.
