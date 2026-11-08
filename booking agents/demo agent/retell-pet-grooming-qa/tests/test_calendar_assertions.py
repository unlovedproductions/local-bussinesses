import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.integration_verifier import IntegrationVerifier
from adapters.provider_evidence import empty_blocked_evidence
from src.config import Settings


class CalendarAssertionTests(unittest.TestCase):
    def test_blocked_without_key(self):
        settings = Settings(calcom_api_key="")
        v = IntegrationVerifier(settings)
        out = v.verify(
            run_id="r",
            test_id="D01",
            receptionist_call_id=None,
            expected_outcome={},
            required_oracles=["calendar.create"],
            before_snapshot={"event_ids": []},
            after_snapshot={"event_ids": ["x"]},
        )
        self.assertEqual(out["status"], "BLOCKED")

    def test_empty_blocked_helper(self):
        ev = empty_blocked_evidence("nope")
        self.assertFalse(ev["verified"])
        self.assertEqual(ev["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
