"""Streamlit QA dashboard — loads actual saved results only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import load_settings
from src.scoring import aggregate_run, interpret_score
from src.storage import latest_run_id, list_runs, load_run_results


st.set_page_config(page_title="Pet Grooming Voice QA", layout="wide")
settings = load_settings()

st.title("Retell Pet Grooming — Voice QA Auditor")
st.caption("Displays saved QA run artifacts only. No fabricated results.")

runs = list_runs(settings)
if not runs:
    st.warning("No QA runs found under qa_runs/. Execute smoke/QA scripts first.")
    st.stop()

run_names = [p.name for p in runs]
default = latest_run_id(settings)
idx = run_names.index(default) if default in run_names else 0
run_id = st.sidebar.selectbox("Run", run_names, index=idx)
results = load_run_results(settings, run_id)
agg = aggregate_run(results)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Overall QA score", agg["score"]["overall"] if agg["score"]["overall"] is not None else "n/a")
c2.metric("Pass rate %", agg["pass_rate"] if agg["pass_rate"] is not None else "n/a")
c3.metric("Executed", agg["executed"])
c4.metric("Readiness", agg["score"]["production_readiness"])

st.write("Interpretation:", interpret_score(agg["score"]["overall"]))
st.write("Counts:", agg["counts"])
st.write("Severities:", agg["severities"])

# Suite coverage
suite_stats = {}
for r in results:
    suite = (r.get("test_id") or "?")[0]
    suite_stats.setdefault(suite, {"PASS": 0, "FAIL": 0, "BLOCKED": 0, "OTHER": 0})
    stt = r.get("status") or "OTHER"
    if stt in suite_stats[suite]:
        suite_stats[suite][stt] += 1
    else:
        suite_stats[suite]["OTHER"] += 1
st.subheader("Suite performance")
st.json(suite_stats)

st.subheader("Filters")
status_f = st.multiselect("Status", sorted({r.get("status") for r in results if r.get("status")}))
sev_f = st.multiselect("Severity", sorted({r.get("severity") for r in results if r.get("severity")}))
qid = st.text_input("Test ID contains")

filtered = results
if status_f:
    filtered = [r for r in filtered if r.get("status") in status_f]
if sev_f:
    filtered = [r for r in filtered if r.get("severity") in sev_f]
if qid:
    filtered = [r for r in filtered if qid.upper() in str(r.get("test_id", "")).upper()]

st.subheader("Results")
for r in filtered:
    with st.expander(f"{r.get('test_id')} — {r.get('status')} — {r.get('severity')}"):
        st.write("Persona:", r.get("persona"))
        st.write("Expected:", r.get("expected_behavior"))
        st.write("Observed:", r.get("observed_behavior"))
        st.write("Call IDs:", r.get("call_ids"))
        st.write("Recommended fix:", r.get("recommended_fix"))
        st.write("Defects:")
        st.json(r.get("defects") or [])
        st.write("Verification:")
        st.json(r.get("verification") or {})
        st.write("Transcript:")
        st.json(r.get("transcript") or [])

# Reports if present
report_dir = settings.qa_runs_dir / run_id / "reports"
if report_dir.exists():
    st.subheader("Reports")
    for path in sorted(report_dir.glob("*.json")):
        with st.expander(path.name):
            st.json(json.loads(path.read_text()))

reg = report_dir / "regression_plan.json"
if reg.exists():
    st.subheader("Regression")
    st.json(json.loads(reg.read_text()))
