---
name: spike
description: Build a temporary artifact that makes evidence observable for one concrete decision.
disable-model-invocation: true
---

# Spike

A spike is **temporary work that makes an unknown observable so a decision can be made**. Its deliverable is the evidence and the decision it supports, not the artifact itself.

## State the decision

Name the one decision this spike is meant to inform. State what is unknown, which routes or claims are in question, and what observation would change the answer. Bound the work by recording what this spike is not deciding.

Complete this step when the record names the decision, the unknown, the observation that could change the answer, and the boundary of the work. If decision-critical context is missing, pause here and ask for it before building.

## Build the smallest useful artifact

Choose the artifact shape from the question. It may be a scratch implementation, data model, benchmark, simulator, visualization, interaction demo, or another form that can expose the relevant evidence.

Preserve the real conditions that could change the answer and simplify everything else. Reuse the repository's types, dependencies, data, and execution paths when they matter; isolate the work from production state and label it as disposable. Give the intended observer a clear path to run or inspect it.

The artifact is ready when a recorded run, interaction, or measurement can produce the decision-relevant observation and all required inputs and entry points are available. Running code alone is not completion.

## Learn from the artifact

Choose the observation that can change the named decision.

Record what was observed separately from what it suggests. Investigate surprising results until they are reproducible, attributable to setup, or recorded as a limitation. Record a changed question as a pivot rather than silently rewriting the original one.

This step is complete when the decision-relevant evidence is captured and its scope and limitations are explicit.

## Capture the decision

Record the question, artifact location and run instructions, material conditions, observations, interpretation, limitations, and the decision or next unknown. Preserve the artifact and raw evidence as a stable primary source linked from the decision record. Keep the implementation disposable; promote only the decision or validated concept into durable work.

Resolve the spike when the evidence lets the decision-maker answer the named decision. If it cannot, leave the decision unresolved and make the next unknown precise enough to investigate.
