from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from ledge_reference import (  # noqa: E402
    apply_authority_approval,
    load_authority_approval,
    load_proposed_transition,
    validate_new_accepted_state,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def scan_reality(root: Path) -> list[str]:
    source_root = root / "src"
    matches: list[str] = []

    for path in sorted(source_root.rglob("*")):
        if path.is_file() and "clerk" in path.read_text(encoding="utf-8").lower():
            matches.append(str(path.relative_to(root)))

    return matches


def main() -> None:
    # Load current accepted state.
    load_json(ROOT / ".ledge" / "states" / "current.json")

    # Load claims.
    claim = load_json(ROOT / ".ledge" / "claims" / "auth-uses-betterauth.json")

    # Load evidence.
    load_json(ROOT / ".ledge" / "evidence" / "source-scan.json")

    # Scan reality fixture and compare it with the accepted claim.
    clerk_references = scan_reality(ROOT)
    claim_text = claim["summary"]

    if claim_text == "Authentication uses BetterAuth." and clerk_references:
        print("Drift detected.")
        print()
        print("Claim:")
        print(claim_text)
        print()
        print("Reality:")
        print("Clerk references found in:")
        for reference in clerk_references:
            print(f"- {reference}")
        print()
        print("Proposed Patch:")
        print("Mark authentication migration as incomplete.")
        print("Add evidence references to remaining Clerk usage.")
        print()

        transition = load_proposed_transition(
            ROOT, "mark-auth-migration-incomplete.proposed.json"
        )
        print("Patch proposal found.")
        print(f"Transition status: {transition['status']}")
        print()

        approval = load_authority_approval(ROOT, "founder-approval.json")
        print("Human approval found.")

        accepted_transition = apply_authority_approval(ROOT, transition, approval)
        print(f"Transition status: {accepted_transition['status']}")

        accepted_state = validate_new_accepted_state(ROOT, accepted_transition)
        print("New accepted state created.")
        print(
            "Authentication migration complete: "
            f"{str(accepted_state.authentication_migration_complete).lower()}"
        )
    else:
        print("No drift detected.")


if __name__ == "__main__":
    main()
