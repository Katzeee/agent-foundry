# Ticket Types

Every ticket has exactly one Type, persisted by the issue tracker. Type definitions own interaction and resolution behavior; the tracker only stores the Type name.

**HITL** means human in the loop: the ticket is worked with a human who speaks for themselves. The agent never stands in for the human's side. **AFK** means the agent drives the ticket alone.

## research

<!-- wayfinder-setup
requires:
  - skill: research
    install: npx skills@latest add mattpocock/skills --skill=research
-->

- **Interaction:** AFK
- **Use when:** Knowledge outside the current working directory is required to surface a fact that a decision awaits.
- **Resolve:** Use a `/research` subagent. Record the findings and their sources as the answer.
- **After creation:** Start newly-created research tickets in parallel, capturing each subagent's findings on a throwaway `research/<name>` branch with a context pointer from the ticket. Research tickets are the exception to the one-ticket-per-session limit.

## prototype

<!-- wayfinder-setup
requires:
  - skill: prototype
    install: npx skills@latest add mattpocock/skills --skill=prototype
-->

- **Interaction:** HITL
- **Use when:** A cheap, rough artifact would make “how should it look?” or “how should it behave?” concrete enough for useful feedback.
- **Resolve:** Create the artifact via `/prototype`, link it from the ticket, and resolve only through the human's reaction to it.

## grilling

<!-- wayfinder-setup
requires:
  - skill: grilling
    install: npx skills@latest add mattpocock/skills --skill=grilling
  - skill: domain-modeling
    install: npx skills@latest add mattpocock/skills --skill=domain-modeling
-->

- **Interaction:** HITL
- **Use when:** A decision needs focused conversation. This is the default type.
- **Resolve:** Use `/grilling` and `/domain-modeling`, one question at a time. Resolve only through the live exchange.

## task

- **Interaction:** AFK when the agent can do the work alone; otherwise HITL.
- **Use when:** Manual work must happen before a decision can be made, with nothing yet to decide, prototype, or research. It unblocks a decision rather than delivering the destination.
- **Resolve:** Do the work where possible; otherwise give the human a precise checklist. Record what was done and any resulting facts that later tickets depend on.
