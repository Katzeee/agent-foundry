---
name: to-goal
description: Write a goal with a checkable finish line and a prompt to start it.
argument-hint: "Goal focus or reference paths"
disable-model-invocation: true
---

A **goal** is one durable objective paired with a completion condition that something other than the working agent can check. The agent keeps working turn after turn without being re-prompted, and stops when that condition is judged met.

Three properties of that loop shape everything below:

- Continuing is its default action; returning control to the user is an exception, not a step the document can schedule.
- Completion is judged by a checker that did not do the work and does not share the reasoning behind it.
- The harness is not guaranteed to carry the objective past this session, so the document is what holds it.

This skill writes that document and hands back a prompt to start it.

## Establish the goal

Read the current conversation as the primary source of intent, then the documents and artifacts the user names or the goal depends on. Use arguments to focus that reading. When sources conflict, the user's latest explicit decision controls.

Name one objective. When the intent covers several results that do not share a finish line, have the user pick the one this goal is for. When the finish line cannot be stated yet, or one turn of ordinary work would reach it, say which part of the definition the work fails and stop.

The goal is **ready** when it runs unattended: the document names what the work depends on, every input and reference is obtainable by the agent without user action, every permission it needs is already granted, and the finish line can be judged by a checker that did not do the work. Settle whatever keeps it from being ready with the user before writing files.

## Write the goal document

Resolve the location from the user's request or project guidance. Ask before writing files when neither provides one.

Read and follow [goal-template.md](references/goal-template.md). It is the single source of truth for the document's contents.

Write the finish line for that checker: it decides yes or no without redoing the work or reconstructing why the evidence matters. What form that takes follows the goal — a command's outcome, a threshold, a state of the tree, or an artifact and the standard its content must meet. Fix what must be true, and leave the route to it open.

## Add context when needed

When the agent needs guidance or current state beyond the goal itself, read and follow [goal-context-template.md](references/goal-context-template.md) and create `<goal-stem>-context.md` beside the goal document, where `<goal-stem>` is that document's filename without its extension. Link it from References.

The goal document stays self-sufficient about what the goal is and when it is complete; the context says how to pursue it and where the work stands. Keep substantial source material in its existing document or a focused supporting one, and reach it through links.

## Check the goal

Reread everything written in this invocation — the goal document, its context, and any supporting document — against the user's latest intent and its governing references. Revise them if anything the user wants is missing, anything they did not ask for has become part of the goal, or the goal no longer runs unattended.

Read Outcome and Complete when together: Complete when is Outcome made checkable — the same result in a form the checker can judge, neither more nor less.

The check is done when the goal is ready and a checker with no memory of this conversation could return a defensible yes or no from the named evidence.

## Hand off

**Do not start the goal in this invocation.**

Give the user one compact prompt they can paste to start it. It points at the goal document by path, states that the objective is the entire result that document defines, and, when a context exists, points at it and tells the agent to keep it current.
