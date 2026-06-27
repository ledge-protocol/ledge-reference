# Specification Boundary

This repository is not the Ledge Protocol specification.

The protocol specification belongs in LPS-0001 and related LPS documents. This repository only demonstrates one possible implementation strategy for local operability.

## Non-Normative Materials

The following are examples, not protocol requirements:

- directory names,
- file names,
- JSON shapes,
- Markdown conventions,
- patch layout,
- Python module structure,
- test structure.

Another implementation may use a database, content-addressed storage, event streams, structured logs, or another representation entirely and still be a valid Ledge implementation if it follows the protocol specification.

## What This Repository May Validate

This repository may validate whether the protocol concepts can be made operational:

- intent can be captured,
- claims can be stored,
- evidence can be gathered,
- drift can be detected,
- remediation can be attached,
- state can be recorded.

## What This Repository Must Not Claim

This repository must not claim:

- to define the required Ledge file format,
- to define the required Ledge directory structure,
- to define all valid claim types,
- to define all valid evidence types,
- to be a production service,
- to be the only valid implementation.
