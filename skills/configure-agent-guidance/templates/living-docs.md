<!-- agent-foundry:begin living-docs -->
## Living Docs

Keep every document **living**: both its content and its continued existence serve a purpose it has now. When revising documentation, first decide whether the content still needs to exist. Delete any paragraph or entire document that no longer serves a purpose; when facts change in content that remains necessary, rewrite the claim in place rather than parking a newer claim beside the stale one.

Maintained documentation explains semantics, ownership boundaries, constraints, and necessary rationale that code and configuration do not make clear. Keep exact interfaces, defaults, command options, and implementation details in their authoritative source, such as the code, configuration, or tool help, and point readers there. Duplicate such details only when the copy provides enough independent value to justify its synchronization cost.

When you find an error in documentation or a comment, correct it cleanly in place. Do not preserve, annotate, or otherwise leave traces of the erroneous claim; errors need no record.

Past material belongs where it still supports a present claim, or where preserving that record is itself the document's purpose. Revision narration that merely explains how the document reached its current form belongs to neither.

Documentation created to carry temporary work is **scaffolding**. When creating it, state the work it serves, its scope, and the condition that ends its purpose. Once that condition is met, fold any semantics and rationale that remain valid into the documents that own them, then remove the temporary material. Before finishing, account for every temporary document this work touched: each either still serves an active purpose or is gone, with anything durable carried forward first.
<!-- agent-foundry:end living-docs -->
