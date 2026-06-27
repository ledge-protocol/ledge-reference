import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
LF = chr(10)

from ledge_reference import (
    apply_authority_approval,
    collect_auth_migration_reproducibility_outputs,
    generate_agent_decision_from_context,
    generate_agent_context,
    inspect_auth_migration,
    load_agent_task,
    load_authority_approval,
    load_expected_reproducibility_outputs,
    load_proposed_transition,
    normalize_line_endings,
    run_auth_migration_reproducibility_check,
    stable_json_hash,
    stable_text_hash,
    validate_agent_context,
    validate_agent_decision,
    validate_accepted_transition,
    validate_new_accepted_state,
    validate_proposed_transition,
    write_agent_context,
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
        expected_hashes = load_expected_reproducibility_outputs(
            ROOT / "examples" / "auth-migration"
        )
        completed = subprocess.run(
            [sys.executable, "examples/auth-migration/run.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            completed.stdout,
            LF.join(
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
                    "Latest accepted state loaded.",
                    "Authentication migration complete: false",
                    "Agent context generated.",
                    "Agent guidance includes corrected assumptions.",
                    "Agent guidance warns against assuming migration completion.",
                    "",
                    "Agent context loaded.",
                    "Agent task loaded.",
                    "Agent task: Continue the authentication migration.",
                    "Agent recognized migration incomplete.",
                    "Agent avoided stale assumption.",
                    "Agent consulted evidence:",
                    "- examples/auth-migration/.ledge/evidence/source-scan.json",
                    "- src/auth/provider.ts",
                    "- src/middleware.ts",
                    "Agent decision generated.",
                    "Agent refused to mark migration complete without evidence.",
                    "",
                    "Reproducibility check started.",
                    f"Agent context hash: {expected_hashes['agentContext']}",
                    f"Agent decision hash: {expected_hashes['agentDecision']}",
                    f"Accepted state hash: {expected_hashes['acceptedState']}",
                    f"Drift result hash: {expected_hashes['driftResult']}",
                    "Reproducibility check passed.",
                    "",
                ]
            ),
        )

    def test_agent_context_can_be_generated_from_accepted_state(self) -> None:
        result = generate_agent_context(ROOT / "examples" / "auth-migration")

        self.assertEqual(result.state_id, "state.current.accepted")
        self.assertFalse(result.authentication_migration_complete)
        self.assertIn("# Agent Context", result.markdown)

    def test_agent_context_includes_human_intent(self) -> None:
        result = generate_agent_context(ROOT / "examples" / "auth-migration")

        self.assertIn("Replace Clerk with BetterAuth.", result.markdown)

    def test_agent_context_includes_accepted_knowledge(self) -> None:
        result = generate_agent_context(ROOT / "examples" / "auth-migration")

        self.assertIn("Authentication migration is not complete.", result.markdown)

    def test_agent_context_includes_evidence_paths(self) -> None:
        result = generate_agent_context(ROOT / "examples" / "auth-migration")

        self.assertEqual(
            result.evidence_paths,
            ("src/auth/provider.ts", "src/middleware.ts"),
        )
        self.assertIn("- src/auth/provider.ts", result.markdown)
        self.assertIn("- src/middleware.ts", result.markdown)

    def test_agent_context_includes_corrected_assumptions(self) -> None:
        result = generate_agent_context(ROOT / "examples" / "auth-migration")

        self.assertIn(
            "Do not assume authentication migration is complete.",
            result.markdown,
        )
        self.assertIn(
            "Do not assume all Clerk references have been removed.",
            result.markdown,
        )

    def test_agent_context_warns_migration_is_incomplete(self) -> None:
        result = generate_agent_context(ROOT / "examples" / "auth-migration")

        self.assertIn("Authentication migration is not complete.", result.markdown)
        self.assertIn(
            "Do not mark the migration complete without evidence.",
            result.markdown,
        )
        self.assertNotIn("Authentication migration is complete.", result.markdown)

    def test_agent_context_artifact_matches_generated_context(self) -> None:
        example_root = ROOT / "examples" / "auth-migration"
        write_agent_context(example_root)

        result = validate_agent_context(example_root)

        self.assertIn("## Agent Guidance", result.markdown)

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

    def test_agent_task_can_be_loaded(self) -> None:
        task = load_agent_task(
            ROOT / "examples" / "auth-migration",
            "continue-auth-migration.md",
        )

        self.assertEqual(task.summary, "Continue the authentication migration.")
        self.assertEqual(task.path, ".ledge/tasks/continue-auth-migration.md")

    def test_agent_decision_can_be_generated_from_context(self) -> None:
        result = generate_agent_decision_from_context(
            ROOT / "examples" / "auth-migration"
        )

        self.assertIn("# Agent Decision", result.markdown)
        self.assertEqual(result.task, "Continue the authentication migration.")

    def test_agent_decision_references_generated_context(self) -> None:
        result = generate_agent_decision_from_context(
            ROOT / "examples" / "auth-migration"
        )

        self.assertEqual(
            result.context_path,
            "examples/auth-migration/.ledge/context/agent-context.md",
        )
        self.assertIn(result.context_path, result.markdown)

    def test_agent_decision_includes_accepted_knowledge(self) -> None:
        result = generate_agent_decision_from_context(
            ROOT / "examples" / "auth-migration"
        )

        self.assertEqual(
            result.accepted_knowledge,
            "Authentication migration is not complete.",
        )
        self.assertIn(result.accepted_knowledge, result.markdown)

    def test_agent_decision_avoids_stale_assumptions(self) -> None:
        result = generate_agent_decision_from_context(
            ROOT / "examples" / "auth-migration"
        )

        self.assertIn(
            "Did not assume migration was complete.",
            result.stale_assumptions_avoided,
        )
        self.assertIn(
            "Did not assume all Clerk references were removed.",
            result.stale_assumptions_avoided,
        )
        self.assertIn("## Stale Assumptions Avoided", result.markdown)

    def test_agent_decision_references_evidence(self) -> None:
        result = generate_agent_decision_from_context(
            ROOT / "examples" / "auth-migration"
        )

        self.assertEqual(
            result.evidence_paths,
            (
                "examples/auth-migration/.ledge/evidence/source-scan.json",
                "src/auth/provider.ts",
                "src/middleware.ts",
            ),
        )
        self.assertIn("src/auth/provider.ts", result.markdown)
        self.assertIn("src/middleware.ts", result.markdown)

    def test_agent_decision_says_migration_is_incomplete(self) -> None:
        result = generate_agent_decision_from_context(
            ROOT / "examples" / "auth-migration"
        )

        self.assertIn("Authentication migration is not complete.", result.markdown)
        self.assertIn("Remaining Clerk references are present.", result.markdown)

    def test_agent_decision_does_not_mark_migration_complete(self) -> None:
        result = generate_agent_decision_from_context(
            ROOT / "examples" / "auth-migration"
        )

        self.assertIn("Do not mark migration complete.", result.markdown)
        self.assertNotIn("Authentication migration is complete.", result.markdown)

    def test_agent_decision_does_not_claim_clerk_references_are_removed(self) -> None:
        result = generate_agent_decision_from_context(
            ROOT / "examples" / "auth-migration"
        )

        self.assertNotIn("Clerk references are removed.", result.markdown)
        self.assertNotIn("Clerk references have been removed.", result.markdown)
        self.assertNotIn("no remaining Clerk references", result.reality_check)

    def test_agent_decision_artifact_matches_generated_decision(self) -> None:
        result = validate_agent_decision(ROOT / "examples" / "auth-migration")

        self.assertIn("## Decision", result.markdown)

    def test_missing_context_fails_agent_decision_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            example_copy = Path(temp_dir) / "auth-migration"
            shutil.copytree(ROOT / "examples" / "auth-migration", example_copy)
            (example_copy / ".ledge" / "context" / "agent-context.md").unlink()

            with self.assertRaisesRegex(ValueError, "context artifact is missing"):
                generate_agent_decision_from_context(example_copy)

    def test_missing_evidence_fails_agent_decision_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            example_copy = Path(temp_dir) / "auth-migration"
            shutil.copytree(ROOT / "examples" / "auth-migration", example_copy)
            (example_copy / ".ledge" / "evidence" / "source-scan.json").unlink()

            with self.assertRaisesRegex(FileNotFoundError, "source-scan.json"):
                generate_agent_decision_from_context(example_copy)

    def test_agent_context_hash_is_reproducible(self) -> None:
        example_root = ROOT / "examples" / "auth-migration"

        first = stable_text_hash(generate_agent_context(example_root).markdown)
        second = stable_text_hash(generate_agent_context(example_root).markdown)

        self.assertEqual(first, second)

    def test_agent_decision_hash_is_reproducible(self) -> None:
        example_root = ROOT / "examples" / "auth-migration"
        write_agent_context(example_root)

        first = stable_text_hash(
            generate_agent_decision_from_context(example_root).markdown
        )
        second = stable_text_hash(
            generate_agent_decision_from_context(example_root).markdown
        )

        self.assertEqual(first, second)

    def test_accepted_state_hash_is_reproducible(self) -> None:
        state_path = (
            ROOT
            / "examples"
            / "auth-migration"
            / ".ledge"
            / "states"
            / "after-transition.json"
        )
        first = stable_json_hash(json.loads(state_path.read_text(encoding="utf-8")))
        second = stable_json_hash(json.loads(state_path.read_text(encoding="utf-8")))

        self.assertEqual(first, second)

    def test_drift_result_hash_is_reproducible(self) -> None:
        example_root = ROOT / "examples" / "auth-migration"

        first = stable_json_hash(inspect_auth_migration(example_root))
        second = stable_json_hash(inspect_auth_migration(example_root))

        self.assertEqual(first, second)

    def test_json_hashing_is_key_order_independent(self) -> None:
        first = {"a": 1, "b": {"c": 2, "d": 3}}
        second = {"b": {"d": 3, "c": 2}, "a": 1}

        self.assertEqual(stable_json_hash(first), stable_json_hash(second))

    def test_line_ending_normalization_works(self) -> None:
        self.assertEqual(
            normalize_line_endings("one\r\ntwo\rthree\n"),
            "one\ntwo\nthree\n",
        )
        self.assertEqual(
            stable_text_hash("one\r\ntwo\rthree\n"),
            stable_text_hash("one\ntwo\nthree\n"),
        )

    def test_changing_evidence_changes_reproducibility_hash(self) -> None:
        example_root = ROOT / "examples" / "auth-migration"
        baseline = collect_auth_migration_reproducibility_outputs(example_root)

        with tempfile.TemporaryDirectory() as temp_dir:
            example_copy = Path(temp_dir) / "auth-migration"
            shutil.copytree(example_root, example_copy)
            evidence_path = example_copy / ".ledge" / "evidence" / "source-scan.json"
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["observations"] = evidence["observations"][:1]
            evidence_path.write_text(
                json.dumps(evidence, indent=2, sort_keys=True) + LF,
                encoding="utf-8",
            )

            changed = collect_auth_migration_reproducibility_outputs(example_copy)

        self.assertNotEqual(baseline["agentContext"], changed["agentContext"])
        self.assertNotEqual(baseline["agentDecision"], changed["agentDecision"])

    def test_repeated_runs_produce_identical_reproducibility_outputs(self) -> None:
        example_root = ROOT / "examples" / "auth-migration"

        first = collect_auth_migration_reproducibility_outputs(example_root)
        second = collect_auth_migration_reproducibility_outputs(example_root)

        self.assertEqual(first, second)

    def test_reproducibility_check_matches_manifest(self) -> None:
        example_root = ROOT / "examples" / "auth-migration"

        result = run_auth_migration_reproducibility_check(example_root)
        expected = load_expected_reproducibility_outputs(example_root)

        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
