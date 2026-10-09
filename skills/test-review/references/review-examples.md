# Review delivery and examples

This reference contains presentation conventions and examples for test reviews. [Suite admission](../SKILL.md) owns the admission criteria.

## Deliver the review

Present each test under a behavior-focused heading with a source or diff link and two short paragraphs:

1. State the behavior actually protected, its consumer, and the decisive inputs and observations. Describe proposed protection as a proposal, not an achieved result.
2. Lead with a short bold recommendation in the user's language, such as **Add**, **Remove**, **Merge into X**, or **Split into X and Y**. Give the decisive evidence and cost trade-off.

For admission or retention, name the silent regression and the gap in the existing protection checked. For rejection or removal, name the unsupported judgment; for removal, also state the protection lost. For merging or splitting, name the source and target tests and map retained and retired scenarios. For an unresolved contract, identify the missing product decision.

Account for every scoped test and parameter class. Group entries only when their judgments agree, while identifying each test. Shared-support reviews identify their consumers and any differing effects. Link actual sources; a rejected proposal has no fabricated test link.

Give shared execution scope and results once, with exceptions beside the affected entry. Distinguish **Executed**, **Counterexample exercised**, **Inferred**, and **Not run**. Name commands, intended failures, missing checks, and baseline failures where relevant. Keep proposed changes distinct from implemented ones.

Keep the review in the current delivery, not in comment cards or a separate inventory.

## Examples

These are illustrative decisions, not findings or executed evidence. Their stated premises must be checked in an actual review.

### Redelivery must not repeat an operation

The proposed test protects one applied operation per event ID for a consumer of an at-least-once queue. It delivers the same event twice through the real processor and an isolated store, then checks that one operation remains. The repository's processor owns recording processed event IDs; a change to its acknowledgement order can leave the first operation applied without that record.

**Add.** Single-delivery tests and the queue's delivery guarantee leave the processor's deduplication failure undetected. Reusing the processor/store fixture adds one delivery and one record check without a queue server. A storage refactor preserving idempotency still passes. The extra operation harms the consumer, so this focused cost is justified; the case covers sequential redelivery, not every concurrent race.

### Cosmetic button wording

The proposed test pins a newly approved button phrase by asserting its exact rendered text. The edit changes that phrase directly, and the actual copy-review process checks it. No consumer relies on the phrase as a data format or automation contract.

**Do not add.** Discrimination and Contribution are unsupported: the test restates the visible edit, with no separate downstream failure established. Low execution cost does not supply the missing evidence.

### A test that restates a derived mapping

An existing test lists every enum variant beside the string a derive macro generates and asserts each pair. The macro documents that mapping, and consumers that rely on particular strings already assert them where they read them.

**Remove.** Contribution fails: the dependency guarantee and consumer assertions already supply the claimed protection. An intended variant rename produces a visible diff and this test demands a second edit without detecting a separate failure. The dedicated list of mapping assertions is lost; no uncovered consumer contract has been identified.

### A test that catches its own edit

A proposed test copies the newly edited dispatch table and checks every entry against that copy. It goes red when an entry differs and green after the copy is updated. The consumer behavior and existing integration assertions have not been inspected.

**Do not add.** Contract and Contribution lack evidence. Red/green sensitivity establishes disagreement between two tables, not a consequential failure left undetected by existing protection. Rewriting the assertions or making them faster does not complete admission.

### Submitted code must match the execution record

File and standard-input tests protect two submission paths used by CLI callers. Each starts a service, submits distinctive code, and checks the execution output and stored source. Their premises establish an input-handling regression that affects persisted source while serializer-level tests still pass.

**Merge into `submitted_code_is_preserved`.** Keep file and standard-input cases with independent source and output expectations and share service startup. Retire the source tests only after both admitted observations exist in the target. This reduces duplicate setup while retaining protection for both paths.

### Theme persistence and session expiry

A combined test covers two independently admitted behaviors: a user's theme survives reload, and an expired session requires sign-in. It changes the theme, reloads, then expires the session and checks access. The evidence records establish each consumer, silent regression, existing coverage gap, and justified cost.

**Split into `theme_survives_reload` and `expired_session_requires_sign_in`.** A theme failure currently prevents the session check from running and obscures which contract fails. Preserve both admitted observations, share browser startup where practical, and isolate state per case.
