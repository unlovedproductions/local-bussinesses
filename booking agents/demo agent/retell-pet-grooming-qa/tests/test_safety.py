import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import Settings
from src.safety import assess_scenario


class SafetyTests(unittest.TestCase):
    def test_sandbox_blocked_by_default(self):
        settings = Settings(
            retell_api_key="x",
            receptionist_agent_id="agent_x",
            receptionist_phone_number="+10000000000",
            qa_caller_agent_id="agent_y",
            qa_outbound_number="+10000000001",
            ack_target_number=True,
            allow_sandbox_writes=False,
            max_calls=3,
            retell_call_mode="phone",
        )
        scenario = {
            "id": "D01",
            "mode": "VOICE",
            "safety_level": "SANDBOX",
        }
        decision = assess_scenario(scenario, settings, run_mode="sandbox", call_count=0)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.status, "BLOCKED")

    def test_readonly_voice_requires_ack(self):
        settings = Settings(
            retell_api_key="x",
            receptionist_agent_id="agent_x",
            receptionist_phone_number="+10000000000",
            qa_caller_agent_id="agent_y",
            qa_outbound_number="+10000000001",
            ack_target_number=False,
            allow_sandbox_writes=False,
            max_calls=3,
            retell_call_mode="phone",
        )
        scenario = {"id": "A01", "mode": "VOICE", "safety_level": "READ_ONLY"}
        decision = assess_scenario(scenario, settings, run_mode="readonly", call_count=0)
        self.assertFalse(decision.allowed)

    def test_audio_blocked_without_adapter(self):
        settings = Settings(retell_api_key="x", test_adapter_url="", max_calls=3)
        scenario = {"id": "B01", "mode": "AUDIO", "safety_level": "READ_ONLY"}
        decision = assess_scenario(scenario, settings, run_mode="readonly", call_count=0)
        self.assertFalse(decision.allowed)


if __name__ == "__main__":
    unittest.main()
