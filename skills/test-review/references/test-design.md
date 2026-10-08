# Test design at the changed boundary

Consult the relevant branch after applying suite admission. A design technique improves a test; it does not establish that the test belongs in the suite.

## Oracles and negative cases

An independently computed expectation can be valid. The problem is sharing the production implementation's error, such as reusing its builder or copying its branches into the expectation.

Keep other prerequisites valid so a negative case reaches its intended guard. Use a successful control or specific semantic error to distinguish rejection from setup failure. Assert exact wording only when wording is promised output.

A surviving mutation can mean an equivalent implementation, missing protection, or an unsuitable experiment. Investigate before drawing a value judgment; restore the experiment without disturbing other work.

## Mocks and seams

Control external responses or expensive boundaries while exercising the actual behavior under review. Merely returning and asserting a stub's programmed answer adds no evidence about that behavior.

Interaction assertions can verify real contracts, such as one emitted charge or resource release. Check the relevant arguments, count, or order. When mock setup reconstructs the implementation, prefer a bounded real collaborator. A fake needs fidelity for the behavior relied upon; it cannot establish an external integration contract by itself.

A clock or IO abstraction can have a legitimate production responsibility. Move observations to that boundary before exposing private intermediates solely for assertions.

## State and asynchronous work

Use independent mutable state, owned cleanup, and replayable randomness. Arrange relevant interleavings through events, barriers, or a controllable scheduler. Wait for observable completion with a deadline; a fixed sleep does not establish readiness.

Intermittent failure can expose a production race. Locate the cause before altering retries or timeouts. If quarantine or skipping is authorized, identify the protection lost and unresolved defect; a passing rerun is not a repair.

## Snapshots and source inspection

Regeneration creates a candidate expectation. Compare changed observations with the intended contract. Normalize only incidental values, preserving meaningful timing, ordering, or formatting.

Exact checks can protect published formats, generated artifacts, or architecture rules. Source inspection that fails on a harmless rename while surviving a broken behavior is a weak substitute for exercising that behavior.

## Parameter cases and properties

Group equivalent scenarios, not merely similar setup. A replay can protect idempotency beyond a happy path; shared conformance assertions can test different adapters. Each added class still needs admission.

Properties need domain-derived invariants and replayable failures. Round trips can hide matching errors in both implementations; use independent examples when interoperability matters. Select input classes for distinct risks rather than every imaginable combination.

## Sources

Rationale, not mandatory reading on every invocation:

- Admission: [Kent Beck](https://stackoverflow.com/questions/153234/how-deep-are-your-unit-tests/153565#153565), [Khorikov](https://enterprisecraftsmanship.com/posts/unit-test-value-proposition/).
- Behavior and DAMP: [Google unit testing](https://abseil.io/resources/swe-book/html/ch12.html).
- FIRST: [Clean Tests](https://www.oreilly.com/library/view/clean-code-a/9780135398586/ch15.xhtml), [Cornell](https://www.cs.cornell.edu/courses/cs3110/2014fa/recitations/2/rec02.html).
- Failure patterns: [change detectors](https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html), [test doubles](https://abseil.io/resources/swe-book/html/ch13.html), [non-determinism](https://martinfowler.com/articles/nonDeterminism.html).
- Experimental limits: [equivalent mutants](https://stryker-mutator.io/docs/mutation-testing-elements/equivalent-mutants/), [round-trip invariants](https://hypothesis.works/articles/encode-decode-invariant/).
