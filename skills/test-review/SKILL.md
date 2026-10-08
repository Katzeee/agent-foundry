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
4. **Deliver.** Reconcile the decisions with actual assertions and any final diff, then produce the review below. Complete when every scoped test and candidate is accounted for and required checks pass; surface unresolved contracts and blocked checks. Adding no tests is a valid outcome.

## Four judgments

| Judgment | Establish |
|---|---|
| **Contract** | The condition, action, observable result, authoritative requirement, and consequence of failure. For changed expectations, explain which requirement changes. |
| **Discrimination** | A credible failure mechanism this test should catch and an equivalent implementation change it should tolerate. Ground the risk in actual logic, interactions, dependencies, or defect history. |
| **Contribution** | Continuing protection beyond existing tests, types, dependency guarantees, and review practices actually used. For removal, state remaining protection and accepted risk; a complete replacement is not mandatory. |
| **Cost** | Future execution, reading, diagnosis, upkeep, and false-alarm costs relative to expected benefit. Consider likely changes and failure impact; distinguish assumptions from observations. Past writing effort is sunk. |

## Admission

**Admit** when the judgments establish continuing protection worth maintaining. A unique assertion, distinct layer, past bug, successful mutation check, or cheap runtime alone is insufficient. Judge the concrete risk and benefit, not coverage or test-count targets. Short, stable code can still merit a test when failure is consequential and difficult to detect.

**Reject** when the benefit only confirms the present edit or does not justify continued upkeep. Rejected additions produce no test artifact; there is no temporary-test fallback. Repository-required checks still run.

**Unresolved contract** means required behavior cannot be determined from the task or authoritative sources. Hold the dependent change and surface that decision. Lack of value in an optional test calls for rejection, not a request that the user invent a justification.

Apply this gate to scoped edits and removals as well as additions. Mechanical edits can preserve established protection without inventing a new regression.

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

Match the explanation to the action: additions and retention need continuing value; rejection needs its admission reason; removal needs remaining protection and accepted loss; modification needs the intended protection change. For merging or splitting, name source and target tests, map retained and retired scenarios, and explain the effect on diagnosis and setup cost. Renames or moves may preserve protection unchanged. Clarification names the missing contract decision, not a vague doubt about value.

Account for every in-scope test and parameter class with its expected outcome. Group entries only when the judgments agree, while identifying each test; shared-support changes identify their consumers and any differing effects. Report actual candidates, not an invented catalogue. Rejected additions have no fabricated source link.

Give shared execution scope and results once, with exceptions beside the relevant entry. Distinguish **Executed**, **Counterexample exercised**, **Inferred**, and **Not run**; identify commands, intended failures, missing checks, and baseline failures as applicable. Keep proposed changes distinct from implemented ones. Green runs do not prove counterexample sensitivity.

Keep the review with the current delivery, not in comment cards or a parallel test inventory. Use [review examples](references/review-examples.md) when calibrating detail.
