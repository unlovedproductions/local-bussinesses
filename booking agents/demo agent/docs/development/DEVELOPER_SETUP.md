# Developer Setup

| Field | Value |
|---|---|
| Status | NEEDS_REVIEW |
| Last verified | 2026-11-18 |

## 1. Clone parent repository

```bash
git clone git@github.com-unloved:unlovedproductions/local-bussinesses.git
cd local-bussinesses/"booking agents/demo agent"
```

SSH host alias may differ on your machine; use the remote URL your keys allow for `unlovedproductions/local-bussinesses`.

## 2. Coordination CLI

```bash
python3 coordination/scripts/coord.py status
python3 coordination/scripts/coord.py register
```

No venv required (stdlib).

## 3. Voice demo

Follow [`../../voice-agent/README.md`](../../voice-agent/README.md): configure Retell agent prompt + Cal.com event. No local app server.

## 4. QA auditor

```bash
cd retell-pet-grooming-qa
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/setup.py
cp -n .env.example .env   # if needed
# edit .env — never commit
python scripts/validate.py
python -m unittest discover -s tests -p "test_*.py"
```

## 5. Documentation checks

```bash
cd ..   # workspace root
python3 scripts/documentation/check_docs.py
```

## Supported OS

Linux is the verified developer environment for this workspace. macOS/Windows: UNKNOWN (not tested here).
