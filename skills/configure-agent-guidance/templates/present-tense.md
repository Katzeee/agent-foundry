<!-- agent-foundry:begin present-tense -->
## Present Tense

Keep the change in **present tense**. Write code, comments, and tests for the system the request calls for.

When you find an error in code, comments, or documentation, correct it cleanly in place. Do not preserve, annotate, or otherwise leave traces of the erroneous state; errors need no record.

Treat **compatibility and migration** as opt-in. Do not add them because a change feels risky or incomplete; add them when the user asks for them.

An addition earns its place by serving the requested system. It does not earn a place by recording that a replacement happened. Test the behavior the request depends on—prefer assertions that go red when that behavior is wrong over assertions that cannot meaningfully fail.
<!-- agent-foundry:end present-tense -->
