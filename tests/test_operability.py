from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ledge_reference import (
    apply_authority_approval,
    inspect_auth_migration,
    load_authority_approval,
    load_proposed_transition,
    validate_accepted_transition,
    validate_new_accepted_state,
    validate_proposed_transition,
)


class OperabilityTest(unittest.TestCase):
    def test_auth_migration_drift_is_detected(self) -> None:
        result = inspect_auth_migration(ROOT / "examples" / "auth-migration")

        self.assertTrue(result.drift)
        self.assertEqual(result.claim_id, "claim.auth.uses-betterauth")
        self.assertEqual(
            result.clerk_references,
            ("src/auth/provider.ts", "src/middleware.ts"),
        )

    def test_auth_migration_script_output(self) -> None:
        completed = subprocess.run(
            [sys.executable, "examples/auth-migration/run.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            completed.stdout,
            "\n".join(
                [
                    "Drift detected.",
                    "",
                    "Claim:",
                    "Authentication uses BetterAuth.",
                    "",
                    "Reality:",
                    "Clerk references found in:",
                    "- src/auth/provider.ts",
                    "- src/middleware.ts",
                    "",
                    "Proposed Patch:",
                    "Mark authentication migration as incomplete.",
                    "Add evidence references to remaining Clerk usage.",
                    "",
                    "Patch proposal found.",
                    "Transition status: proposed",
                    "",
                    "Human approval found.",
                    "Transition status: accepted",
                    "New accepted state created.",
                    "Authentication migration complete: false",
                    "",
                ]
            ),
        )

    def test_proposed_transition_is_not_accepted_without_approval(self) -> None:
        transition = load_proposed_transition(
            ROOT / "examples" / "auth-migration",
            "mark-auth-migration-incomplete.proposed.json",
        )

        with self.assertRaisesRegex(ValueError, "Transition is not accepted"):
            validate_accepted_transition(transition)

    def test_transition_with_approval_can_become_accepted(self) -> None:
        example_root = ROOT / "examples" / "auth-migration"
        transition = load_proposed_transition(
            example_root, "mark-auth-migration-incomplete.proposed.json"
        )
        approval = load_authority_approval(example_root, "founder-approval.json")

        accepted_transition = apply_authority_approval(
            example_root, transition, approval
        )

        self.assertEqual(accepted_transition["status"], "accepted")
        self.assertEqual(
            accepted_transition["approval"],
            "authority.approval.founder-auth-migration",
        )

    def test_new_state_marks_authentication_migration_incomplete(self) -> None:
        example_root = ROOT / "examples" / "auth-migration"
        transition = load_proposed_transition(
            example_root, "mark-auth-migration-incomplete.proposed.json"
        )
        approval = load_authority_approval(example_root, "founder-approval.json")
        accepted_transition = apply_authority_approval(
            example_root, transition, approval
        )

        result = validate_new_accepted_state(example_root, accepted_transition)

        self.assertFalse(result.authentication_migration_complete)

    def test_missing_approval_fails_validation(self) -> None:
        example_root = ROOT / "examples" / "auth-migration"
        transition = load_proposed_transition(
            example_root, "mark-auth-migration-incomplete.proposed.json"
        )
        approval = {
            "id": "authority.approval.missing",
            "transition": transition["id"],
            "decision": "missing",
        }

        with self.assertRaisesRegex(ValueError, "explicitly approve"):
            apply_authority_approval(example_root, transition, approval)

    def test_transition_must_reference_existing_patch(self) -> None:
        example_root = ROOT / "examples" / "auth-migration"
        transition = load_proposed_transition(
            example_root, "mark-auth-migration-incomplete.proposed.json"
        )
        invalid_transition = dict(transition)
        invalid_transition["patchPath"] = "patches/missing.patch"

        with self.assertRaisesRegex(ValueError, "existing patch"):
            validate_proposed_transition(example_root, invalid_transition)


if __name__ == "__main__":
    unittest.main()
