from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DriftResult:
    claim_id: str
    drift: bool
    reason: str
    clerk_references: tuple[str, ...]


def inspect_auth_migration(example_root: Path) -> DriftResult:
    """Inspect the auth migration example without defining a protocol format."""
    claim_path = example_root / ".ledge" / "claims" / "auth-uses-betterauth.json"
    source_paths = sorted((example_root / "app").glob("*.ts"))

    claim_text = claim_path.read_text(encoding="utf-8")
    claimed_complete = '"claimedComplete": true' in claim_text
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
