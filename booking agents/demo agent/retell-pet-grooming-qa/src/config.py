"""Configuration loading with fail-closed defaults."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[1]


def _yes(val: str | None) -> bool:
    return (val or "").strip().upper() in {"YES", "TRUE", "1", "Y"}


class Settings(BaseModel):
    retell_api_key: str = ""
    retell_api_base: str = "https://api.retellai.com"
    receptionist_agent_id: str = ""
    receptionist_phone_number: str = ""
    qa_caller_agent_id: str = ""
    qa_outbound_number: str = ""
    retell_call_mode: str = "phone"

    openai_api_key: str = ""
    judge_provider: str = "ollama"  # ollama | openai
    ollama_base_url: str = "http://127.0.0.1:11434/v1"
    judge_model: str = "qwen2.5:14b-instruct-q5_K_M"

    max_calls: int = 3
    max_call_duration_seconds: int = 300
    max_run_spend_usd: float = 5.0
    allow_sandbox_writes: bool = False
    ack_target_number: bool = False
    sandbox_proof_path: Path = ROOT / "config" / "sandbox_proof.json"

    qa_assert_url: str = ""
    test_adapter_url: str = ""

    calcom_api_key: str = ""
    calcom_api_base: str = "https://api.cal.com/v2"
    calcom_api_version: str = "2024-08-13"
    calcom_event_type_id: str = ""
    calcom_sandbox_calendar_id: str = ""
    calcom_timezone: str = "America/Los_Angeles"

    business_config_path: Path = ROOT / "config" / "business.json"
    qa_vars_path: Path = ROOT / "config" / "qa_vars.json"
    test_settings_path: Path = ROOT / "config" / "test_settings.json"
    cases_path: Path = ROOT / "tests" / "cases.json"
    qa_runs_dir: Path = ROOT / "qa_runs"

    project_root: Path = ROOT


def load_settings(env_file: Path | None = None) -> Settings:
    # Prefer project .env over stale exported shell vars (e.g. old JUDGE_MODEL).
    load_dotenv(env_file or (ROOT / ".env"), override=True)
    return Settings(
        retell_api_key=os.getenv("RETELL_API_KEY", ""),
        retell_api_base=os.getenv("RETELL_API_BASE", "https://api.retellai.com"),
        receptionist_agent_id=os.getenv("RECEPTIONIST_AGENT_ID", ""),
        receptionist_phone_number=os.getenv("RECEPTIONIST_PHONE_NUMBER", ""),
        qa_caller_agent_id=os.getenv("QA_CALLER_AGENT_ID", ""),
        qa_outbound_number=os.getenv("QA_OUTBOUND_NUMBER", ""),
        retell_call_mode=os.getenv("RETELL_CALL_MODE", "phone").lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        judge_provider=os.getenv("JUDGE_PROVIDER", "ollama").strip().lower(),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1").rstrip("/"),
        judge_model=os.getenv("JUDGE_MODEL", "qwen2.5:14b-instruct-q5_K_M"),
        max_calls=int(os.getenv("MAX_CALLS", "3")),
        max_call_duration_seconds=int(os.getenv("MAX_CALL_DURATION_SECONDS", "300")),
        max_run_spend_usd=float(os.getenv("MAX_RUN_SPEND_USD", "5")),
        allow_sandbox_writes=_yes(os.getenv("ALLOW_SANDBOX_WRITES", "NO")),
        ack_target_number=_yes(os.getenv("ACK_TARGET_NUMBER", "NO")),
        sandbox_proof_path=Path(os.getenv("SANDBOX_PROOF_PATH", str(ROOT / "config" / "sandbox_proof.json"))),
        qa_assert_url=os.getenv("QA_ASSERT_URL", ""),
        test_adapter_url=os.getenv("TEST_ADAPTER_URL", ""),
        calcom_api_key=os.getenv("CALCOM_API_KEY", ""),
        calcom_api_base=os.getenv("CALCOM_API_BASE", "https://api.cal.com/v2"),
        calcom_api_version=os.getenv("CALCOM_API_VERSION", "2024-08-13"),
        calcom_event_type_id=os.getenv("CALCOM_EVENT_TYPE_ID", ""),
        calcom_sandbox_calendar_id=os.getenv("CALCOM_SANDBOX_CALENDAR_ID", ""),
        calcom_timezone=os.getenv("CALCOM_TIMEZONE", "America/Los_Angeles"),
        business_config_path=Path(os.getenv("BUSINESS_CONFIG_PATH", str(ROOT / "config" / "business.json"))),
        qa_vars_path=Path(os.getenv("QA_VARS_PATH", str(ROOT / "config" / "qa_vars.json"))),
        test_settings_path=Path(os.getenv("TEST_SETTINGS_PATH", str(ROOT / "config" / "test_settings.json"))),
        cases_path=Path(os.getenv("CASES_PATH", str(ROOT / "tests" / "cases.json"))),
        qa_runs_dir=Path(os.getenv("QA_RUNS_DIR", str(ROOT / "qa_runs"))),
    )


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        example = path.with_name(path.name.replace(".json", ".example.json"))
        if example.exists() and path.name.endswith(".json") and ".example" not in path.name:
            # Prefer explicit example when local config missing
            alt = path.parent / (path.stem + ".example.json")
            if alt.exists():
                return json.loads(alt.read_text())
        raise FileNotFoundError(f"Missing config: {path}")
    return json.loads(path.read_text())


def load_business(settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or load_settings()
    path = settings.business_config_path
    if not path.exists():
        path = ROOT / "config" / "business.example.json"
    return load_json(path)


def load_qa_vars(settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or load_settings()
    path = settings.qa_vars_path
    if not path.exists():
        path = ROOT / "config" / "qa_vars.example.json"
    return load_json(path)


def load_test_settings(settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or load_settings()
    path = settings.test_settings_path
    if not path.exists():
        path = ROOT / "config" / "test_settings.example.json"
    return load_json(path)


def load_sandbox_proof(settings: Settings | None = None) -> dict[str, Any] | None:
    settings = settings or load_settings()
    path = settings.sandbox_proof_path
    if not path.exists():
        example = ROOT / "config" / "sandbox_proof.example.json"
        if example.exists():
            return json.loads(example.read_text())
        return None
    return json.loads(path.read_text())
