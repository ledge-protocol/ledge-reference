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
status. The tests confirm that drift is detected, proposed transitions are not
accepted without approval, missing approval fails, transitions must reference an
existing patch, and accepted state can generate agent-readable context.

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
