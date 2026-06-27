from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ledge_reference import inspect_auth_migration


class OperabilityTest(unittest.TestCase):
    def test_auth_migration_drift_is_detected(self) -> None:
        result = inspect_auth_migration(ROOT / "examples" / "auth-migration")

        self.assertTrue(result.drift)
        self.assertEqual(result.claim_id, "claim.auth.uses-betterauth")
        self.assertEqual(result.clerk_references, ("app/auth.ts",))


if __name__ == "__main__":
    unittest.main()
