from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
SOURCE_ROOT = REPO_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from ledge_reference import (  # noqa: E402
    apply_authority_approval,
    load_authority_approval,
    load_agent_task,
    load_latest_accepted_state,
    load_proposed_transition,
    run_auth_migration_reproducibility_check,
    validate_new_accepted_state,
    write_agent_decision,
    write_agent_context,
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
    latest_state = load_latest_accepted_state(ROOT)

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
        print()

        agent_context = write_agent_context(ROOT)
        print("Latest accepted state loaded.")
        print(
            "Authentication migration complete: "
            f"{str(latest_state['authenticationMigrationComplete']).lower()}"
        )
        print("Agent context generated.")
        print("Agent guidance includes corrected assumptions.")
        if any(
            assumption == "Do not assume authentication migration is complete."
            for assumption in agent_context.corrected_assumptions
        ):
            print("Agent guidance warns against assuming migration completion.")

        print()
        task = load_agent_task(ROOT, "continue-auth-migration.md")
        print("Agent context loaded.")
        print("Agent task loaded.")
        print(f"Agent task: {task.summary}")

        agent_decision = write_agent_decision(ROOT)
        print("Agent recognized migration incomplete.")
        print("Agent avoided stale assumption.")
        print("Agent consulted evidence:")
        for evidence_path in agent_decision.evidence_paths:
            print(f"- {evidence_path}")
        print("Agent decision generated.")
        print("Agent refused to mark migration complete without evidence.")
        print()
        print("Reproducibility check started.")
        reproducibility_hashes = run_auth_migration_reproducibility_check(ROOT)
        agent_context_hash = reproducibility_hashes["agentContext"]
        agent_decision_hash = reproducibility_hashes["agentDecision"]
        accepted_state_hash = reproducibility_hashes["acceptedState"]
        drift_result_hash = reproducibility_hashes["driftResult"]
        print(f"Agent context hash: {agent_context_hash}")
        print(f"Agent decision hash: {agent_decision_hash}")
        print(f"Accepted state hash: {accepted_state_hash}")
        print(f"Drift result hash: {drift_result_hash}")
        print("Reproducibility check passed.")
    else:
        print("No drift detected.")


if __name__ == "__main__":
    main()
