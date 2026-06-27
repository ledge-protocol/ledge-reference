# Reproducibility

This reference implementation treats reproducibility as a local invariant:
given the same auth migration inputs and evidence, the same minimal Ledge loop
must produce the same knowledge outputs.

The check is intentionally plain text and local. It is designed to be easy to
read in a pull request as well as easy to run from a checkout.

For `examples/auth-migration/`, the reproducibility check runs the local loop
twice and compares stable SHA-256 hashes for:

- the drift detection result,
- the accepted state after the approved transition,
- the generated agent context,
- the generated agent decision.

The expected hashes are recorded in
`examples/auth-migration/.ledge/reproducibility/expected-outputs.json`.

## What Is Checked

Markdown artifacts are hashed as UTF-8 text after line endings are normalized
to LF.

JSON values are serialized with sorted keys and compact separators before
hashing. This makes the local check independent of object key insertion order.

The check detects nondeterminism by running the same local loop twice and
requiring the output hashes to match. It then compares those hashes with the
checked-in manifest.

## Out Of Scope

This repository does not define a normative reproducibility file layout,
manifest shape, hash algorithm, or canonical JSON format.

SHA-256 is used here because it is available in the Python standard library and
is easy to inspect. Ledge does not require SHA-256. Real implementations may
use different canonicalization, content addressing, signatures, consensus
systems, audit logs, or verification methods.

This check does not introduce a CLI, SDK, cloud service, UI, MCP server,
database, authority model, or product behavior.

## Why Deterministic Output Matters

LPS-0001 requires reproducibility as a protocol property: accepted states must
be reproducible from identical evidence. A reference implementation cannot
prove every production design, but it can demonstrate the invariant in a small
local loop.

Deterministic output makes drift, accepted state, generated context, and agent
decision fixtures inspectable. If the same evidence produces a different hash,
the implementation has either changed or become nondeterministic.

## No Generated Time Or Randomness

Generated artifacts do not include current timestamps, random IDs,
machine-specific paths, or environment-specific values. Those values would make
byte-level output vary even when evidence and inputs are identical.

The example may contain historical fixture data, such as a fixed approval
timestamp, but the reproducibility check does not generate new time-dependent
values.
