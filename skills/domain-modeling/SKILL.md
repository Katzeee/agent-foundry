---
name: domain-modeling
description: Ubiquitous language — build and sharpen it while a design is still moving. Use when terms collide, blur, or drift from the code, or when the user asks to create or maintain a glossary.
---

Build and sharpen the **ubiquitous language** while the design is still moving: challenge the words as they are used.

## During the session

- **Challenge collisions.** When a term is used against the glossary's definition, say so at once: "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"
- **Split overloaded terms.** One word carrying two concepts becomes two canonical names: "You're saying 'account' — do you mean the Customer or the User? Those are different things."
- **Collapse synonyms.** Several words for one concept get one winner; the rest go under its `_Avoid_` list.
- **Stress-test with scenarios.** Invent concrete cases that probe the edges of a relationship, and make the user state where one concept stops and the next begins.
- **Cross-reference the code.** When the user says how something works, check whether the code agrees and surface the contradiction: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"
- **Write each term as it settles**, never in a batch at the end.

## Writing it down

Every term this session settles lands in one glossary — the **active glossary**. Pick it before writing anything:

- When the invocation names one — a calling skill, the user, or notes the session loaded — it is the only glossary this session writes.
- Otherwise it is the project glossary: the `CONTEXT.md` of the **bounded context** the topic belongs to. Use [PROJECT-GLOSSARY.md](./PROJECT-GLOSSARY.md) to locate it, and to create one when the user asks for a glossary.
- When the repo has no glossary and the user has not asked for one, stay read-only: sharpen the language in the conversation, gather the terms you settled into your reply, and offer to write them down.

Write only inside its `## Language` section, one entry per term:

```md
**Order**:
A customer's request for goods, priced and accepted but not yet shipped.
_Avoid_: Purchase, transaction
```

- **Be opinionated.** When several words exist for one concept, pick the best and list the rest under `_Avoid_`.
- **Keep definitions tight.** One or two sentences in the words a domain expert would use. Define what it IS, not what it does or how it is stored.
- **Admit only terms this context owns.** General programming concepts — timeouts, error types, utility patterns — stay out however heavily the project uses them. Before adding a term, ask whether the concept is unique to this context.
- **Group under subheadings** when natural clusters emerge; a flat list is right when every term belongs to one cohesive area.

**Completion:** every domain term this session used is now defined in the glossary, left as a stated open question, or rejected as one this context does not own — with no glossary in play, gathered into the reply instead; every collision raised is settled or recorded as an open question; every claim about how the code works was checked against the code; the glossary holds names and definitions and nothing else.
