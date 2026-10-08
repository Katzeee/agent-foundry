---
name: test-review
description: Review test value, design, and coverage trade-offs. Use when deciding whether implementation work needs tests, when adding, modifying, or removing tests or test support, when changing test execution settings, or when reviewing an existing test suite.
---

# Test review

Judge which tests earn a place in the maintained suite, whether they protect the claimed behavior, and how authorized changes should express it. Give the user a reviewable judgment for each scoped test or candidate.

During implementation, review the affected tests and candidates, including whether a test is needed at all. For an existing-suite review, cover the requested tests and their shared support. Do not expand a local change into a whole-suite audit. A review request alone does not authorize test edits.

## Workflow

1. **Scope.** Read the requested behavior, repository conventions, production owner, and nearby coverage. Identify every in-scope logical test or candidate, including consumers of reviewed support or execution settings, and distinguish this task's edits from pre-existing work.
2. **Decide.** Apply the four judgments and admission rule below before editing. Every candidate gets an admit, reject, or unresolved-contract decision. Extend an existing scenario when it provides the needed protection.
3. **Implement and verify.** For review-only work, inspect actual assertions and available execution evidence; keep recommended edits as proposals. When implementation is in scope, write admitted changes using the design principles and run affected tests and repository-required checks. For a bug regression, demonstrate failure on defective behavior and success after repair when feasible; report missing evidence. Compilation or unrelated setup failures do not demonstrate the intended defect. Existing-behavior tests may pass immediately. Use bounded counterexamples or mutation when risk or doubtful assertions warrant them.
4. **Deliver.** Reconcile the decisions with actual assertions and any final diff, then produce the review below. Complete when every scoped test and candidate is accounted for and required checks pass; surface unresolved contracts and blocked checks. Adding no tests and removing tests are valid outcomes.

## Four judgments

Each judgment is a proof obligation, answered concretely from code, tests, or recorded decisions.

| Judgment | Establish |
|---|---|
| **Contract** | The condition, action, and observable result, and the consumer relying on it today: a caller, user, component, persisted data, or recorded decision, with the consequence it suffers when the behavior breaks. For changed expectations, explain which requirement changes. |
| **Discrimination** | The **silent regression**: a plausible change to this repository's own logic that breaks the contract while its author, reviewing that change, would miss the break, because the effect appears far from the edit, after a particular sequence or timing, or on a rare path. Ground it in actual logic, interactions, or defect history, and name an equivalent implementation change the test tolerates. |
| **Contribution** | The existing tests and assertions, types, dependency guarantees, and review practices actually used that you checked, and why the silent regression passes all of them. Behavior a dependency documents, such as a derive macro's output or a serializer's round trip, is that dependency's guarantee. |
| **Cost** | Future execution, reading, diagnosis, upkeep, and false-alarm costs relative to expected benefit. Consider likely changes and failure impact; distinguish assumptions from observations. |

## Admission

Admission carries the **burden of proof**, and the default is reject. **Admit** only when all four judgments have concrete answers and the protection outweighs its cost; one blank or speculative answer rejects. A unique assertion, literal expectation, distinct layer, past bug, successful mutation check, cheap runtime, or passing run alone is insufficient. A deliberate change its own diff displays, such as a rename or an edited table, is reviewed rather than silent. Judge the concrete risk and benefit, not coverage or test-count targets. Short, stable code can still merit a test when failure is consequential and difficult to detect.

Every scoped test carries the same burden: additions, existing tests, tests written earlier in the current task, and tests touched only mechanically. Past effort and a green history are no evidence. A scoped existing test that fails admission gets **Remove.**, naming the judgment it leaves unanswered; it needs no replacement.

Rejected additions produce no test artifact; there is no temporary-test fallback. Repository-required checks still run.

**Unresolved contract** means required behavior cannot be determined from the task or authoritative sources. Hold the dependent change and surface that decision. Lack of value in an optional test calls for rejection, not a request that the user invent a justification.

## Design principles

- **Behavior:** use the smallest boundary that faithfully exposes the contract. Internal reorganization should pass; interactions, ordering, or bytes deserve exact checks when they are the contract.
- **Independent oracle:** derive expectations from requirements or independently checked examples, not the implementation's own result or logic. Keep the claimed production behavior real.
- **DAMP:** favor descriptive, meaningful scenarios over removing every repeated line. Keep decisive inputs and assertions visible; share infrastructure. Comments explain non-obvious reasons, not the code's actions.
- **Cohesion:** one behavior may require multiple assertions. Name parameter classes and checkpoints; share expensive setup without hiding unrelated scenarios or failure locations.
- **FIRST:** seek fast, independent, repeatable, self-verifying, timely tests. Control state, time, randomness, and completion while preserving necessary fidelity.
- **Integrity:** justify weakened assertions, updated snapshots, skips, retries, discovery changes, and thresholds by their effect on protection; a green run does not justify them.

For oracle doubts, negative cases, mocks, asynchronous work, snapshots, or generated inputs, read the relevant section of [test design](references/test-design.md).

## User review

Complete all four judgments; the following conventions govern presentation only. Present each test under a behavior-focused heading with a source or diff link and two short paragraphs.

**First paragraph:** state the behavior actually protected and how the test checks it. Include decisive inputs and observations, not a transcript of setup calls. For proposed additions, describe intended protection as a proposal, not an achieved result.

**Second paragraph:** lead with a short bold recommendation in the user's language, naming targets when relevant, such as **Add.**, **Remove.**, **Merge into X.**, or **Split into X and Y.** Follow with the decisive reason and trade-off. Describe a material gap once, alongside its consequence or remedy; omit routine implementation detail.

Match the explanation to the action: additions and retention name the consumer, the silent regression, and the coverage checked; rejection and removal name the unanswered judgment, and removal states any protection still lost; modification needs the intended protection change. For merging or splitting, name source and target tests, map retained and retired scenarios, and explain the effect on diagnosis and setup cost. Renames or moves may preserve protection unchanged. Clarification names the missing contract decision, not a vague doubt about value.

Account for every in-scope test and parameter class with its expected outcome. Group entries only when the judgments agree, while identifying each test; shared-support changes identify their consumers and any differing effects. Report actual candidates, not an invented catalogue. Rejected additions have no fabricated source link.

Give shared execution scope and results once, with exceptions beside the relevant entry. Distinguish **Executed**, **Counterexample exercised**, **Inferred**, and **Not run**; identify commands, intended failures, missing checks, and baseline failures as applicable. Keep proposed changes distinct from implemented ones. Green runs do not prove counterexample sensitivity.

Keep the review with the current delivery, not in comment cards or a parallel test inventory. Use [review examples](references/review-examples.md) when calibrating detail.
