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
- prompt layout,
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
  silently mutating state.

## What This Repository Must Not Claim

This repository must not claim:

- to define the required Ledge file format,
- to define the required Ledge directory structure,
- to define all valid claim types,
- to define all valid evidence types,
- to define the required transition format,
- to define the required authority model,
- to define a required context format,
- to define a required prompt format,
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
