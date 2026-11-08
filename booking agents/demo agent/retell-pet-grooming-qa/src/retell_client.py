"""Retell AI API client with explicit error handling."""
from __future__ import annotations

import time
from typing import Any

import httpx

from src.config import Settings


class RetellAPIError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class RetellClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base = settings.retell_api_base.rstrip("/")
        if not settings.retell_api_key:
            raise RetellAPIError("RETELL_API_KEY is not configured")
        self._headers = {
            "Authorization": f"Bearer {settings.retell_api_key}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base}{path}"
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.request(method, url, headers=self._headers, **kwargs)
        except httpx.HTTPError as exc:
            raise RetellAPIError(f"Retell transport error: {exc}") from exc
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise RetellAPIError(
                f"Retell API {method} {path} failed: HTTP {resp.status_code}",
                status_code=resp.status_code,
                body=body,
            )
        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    def get_agent(self, agent_id: str) -> dict[str, Any]:
        return self._request("GET", f"/get-agent/{agent_id}")

    def list_agents(self) -> Any:
        # Endpoint name historically varies; try common path
        try:
            return self._request("GET", "/list-agents")
        except RetellAPIError:
            return self._request("POST", "/list-agents", json={})

    def create_phone_call(
        self,
        *,
        from_number: str,
        to_number: str,
        override_agent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        retell_llm_dynamic_variables: dict[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "from_number": from_number,
            "to_number": to_number,
        }
        if override_agent_id:
            payload["override_agent_id"] = override_agent_id
        if metadata:
            payload["metadata"] = metadata
        if retell_llm_dynamic_variables:
            # Retell requires string values
            payload["retell_llm_dynamic_variables"] = {
                k: (v if isinstance(v, str) else str(v))
                for k, v in retell_llm_dynamic_variables.items()
            }
        if idempotency_key:
            payload["idempotency_key"] = idempotency_key
        return self._request("POST", "/v2/create-phone-call", json=payload)

    def create_web_call(
        self,
        *,
        agent_id: str,
        metadata: dict[str, Any] | None = None,
        retell_llm_dynamic_variables: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"agent_id": agent_id}
        if metadata:
            payload["metadata"] = metadata
        if retell_llm_dynamic_variables:
            payload["retell_llm_dynamic_variables"] = {
                k: (v if isinstance(v, str) else str(v))
                for k, v in retell_llm_dynamic_variables.items()
            }
        return self._request("POST", "/v2/create-web-call", json=payload)

    def get_call(self, call_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v2/get-call/{call_id}")

    def list_calls(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request("POST", "/v2/list-calls", json=payload or {})

    def wait_for_call_end(
        self,
        call_id: str,
        *,
        timeout_seconds: int,
        poll_interval: float = 5.0,
    ) -> dict[str, Any]:
        deadline = time.time() + timeout_seconds
        last: dict[str, Any] = {}
        while time.time() < deadline:
            last = self.get_call(call_id)
            status = (last.get("call_status") or "").lower()
            if status in {"ended", "error", "not_connected"}:
                return last
            time.sleep(poll_interval)
        raise RetellAPIError(f"Timed out waiting for call {call_id} to end", body=last)

    def extract_transcript(self, call: dict[str, Any]) -> list[dict[str, Any]]:
        for key in (
            "transcript_with_tool_calls",
            "scrubbed_post_session_transcript_with_tool_calls",
            "transcript_object",
        ):
            val = call.get(key)
            if isinstance(val, list) and val:
                return val
        transcript = call.get("transcript")
        if isinstance(transcript, str) and transcript.strip():
            return [{"role": "unknown", "content": transcript}]
        return []

    def extract_tool_calls(self, call: dict[str, Any]) -> list[dict[str, Any]]:
        tools = []
        for turn in self.extract_transcript(call):
            if not isinstance(turn, dict):
                continue
            name = turn.get("name") or turn.get("tool_name")
            role = (turn.get("role") or "").lower()
            if role in {"tool_call_invocation", "tool_call_result", "tool"} or name:
                tools.append(turn)
            # Nested tool calls
            for nested_key in ("tool_calls", "invocations"):
                nested = turn.get(nested_key)
                if isinstance(nested, list):
                    tools.extend([x for x in nested if isinstance(x, dict)])
        return tools
