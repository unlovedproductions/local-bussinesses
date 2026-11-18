# Testing Guide

## Coordination

```bash
python3 coordination/scripts/test_coord.py
```

## Documentation checks

```bash
python3 scripts/documentation/check_docs.py
python3 scripts/documentation/test_check_docs.py
```

## QA unit tests

```bash
cd retell-pet-grooming-qa
source .venv/bin/activate
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate.py
python scripts/preflight.py --mode readonly
python scripts/run_smoke.py
```

Smoke may return **BLOCKED** without credentials — that is correct behavior.

Live Retell/Cal.com and sandbox writes require explicit approvals and env gates. See `retell-pet-grooming-qa/README.md`.
