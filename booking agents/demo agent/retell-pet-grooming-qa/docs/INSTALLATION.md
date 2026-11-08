# Installation

```bash
cd retell-pet-grooming-qa
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/setup.py
cp .env.example .env   # if setup did not already create it
```

Edit `.env` with local credentials. Never commit `.env`.
