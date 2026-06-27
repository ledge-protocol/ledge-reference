from __future__ import annotations

from dataclasses import asdict, is_dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .operability import (
    apply_authority_approval,
    inspect_auth_migration,
    load_authority_approval,
    load_json,
    load_proposed_transition,
    validate_new_accepted_state,
    write_agent_context,
    write_agent_decision,
)


LF = chr(10)
REPRODUCIBILITY_KEYS = (
    "agentContext",
    "agentDecision",
    "acceptedState",
    "driftResult",
)


def normalize_line_endings(text: str) -> str:
    return text.replace("\r\n", LF).replace("\r", LF)


def stable_text_hash(text: str) -> str:
    normalized = normalize_line_endings(text)
    return sha256(normalized.encode("utf-8")).hexdigest()


def stable_json_text(value: Any) -> str:
    return json.dumps(
        _to_jsonable(value),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ) + LF


def stable_json_hash(value: Any) -> str:
    return stable_text_hash(stable_json_text(value))


def collect_auth_migration_reproducibility_outputs(
    example_root: Path,
) -> dict[str, str]:
    drift_result = inspect_auth_migration(example_root)

    transition = load_proposed_transition(
        example_root, "mark-auth-migration-incomplete.proposed.json"
    )
    approval = load_authority_approval(example_root, "founder-approval.json")
    accepted_transition = apply_authority_approval(example_root, transition, approval)
    accepted_state_result = validate_new_accepted_state(
        example_root, accepted_transition
    )
    accepted_state = load_json(
        example_root / ".ledge" / accepted_state_result.accepted_state_path
    )

    agent_context = write_agent_context(example_root)
    agent_decision = write_agent_decision(example_root)

    return {
        "agentContext": stable_text_hash(agent_context.markdown),
        "agentDecision": stable_text_hash(agent_decision.markdown),
        "acceptedState": stable_json_hash(accepted_state),
        "driftResult": stable_json_hash(drift_result),
    }


def run_auth_migration_reproducibility_check(example_root: Path) -> dict[str, str]:
    first_run = collect_auth_migration_reproducibility_outputs(example_root)
    second_run = collect_auth_migration_reproducibility_outputs(example_root)

    if first_run != second_run:
        raise ValueError("Reproducibility check failed: repeated runs differ.")

    expected_outputs = load_expected_reproducibility_outputs(example_root)
    if first_run != expected_outputs:
        mismatched = ", ".join(
            key
            for key in REPRODUCIBILITY_KEYS
            if first_run.get(key) != expected_outputs.get(key)
        )
        raise ValueError(
            "Reproducibility check failed: output hashes differ from manifest "
            f"for {mismatched}."
        )

    return first_run


def load_expected_reproducibility_outputs(example_root: Path) -> dict[str, str]:
    manifest_path = (
        example_root / ".ledge" / "reproducibility" / "expected-outputs.json"
    )
    manifest = load_json(manifest_path)
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict):
        raise ValueError("Reproducibility manifest must include outputs.")

    expected = {}
    for key in REPRODUCIBILITY_KEYS:
        value = outputs.get(key)
        if not isinstance(value, str):
            raise ValueError(f"Reproducibility manifest missing {key} hash.")
        expected[key] = value

    return expected


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _to_jsonable(asdict(value))

    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]

    return value
