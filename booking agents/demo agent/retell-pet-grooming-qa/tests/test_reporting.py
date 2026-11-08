import unittest
from pathlib import Path
import sys
import tempfile
import shutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import Settings
from src.report_generator import generate_reports
from src.scenario_loader import load_cases
from src.scoring import aggregate_run, compute_score


class ReportingTests(unittest.TestCase):
    def test_aggregate_and_reports(self):
        results = [
            {"test_id": "A01", "status": "PASS", "severity": "NONE", "dimension_scores": {"task_completion": 90}},
            {"test_id": "A02", "status": "FAIL", "severity": "P2", "dimension_scores": {"task_completion": 40}, "recommended_fix": "Fix greeting identity grounding."},
            {"test_id": "B01", "status": "BLOCKED", "severity": "NONE", "dimension_scores": {}},
        ]
        agg = aggregate_run(results)
        self.assertEqual(agg["counts"]["PASS"], 1)
        self.assertEqual(agg["counts"]["FAIL"], 1)
        score = compute_score({"task_completion": 80}, has_p0=True)
        self.assertEqual(score["production_readiness"], "NO-GO")

        tmp = Path(tempfile.mkdtemp())
        try:
            settings = Settings(
                qa_runs_dir=tmp,
                cases_path=ROOT / "tests" / "cases.json",
            )
            paths = generate_reports(settings, "run_test", results, load_cases()[:3])
            self.assertTrue(paths["executive_scorecard"].exists())
            self.assertTrue(paths["test_matrix"].exists())
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
