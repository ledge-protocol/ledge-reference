# ledge-reference

`ledge-reference` is the first minimal reference implementation for the Ledge Protocol.

Its purpose is to show that Ledge can operate end-to-end in a local, file-based workflow:

1. A human records intent.
2. A system records knowledge claims.
3. Evidence is collected from the working reality.
4. Drift is detected when claims and reality disagree.
5. A patch or next action can be associated with that drift.
6. A proposed transition can become accepted only after explicit human authority approval.
7. Accepted state can be transformed into agent-readable context.
8. Agent-readable context can be consumed by a deterministic simulated agent
   workflow to produce an evidence-backed decision.
9. Identical local evidence and inputs can be checked for reproducible
   knowledge outputs.

This repository is intentionally small. It validates operability, not completeness.

## What This Repository Is

- A reference implementation for experimenting with Ledge workflows.
- A local file-based example of intent, claims, evidence, patches,
  transitions, authority, state, and context.
- A small executable check that demonstrates drift detection against an example project.
- A generated context artifact showing accepted knowledge as guidance for an agent.
- A deterministic agent consumption simulation that reads that context before
  producing an evidence-backed decision.
- A reproducibility check showing that identical auth migration inputs produce
  stable drift, accepted state, context, and decision hashes.
- A place to test whether the concepts in LPS-0001 can be made operational.

## What This Repository Is Not

- It is not the Ledge Protocol specification.
- It is not a normative file format.
- It is not a normative JSON shape.
- It is not a normative Markdown shape.
- It is not a prompt format.
- It is not an agent behavior specification.
- It is not a real LLM evaluation or benchmark.
- It is not a normative reproducibility manifest.
- It is not a normative hash or canonicalization scheme.
- It is not a normative authority system.
- It is not a cloud service.
- It is not a product.
- It is not a full CLI.
- It is not the only valid way to implement Ledge.

## Relationship To LPS-0001

LPS-0001 defines the protocol-level concepts and boundaries for Ledge.

This repository does not replace, extend, or normatively define LPS-0001.
Instead, it provides a small working implementation that exercises those
concepts in one concrete environment: a local directory containing files.

If this repository and LPS-0001 disagree, LPS-0001 is the authority.

## Operability

In this repository, "operability" means that the protocol concepts can be used
together in a running local workflow.

For this reference implementation, that means:

- intent can be represented as a file,
- claims can be represented as files,
- evidence can be collected from local source files,
- drift can be detected by comparing claims to evidence,
- state can record the result,
- patches can describe a possible remediation,
- transitions can remain proposed until explicit human approval is recorded,
- accepted state can be updated after approval,
- accepted knowledge can be rendered into agent-usable context without silently
  mutating state,
- generated context can guide a deterministic simulated agent decision without
  claiming real-world agent behavior.

The implementation is deliberately narrow. It only demonstrates that the loop
can close. The local directories and JSON documents are reference fixtures, not
protocol requirements.

## Example Scenario

The example in `examples/auth-migration/` models this situation:

- Human intent: replace Clerk with BetterAuth.
- Knowledge claim: authentication uses BetterAuth.
- Reality: source files still contain Clerk references.
- Drift: the claim says the migration is complete, but the working reality still references Clerk.
- Patch proposal: mark the migration as incomplete.
- Transition: propose the accepted-state update.
- Authority: a human approval record accepts the transition.
- New accepted state: the migration is no longer marked complete.
- Agent context: the accepted incomplete state, supporting evidence, corrected
  assumptions, and guidance are rendered for an agent continuing the migration.
- Agent decision: a deterministic simulated agent reads the generated context
  and task, consults source-scan evidence, avoids stale completion assumptions,
  and refuses to mark the migration complete.
- Reproducibility: the same local loop is run twice and compared against a
  checked-in non-normative hash manifest.

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

The first question is not whether Ledge has a polished interface. The first
question is whether intent, claims, evidence, drift, and remediation can be
connected in a coherent operational loop. This repository exists to answer that
question with the fewest moving parts possible.

The authority check in this repository is intentionally minimal: it loads a
local approval record, verifies that it explicitly approves the proposed
transition, and then validates the resulting accepted state. Real
implementations may use signatures, organizations, quorum rules, policy
engines, audit logs, or other authority systems.

The generated agent context is also intentionally minimal and non-normative.
This repository uses Markdown only because it is easy to inspect in a small
reference implementation. Real implementations may generate XML, JSON,
Markdown, database records, prompts, model-specific context, or another
representation. Ledge does not define prompt format; it only requires that
accepted knowledge can be transformed into agent-usable context without
silently mutating accepted state.

The agent decision step is also intentionally deterministic and non-normative.
It does not call OpenAI, Anthropic, Claude, Codex, Gemini, Cursor, or any other
external service. It does not evaluate a real LLM. The checked-in Markdown
decision format is only a readable fixture for this repository. Real
implementations may provide accepted context to Codex, Claude, Cursor, Gemini,
MCP, IDEs, local tools, or other agents, but Ledge does not define how those
agents behave. This proof is about local operability, not benchmark validity.

The reproducibility check is also non-normative. This repository uses SHA-256
over normalized text and deterministically serialized JSON because that is
small and easy to verify locally. Ledge requires reproducibility as a protocol
property, not this manifest format, hash algorithm, file layout, or
canonicalization method. Real implementations may verify reproducibility by
other means.
