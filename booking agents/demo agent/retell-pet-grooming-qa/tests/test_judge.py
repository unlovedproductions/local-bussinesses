import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import Settings
from src.qa_judge import heuristic_judge, judge_scenario


class JudgeTests(unittest.TestCase):
    def test_heuristic_empty_transcript_blocked(self):
        scenario = {"id": "A01", "mode": "VOICE", "suite": "A", "expected_behavior": "greet"}
        result = heuristic_judge(scenario, transcript=[], verification=None, deterministic=[])
        self.assertEqual(result["status"], "BLOCKED")

    def test_backend_override(self):
        # Force heuristic path (no live LLM) while still applying backend FAIL override rules.
        settings = Settings(judge_provider="openai", openai_api_key="")
        scenario = {"id": "D01", "mode": "VOICE", "suite": "D", "expected_behavior": "book"}
        verification = {"status": "FAIL", "assertions": [{"name": "exactly_one_new_event", "passed": False, "detail": "created=[]"}]}
        det = [{"name": "exactly_one_new_event", "passed": False, "detail": "created=[]"}]
        result = judge_scenario(
            settings,
            scenario,
            business={},
            transcript=[{"role": "agent", "content": "Booked!"}],
            call_metadata={},
            verification=verification,
            deterministic=det,
        )
        self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
