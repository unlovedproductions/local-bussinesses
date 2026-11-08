import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.scenario_loader import load_cases, validate_cases, select_cases


class ManifestTests(unittest.TestCase):
    def test_count_and_unique(self):
        cases = load_cases()
        self.assertEqual(len(cases), 108)
        self.assertEqual(len({c["id"] for c in cases}), 108)
        self.assertEqual(validate_cases(cases), [])

    def test_suites_present(self):
        cases = load_cases()
        suites = {c["suite"] for c in cases}
        self.assertEqual(suites, set("ABCDEFGHIJ"))

    def test_select(self):
        cases = load_cases()
        selected = select_cases(cases, "A01,A02,A05")
        self.assertEqual([c["id"] for c in selected], ["A01", "A02", "A05"])


if __name__ == "__main__":
    unittest.main()
