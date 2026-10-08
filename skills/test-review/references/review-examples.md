# Review examples

Illustrative proposals, not implemented changes or executed evidence. Link actual tests and follow the [delivery conventions](../SKILL.md#user-review).

## Redelivery must not repeat an operation

The proposed test would protect one applied operation per event ID. It would deliver the same event twice through the real processor and an isolated store, then check that one operation remains. The queue's at-least-once delivery contract makes repetition an actual operating condition.

**Add.** Existing tests cover one delivery, which cannot expose repeated side effects after interrupted acknowledgement. Two deliveries provide focused protection without starting a queue server. This proposal covers sequential redelivery, not every concurrent race.

## Cosmetic button wording

The proposed test would pin the newly approved button phrase by asserting its exact rendered text.

**Do not add.** The actual copy-review process already checks this edit. The phrase is neither a data format nor an automation contract, and no continuing failure mechanism justifies pinning it. Cheap execution alone does not establish admission value.

## A test that restates a derived mapping

An existing test lists every enum variant beside the string a derive macro generates for it and asserts each pair.

**Remove.** The generated strings are the macro's documented behavior, and renaming a variant is a deliberate change its own diff displays, so no silent regression remains. Consumers that rely on particular strings already assert them where they read them. The test only demands a second edit on every intended rename.

## Submitted code must match the execution record

Separate file and standard-input tests protect two code-submission paths. Each starts a service, submits distinctive code, and checks the resulting output and stored source.

**Merge into `submitted_code_is_preserved`.** Keep both input paths as named cases, with independent source and output expectations, and share service startup. Retire the two source tests only after these observations are present in the target. The gain is shared setup and one place to maintain the same contract, not loss of either input category.

## Theme persistence and session expiry

A combined test covers two independently admitted behaviors: the chosen theme survives a reload, and an expired session requires sign-in. It changes the theme, reloads, then expires the session and checks access.

**Split into `theme_survives_reload` and `expired_session_requires_sign_in`.** A theme failure currently prevents the session check from running and obscures which contract fails. Preserve both observations, share browser startup where practical, and isolate state per case. The structural change improves independent execution and diagnosis while keeping setup costs bounded.
