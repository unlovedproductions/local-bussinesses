# Execution Playbook

1. Validate manifest: `python scripts/validate.py`
2. Unit tests: `python -m unittest discover -s tests -p "test_*.py"`
3. Preflight readonly: `python scripts/preflight.py --mode readonly`
4. Smoke: `python scripts/run_smoke.py` → A01, A02, A05
5. Inspect evidence under `qa_runs/<run_id>/`
6. Sandbox preflight: `python scripts/preflight.py --mode sandbox`
7. First calendar tests: D01, then D06, then D02 — only with sandbox approval
8. Broader suites with budgets
9. Reports: `python scripts/generate_report.py`
10. Dashboard: `streamlit run dashboard/app.py`
11. Regression: `python scripts/run_regression.py`
