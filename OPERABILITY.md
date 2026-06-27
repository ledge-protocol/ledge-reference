# Operability

This repository treats operability as the ability to close a minimal Ledge loop locally.

The loop is:

1. Record human intent.
2. Record a knowledge claim.
3. Inspect local reality for evidence.
4. Detect disagreement between claim and evidence.
5. Record state and attach a possible remediation.
6. Propose a transition from that remediation.
7. Accept the transition only after explicit human authority approval.
8. Record a new accepted state.
9. Generate agent-readable context from accepted state.
10. Consume that context in a deterministic simulated agent workflow.

## Local Workflow

The `examples/auth-migration/` directory contains a deliberately small project
reality and a `.ledge/` directory.

The `.ledge/` directory contains:

- `intent/`: the human objective,
- `claims/`: what the system believes is true,
- `evidence/`: observed facts from the local project,
- `patches/`: possible remediation,
- `transitions/`: proposed changes to accepted state,
- `authority/`: local approval records for this reference example,
- `states/`: observed protocol state,
- `context/`: supporting background and generated agent-readable context.
- `tasks/`: a local agent task fixture,
- `agent-decisions/`: a local deterministic agent decision fixture.

These names are descriptive for this reference implementation. They are not
normative. The JSON shapes are also non-normative.

## Demonstrated Drift

The example claim says authentication uses BetterAuth and the Clerk migration is complete.

The example source reality still contains Clerk references.

That mismatch is drift.

The example then proposes a transition that marks the authentication migration
as incomplete. The transition remains proposed until a human authority approval
record is loaded and checked. Only after that approval does the example
validate the new accepted state with `authenticationMigrationComplete` set to
`false`.

The example then generates
`examples/auth-migration/.ledge/context/agent-context.md` from the latest
accepted state, intent, transition approval, and evidence. The generated
context tells an agent that the migration is incomplete, lists the remaining
Clerk references, records corrected assumptions, and warns against assuming
migration completion without evidence.

The example then loads
`examples/auth-migration/.ledge/tasks/continue-auth-migration.md`, consumes the
generated context, consults
`examples/auth-migration/.ledge/evidence/source-scan.json`, and writes
`examples/auth-migration/.ledge/agent-decisions/continue-auth-migration.decision.md`.
That decision says the migration is incomplete, references the evidence, avoids
stale assumptions, and refuses to mark the migration complete without evidence.

## Running The Check

Run:

```bash
python examples/auth-migration/run.py
```

The repository tests can be run with:

```bash
python -m unittest discover
```

The example runner prints the drift, patch proposal, proposed transition, human
approval, accepted transition, new accepted state, and generated agent context
status. It also prints the deterministic agent consumption step: context
loaded, task loaded, incomplete migration recognized, stale assumption avoided,
evidence consulted, decision generated, and completion refused without
evidence. The tests confirm that drift is detected, proposed transitions are
not accepted without approval, missing approval fails, transitions must
reference an existing patch, accepted state can generate agent-readable
context, and generated context can drive an evidence-backed simulated agent
decision.

Authority validation here is intentionally minimal. It is enough to demonstrate
explicit human approval in a local reference workflow, but it is not a
prescription for real deployments. Real implementations may use different
authority systems.

The generated Markdown context is intentionally non-normative. Real
implementations may generate XML, JSON, Markdown, database records, prompts,
model-specific context, or another representation. Ledge does not define prompt
format. This reference implementation only demonstrates that accepted knowledge
can be transformed into agent-usable context without silently mutating accepted
state.

The agent consumption workflow is also intentionally non-normative. It is a
deterministic simulation, not a real LLM call and not an evaluation of Codex,
Claude, Cursor, Gemini, MCP, IDE integrations, or any other agent. Real
implementations may provide Ledge context to those tools, but Ledge does not
define agent behavior. This proof demonstrates operability: accepted knowledge
can constrain or guide agent work in a local workflow. It does not claim
benchmark validity.
