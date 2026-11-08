import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import Settings
from src.qa_orchestrator import QAOrchestrator


class OrchestratorTests(unittest.TestCase):
    def test_blocked_without_credentials(self):
        settings = Settings(
            retell_api_key="",
            receptionist_agent_id="",
            max_calls=3,
            cases_path=ROOT / "tests" / "cases.json",
            business_config_path=ROOT / "config" / "business.example.json",
            qa_vars_path=ROOT / "config" / "qa_vars.example.json",
            test_settings_path=ROOT / "config" / "test_settings.example.json",
            qa_runs_dir=ROOT / "qa_runs",
        )
        orch = QAOrchestrator(settings)
        summary = orch.run(ids="A01", mode="readonly", max_calls=1)
        self.assertEqual(summary["results"][0]["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
