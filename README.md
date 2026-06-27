# ledge-reference

`ledge-reference` is the first minimal reference implementation for the Ledge Protocol.

Its purpose is to show that Ledge can operate end-to-end in a local, file-based workflow:

1. A human records intent.
2. A system records knowledge claims.
3. Evidence is collected from the working reality.
4. Drift is detected when claims and reality disagree.
5. A patch or next action can be associated with that drift.

This repository is intentionally small. It validates operability, not completeness.

## What This Repository Is

- A reference implementation for experimenting with Ledge workflows.
- A local file-based example of intent, claims, evidence, patches, state, and context.
- A small executable check that demonstrates drift detection against an example project.
- A place to test whether the concepts in LPS-0001 can be made operational.

## What This Repository Is Not

- It is not the Ledge Protocol specification.
- It is not a normative file format.
- It is not a cloud service.
- It is not a product.
- It is not a full CLI.
- It is not the only valid way to implement Ledge.

## Relationship To LPS-0001

LPS-0001 defines the protocol-level concepts and boundaries for Ledge.

This repository does not replace, extend, or normatively define LPS-0001. Instead, it provides a small working implementation that exercises those concepts in one concrete environment: a local directory containing files.

If this repository and LPS-0001 disagree, LPS-0001 is the authority.

## Operability

In this repository, "operability" means that the protocol concepts can be used together in a running local workflow.

For this reference implementation, that means:

- intent can be represented as a file,
- claims can be represented as files,
- evidence can be collected from local source files,
- drift can be detected by comparing claims to evidence,
- state can record the result,
- patches can describe a possible remediation.

The implementation is deliberately narrow. It only demonstrates that the loop can close.

## Example Scenario

The example in `examples/auth-migration/` models this situation:

- Human intent: replace Clerk with BetterAuth.
- Knowledge claim: authentication uses BetterAuth.
- Reality: source files still contain Clerk references.
- Drift: the claim says the migration is complete, but the working reality still references Clerk.

Run the tests with:

```bash
python -m unittest discover
```

Run the local example script with:

```bash
python examples/auth-migration/run.py
```

You can also inspect the example directly under:

```text
examples/auth-migration/.ledge/
```

## Why Minimal

This repository avoids product, platform, and serialization commitments on purpose.

The first question is not whether Ledge has a polished interface. The first question is whether intent, claims, evidence, drift, and remediation can be connected in a coherent operational loop. This repository exists to answer that question with the fewest moving parts possible.
