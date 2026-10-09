---
name: test-review
description: Review test value, design, and coverage trade-offs. Use when deciding whether implementation work needs tests, when adding, modifying, or removing tests or test support, when changing test execution settings, or when reviewing an existing test suite.
---

# Test admission

Start with reject. Admit a maintained test only after concrete evidence establishes its continuing protection and justifies its cost.

## 1. Scope

Read the requested behavior, repository conventions, production owner, and nearby coverage. Identify each scoped test and parameter class, including existing tests and consumers of changed shared support or execution settings. Distinguish current-task edits from pre-existing work.

Keep the scope local to the request. Scope is complete when every affected test or candidate is accounted for; an unrelated suite is outside it. A review request authorizes inspection and recommendations, not test edits.

## 2. Record evidence

Inspect the actual assertions for existing tests. Establish required behavior from its consumer and authoritative sources, independently of the test's expectations. Gather existing execution evidence or use a bounded counterexample when needed to resolve a claim.

Complete this record for each test or case. Name the code, tests, dependency guarantees, or recorded decisions inspected; distinguish observations from assumptions.

| Judgment | Required evidence | Reject when |
|---|---|---|
| **Contract** | A current consumer; the condition, action, and observable result it relies on; the consequence of failure; the authoritative requirement | No present consumer or consequential behavior is established |
| **Discrimination** | A plausible change to this repository's own logic; the unintended failure a reviewer could miss because its effect appears elsewhere, after a sequence or timing, or on a rare path; an equivalent implementation change the test tolerates | Only the edited implementation, an intentional rename, or another effect directly reviewed in the diff is restated |
| **Contribution** | The existing assertions, types, dependency guarantees, and review practices actually checked; why they leave that failure undetected | Additional protection is asserted without inspecting existing protection, or merely repeats a dependency guarantee or existing assertion |
| **Cost** | Expected execution, reading, diagnosis, upkeep, and false-alarm costs; why the established protection warrants those costs | Costs are unexamined or their justification relies on speculative benefit |

An intentional edit can have an unintended downstream effect. Identify that effect and the gap in existing protection, rather than treating every visible edit as either automatically covered by review or automatically deserving a test.

Evidence is complete when every judgment has a concrete answer or an identified missing premise. A missing premise remains a reason for rejection, not an invitation to invent a plausible story.

## 3. Decide

Record one decision before creating or changing test artifacts:

- **Admit:** all four judgments have concrete answers, and the continuing protection warrants the cost.
- **Reject:** a judgment is unsupported, speculative, or meets a rejection condition. Name that judgment and the missing evidence. For a scoped existing test, recommend **Remove** and identify the protection lost; replacement is optional.
- **Unresolved contract:** authoritative sources cannot determine required behavior. Hold the dependent change and name the missing product decision. Insufficient evidence of test value is **Reject**, not a request for the user to justify a test.

Apply the same burden to new, existing, and mechanically touched tests, including tests written earlier in the current task. Past effort earns no presumption of retention.

Admission uses complete evidence, not points that compensate for a missing judgment. Cheap execution, readable design, green results, a historical bug, or a successful mutation check cannot fill a missing premise. Use those observations only for the specific judgment they establish.

Rejected additions leave no test artifact, including temporary tests. Repository-required checks still apply. This step is complete when every scoped test and case has a decision with its evidence or rejection reason.

## 4. Follow the decision

Implement admitted changes authorized by the task. Run affected tests and repository-required checks, and report missing verification. During a review, keep edits as proposals.

If inspection or execution contradicts an admission premise, return to the evidence record and revise the decision. Improved design or successful execution cannot rescue an unsupported admission.

For rejection or an unresolved contract, report the decision and any required checks without creating a replacement by default.

## 5. Deliver

Report each decision, the decisive evidence, and the actual execution scope. Complete when every scoped test and case is accounted for, authorized admitted work is verified, and blocked checks or unresolved contracts are explicit.

## References

- [Test design and verification](references/test-design.md)
- [Review delivery and examples](references/review-examples.md)
