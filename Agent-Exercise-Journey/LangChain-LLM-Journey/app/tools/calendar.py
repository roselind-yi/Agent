from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.tools.calculator import ToolResult


@dataclass
class CalendarEvent:
    id: str
    title: str
    starts_at: str
    ends_at: str
    location: str = "online"


@dataclass
class CalendarTool:
    name: str = "calendar"
    storage_path: Path = settings.calendar_path
    events: list[CalendarEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self.events = [CalendarEvent(**item) for item in payload.get("events", [])]
            return

        today = date.today()
        self.events = [
            CalendarEvent(
                id="demo-standup",
                title="Agent 项目复盘",
                starts_at=f"{today.isoformat()}T10:00:00",
                ends_at=f"{today.isoformat()}T10:30:00",
            ),
            CalendarEvent(
                id="demo-interview",
                title="产品经理面试模拟",
                starts_at=f"{(today + timedelta(days=1)).isoformat()}T15:00:00",
                ends_at=f"{(today + timedelta(days=1)).isoformat()}T16:00:00",
            ),
            CalendarEvent(
                id="demo-review",
                title="知识库答疑材料整理",
                starts_at=f"{(today + timedelta(days=2)).isoformat()}T09:30:00",
                ends_at=f"{(today + timedelta(days=2)).isoformat()}T10:15:00",
            ),
        ]
        self._save()

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"events": [event.__dict__ for event in self.events]}
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def run(self, query: str) -> ToolResult:
        lowered = query.lower()
        if any(word in lowered for word in ["create", "add"]) or any(word in query for word in ["安排", "创建", "新增"]):
            starts_at = self._extract_start_time(query)
            event = self.create_event("用户临时安排", starts_at, 45)
            return ToolResult(self.name, f"已创建日程：{event.title} {event.starts_at}-{event.ends_at}")

        target = self._resolve_target_date(query)
        events = [event for event in self.events if event.starts_at.startswith(target.isoformat())]
        if not events:
            return ToolResult(self.name, f"{target.isoformat()} 暂无日程。")
        lines = [f"{event.starts_at[11:16]} {event.title} ({event.location})" for event in events]
        return ToolResult(self.name, f"{target.isoformat()} 的日程：\n" + "\n".join(lines))

    def create_event(self, title: str, starts_at: datetime, duration_minutes: int = 30) -> CalendarEvent:
        event = CalendarEvent(
            id=str(uuid4()),
            title=title,
            starts_at=starts_at.replace(microsecond=0).isoformat(),
            ends_at=(starts_at + timedelta(minutes=duration_minutes)).replace(microsecond=0).isoformat(),
        )
        self.events.append(event)
        self._save()
        return event

    @staticmethod
    def _resolve_target_date(query: str) -> date:
        lowered = query.lower()
        today = date.today()
        if "后天" in query or "day after tomorrow" in lowered:
            return today + timedelta(days=2)
        if "明天" in query or "tomorrow" in lowered:
            return today + timedelta(days=1)
        return today

    @staticmethod
    def _extract_start_time(query: str) -> datetime:
        base_date = CalendarTool._resolve_target_date(query)
        hour = None
        minute = 0

        colon_match = re.search(r"(\d{1,2})[:：](\d{2})", query)
        if colon_match:
            hour = int(colon_match.group(1))
            minute = int(colon_match.group(2))
        else:
            hour_match = re.search(r"(\d{1,2})点", query)
            if hour_match:
                hour = int(hour_match.group(1))

        if hour is None:
            return datetime.now() + timedelta(hours=2)

        if any(token in query for token in ["下午", "晚上"]) and hour < 12:
            hour += 12
        if "中午" in query and hour == 12:
            minute = minute or 30

        return datetime.combine(base_date, datetime.min.time()).replace(hour=hour, minute=minute)

