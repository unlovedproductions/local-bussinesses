"""Calendar adapter interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CalendarSnapshot:
    provider: str
    calendar_id: str
    captured_at: str
    events: list[dict[str, Any]] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


class BaseCalendarAdapter(ABC):
    provider_name: str = "unknown"

    @abstractmethod
    def healthcheck(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def snapshot(self, *, calendar_id: str | None = None) -> CalendarSnapshot:
        raise NotImplementedError

    @abstractmethod
    def get_event(self, event_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    def list_events(self, **filters: Any) -> list[dict[str, Any]]:
        snap = self.snapshot()
        return snap.events
