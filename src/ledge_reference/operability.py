from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DriftResult:
    claim_id: str
    drift: bool
    reason: str
    clerk_references: tuple[str, ...]


@dataclass(frozen=True)
class TransitionResult:
    transition_id: str
    status: str
    approval_id: str
    accepted_state_path: str
    authentication_migration_complete: bool


def inspect_auth_migration(example_root: Path) -> DriftResult:
    """Inspect the auth migration example without defining a protocol format."""
    claim_path = example_root / ".ledge" / "claims" / "auth-uses-betterauth.json"
    source_paths = sorted((example_root / "src").rglob("*.ts"))

    claim = json.loads(claim_path.read_text(encoding="utf-8"))
    claimed_complete = claim["migration"]["claimedComplete"]
    clerk_references = tuple(
        str(path.relative_to(example_root))
        for path in source_paths
        if "clerk" in path.read_text(encoding="utf-8").lower()
    )

    drift = claimed_complete and bool(clerk_references)
    reason = (
        "Claim says the Clerk to BetterAuth migration is complete, "
        "but local source files still reference Clerk."
        if drift
        else "Claim and local source evidence do not show this drift."
    )

    return DriftResult(
        claim_id="claim.auth.uses-betterauth",
        drift=drift,
        reason=reason,
        clerk_references=clerk_references,
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_proposed_transition(example_root: Path, transition_name: str) -> dict[str, Any]:
    transition_path = example_root / ".ledge" / "transitions" / transition_name
    transition = load_json(transition_path)
    validate_proposed_transition(example_root, transition)
    return transition


def validate_proposed_transition(
    example_root: Path, transition: dict[str, Any]
) -> None:
    if transition.get("status") != "proposed":
        raise ValueError("Transition must have status proposed before approval.")

    patch_path = transition.get("patchPath")
    if not isinstance(patch_path, str):
        raise ValueError("Transition must reference a patch path.")

    if not (example_root / ".ledge" / patch_path).is_file():
        raise ValueError("Transition must reference an existing patch.")


def load_authority_approval(example_root: Path, approval_name: str) -> dict[str, Any]:
    approval_path = example_root / ".ledge" / "authority" / approval_name
    return load_json(approval_path)


def apply_authority_approval(
    example_root: Path, transition: dict[str, Any], approval: dict[str, Any]
) -> dict[str, Any]:
    validate_proposed_transition(example_root, transition)

    if approval.get("decision") != "approved":
        raise ValueError("Authority approval must explicitly approve the transition.")

    if approval.get("transition") != transition.get("id"):
        raise ValueError("Authority approval must reference the transition.")

    accepted_transition = dict(transition)
    accepted_transition["status"] = "accepted"
    accepted_transition["approval"] = approval["id"]
    return accepted_transition


def validate_accepted_transition(transition: dict[str, Any]) -> None:
    if transition.get("status") != "accepted":
        raise ValueError("Transition is not accepted.")

    if not transition.get("approval"):
        raise ValueError("Accepted transition must record approval.")


def validate_new_accepted_state(
    example_root: Path, accepted_transition: dict[str, Any]
) -> TransitionResult:
    validate_accepted_transition(accepted_transition)

    state_path = accepted_transition.get("acceptedStatePath")
    if not isinstance(state_path, str):
        raise ValueError("Accepted transition must reference a new accepted state.")

    state = load_json(example_root / ".ledge" / state_path)

    if state.get("acceptedTransition") != accepted_transition.get("id"):
        raise ValueError("New accepted state must reference the accepted transition.")

    complete = state.get("authenticationMigrationComplete")
    if complete is not False:
        raise ValueError(
            "New accepted state must mark authentication migration complete as false."
        )

    return TransitionResult(
        transition_id=accepted_transition["id"],
        status=accepted_transition["status"],
        approval_id=accepted_transition["approval"],
        accepted_state_path=state_path,
        authentication_migration_complete=complete,
    )
