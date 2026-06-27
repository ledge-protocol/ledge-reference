# Specification Boundary

This repository is not the Ledge Protocol specification.

The protocol specification belongs in LPS-0001 and related LPS documents. This
repository only demonstrates one possible implementation strategy for local
operability.

## Non-Normative Materials

The following are examples, not protocol requirements:

- directory names,
- file names,
- JSON shapes,
- Markdown conventions,
- patch layout,
- transition layout,
- authority approval layout,
- generated context layout,
- generated decision layout,
- agent task layout,
- reproducibility manifest layout,
- hash algorithm,
- canonicalization method,
- prompt layout,
- agent behavior,
- Python module structure,
- test structure.

Another implementation may use a database, content-addressed storage, event
streams, structured logs, generated XML, generated JSON, generated Markdown,
prompts, model-specific context, or another representation entirely and still
be a valid Ledge implementation if it follows the protocol specification.

## What This Repository May Validate

This repository may validate whether the protocol concepts can be made operational:

- intent can be captured,
- claims can be stored,
- evidence can be gathered,
- drift can be detected,
- remediation can be attached,
- transitions can be proposed,
- explicit human authority approval can be required before acceptance,
- state can be recorded after approval,
- accepted knowledge can be transformed into agent-usable context without
  silently mutating state,
- accepted context can be consumed by a deterministic simulated agent workflow
  to produce an evidence-backed decision.
- identical inputs and evidence can reproduce the same local knowledge outputs.

## What This Repository Must Not Claim

This repository must not claim:

- to define the required Ledge file format,
- to define the required Ledge directory structure,
- to define all valid claim types,
- to define all valid evidence types,
- to define the required transition format,
- to define the required authority model,
- to define a required context format,
- to define a required agent decision format,
- to define a required reproducibility manifest,
- to define required SHA-256 usage,
- to define required JSON canonicalization,
- to define required agent behavior,
- to define a required prompt format,
- to be a real LLM evaluation,
- to provide benchmark validity,
- to be a production service,
- to be the only valid implementation.

The authority validation in this repository is intentionally minimal. It checks
local files only so the reference workflow can demonstrate proposed -> approved
-> accepted. LPS documents, not this repository, define protocol boundaries.
Real implementations may use signatures, policies, review systems, governance
processes, or other authority mechanisms without adopting this file layout or
these JSON shapes.

The generated agent context in this repository is a local Markdown artifact for
readability only. It is not a normative serialization format, prompt
engineering framework, SDK surface, MCP interface, or product feature. Ledge
does not define prompt format; Ledge requires the protocol boundary that
accepted knowledge can be transformed into agent-usable context without
silently changing accepted state.

The generated agent decision in this repository is also a local Markdown
artifact for readability only. It is produced by deterministic Python code and
does not call or evaluate a real LLM. Real implementations may provide Ledge
context to Codex, Claude, Cursor, Gemini, MCP, IDEs, local agents, or other
tools, but Ledge does not define how those agents decide or act. This
repository only demonstrates that accepted knowledge can be consumed to
constrain or guide work in a local operability proof.

The reproducibility check in this repository is a local verification fixture.
It uses SHA-256 over normalized text and deterministically serialized JSON, and
it stores expected hashes in a checked-in manifest. That manifest format,
hashing choice, file layout, and canonicalization method are not normative.

Ledge requires reproducibility as a protocol property; real implementations may
prove or verify that property with different mechanisms.
