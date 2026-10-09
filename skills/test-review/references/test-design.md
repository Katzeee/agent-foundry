# Test design and verification

This reference covers how test behavior is expressed and verified. [Suite admission](../SKILL.md) determines whether that protection belongs in the suite.

## Test design

- **Behavior:** use the smallest boundary that faithfully exposes the contract. Internal reorganization should pass; interactions, ordering, or bytes deserve exact checks when they are the contract.
- **Independent oracle:** derive expectations from requirements or independently checked examples, not the implementation's own result or logic. Keep the claimed production behavior real.
- **DAMP:** make decisive inputs and assertions visible. Share infrastructure; use comments for non-obvious reasons.
- **Cohesion:** one behavior may require multiple assertions. Name parameter classes and checkpoints; share expensive setup without hiding unrelated scenarios or failure locations.
- **FIRST:** seek fast, independent, repeatable, self-verifying, timely execution. Control state, time, randomness, and completion while preserving necessary fidelity.
- **Integrity:** justify weakened assertions, updated snapshots, skips, retries, discovery changes, and thresholds by their effect on the protection.

## Oracles and negative cases

An independently computed expectation can be valid. Sharing a production builder or copying its branches into the expectation can reproduce the production error.

Keep other prerequisites valid so a negative case reaches its intended guard. Use a successful control or a specific semantic error to distinguish rejection from setup failure. Assert exact wording only when wording is promised output.

## Mocks and seams

Control external responses or expensive boundaries while exercising the behavior under review. Returning and asserting a stub's programmed answer establishes no production behavior.

Interaction assertions can verify contracts such as one emitted charge or resource release. Check relevant arguments, count, or order. When mock setup reconstructs the implementation, prefer a bounded real collaborator. A fake needs fidelity for the behavior relied upon; it cannot establish an external integration contract by itself.

A clock or IO abstraction can have a production responsibility. Move observations to that boundary before exposing private intermediates solely for assertions.

## State and asynchronous work

Use independent mutable state, owned cleanup, and replayable randomness. Arrange relevant interleavings through events, barriers, or a controllable scheduler. Wait for observable completion with a deadline; a fixed sleep establishes no readiness.

Intermittent failure can expose a production race. Locate the cause before altering retries or timeouts. If quarantine or skipping is authorized, identify the protection lost and unresolved defect; a passing rerun is not a repair.

## Snapshots and source inspection

Regeneration creates a candidate expectation. Compare observations with the intended contract. Normalize only incidental values, preserving meaningful timing, ordering, or formatting.

Exact checks can protect published formats, generated artifacts, or architecture rules. Source inspection that fails on a harmless rename while surviving a broken behavior is a weak substitute for exercising the behavior.

## Parameter cases and properties

Group equivalent scenarios, not merely similar setup. A replay can protect idempotency beyond a happy path; shared conformance assertions can test different adapters. Each added class goes through the main skill's admission workflow.

Properties need domain-derived invariants and replayable failures. Round trips can hide matching errors in both implementations; use independent examples when interoperability matters.

## Verification

During implementation:

1. Write only admitted changes within the user's authorized scope.
2. For a bug regression, demonstrate failure on defective behavior and success after repair when feasible. Compilation or unrelated setup failures do not demonstrate the intended defect. Existing-behavior tests may pass immediately.
3. Use bounded counterexamples or mutation when doubtful assertions warrant them. A surviving mutation can mean an equivalent implementation, missing protection, or an unsuitable experiment; investigate before interpreting it. Restore experiments without disturbing other work.
4. Run affected tests and repository-required checks. Reconcile actual assertions and results with the admitted contract. Report missing evidence and blocked checks.

During review-only work, inspect actual assertions and available execution evidence; run existing tests or bounded counterexamples when needed to resolve a claim. Keep recommended changes as proposals.

Verification is complete when the reported assertions protect the admitted behavior and required checks pass, or their limitations are explicit. If a result disproves an admission premise, return to the main skill's evidence record.

## Sources

Supporting sources:

- Behavior and DAMP: [Google unit testing](https://abseil.io/resources/swe-book/html/ch12.html).
- FIRST: [Clean Tests](https://www.oreilly.com/library/view/clean-code-a/9780135398586/ch15.xhtml), [Cornell](https://www.cs.cornell.edu/courses/cs3110/2014fa/recitations/2/rec02.html).
- Failure patterns: [change detectors](https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html), [test doubles](https://abseil.io/resources/swe-book/html/ch13.html), [non-determinism](https://martinfowler.com/articles/nonDeterminism.html).
- Experimental limits: [equivalent mutants](https://stryker-mutator.io/docs/mutation-testing-elements/equivalent-mutants/), [round-trip invariants](https://hypothesis.works/articles/encode-decode-invariant/).
