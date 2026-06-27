# Operability

This repository treats operability as the ability to close a minimal Ledge loop locally.

The loop is:

1. Record human intent.
2. Record a knowledge claim.
3. Inspect local reality for evidence.
4. Detect disagreement between claim and evidence.
5. Record state and attach a possible remediation.

## Local Workflow

The `examples/auth-migration/` directory contains a deliberately small project reality and a `.ledge/` directory.

The `.ledge/` directory contains:

- `intent/`: the human objective,
- `claims/`: what the system believes is true,
- `evidence/`: observed facts from the local project,
- `patches/`: possible remediation,
- `states/`: observed protocol state,
- `context/`: supporting background.

These names are descriptive for this reference implementation. They are not normative.

## Demonstrated Drift

The example claim says authentication uses BetterAuth and the Clerk migration is complete.

The example source reality still contains Clerk references.

That mismatch is drift.

## Running The Check

Run:

```bash
python -m unittest discover
```

The test exercises the example and confirms that the implementation detects the expected drift.
