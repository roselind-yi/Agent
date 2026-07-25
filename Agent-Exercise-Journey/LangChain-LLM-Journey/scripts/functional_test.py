from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs" / "functional_test_report.md"
BASE_URL = os.environ.get("JOURNEY_AGENT_BASE_URL", "http://127.0.0.1:8766").rstrip("/")


@dataclass
class CaseResult:
    name: str
    ok: bool
    detail: str


def request_json(method: str, path: str, payload: dict | None = None) -> tuple[int, dict | str]:
    url = f"{BASE_URL}{path}"
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = Request(url, data=data, method=method, headers=headers)
    with urlopen(request, timeout=20) as response:
        body = response.read().decode("utf-8")
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.status, json.loads(body)
        return response.status, body


def run_case(name: str, func) -> CaseResult:
    try:
        ok, detail = func()
        return CaseResult(name, ok, detail)
    except (HTTPError, URLError, AssertionError, ValueError, subprocess.CalledProcessError) as exc:
        return CaseResult(name, False, f"{type(exc).__name__}: {exc}")


def main() -> int:
    cases: list[CaseResult] = []

    def add(name: str, func) -> None:
        cases.append(run_case(name, func))

    add("Health endpoint", _check_health)
    add("Web demo page", _check_web_page)
    add("API discovery", _check_api)
    add("Knowledge search", _check_search)

    weather_cases = ["北京", "上海", "杭州", "深圳", "广州", "成都", "武汉", "西安", "重庆", "苏州"]
    for city in weather_cases:
        add(f"Weather {city}", lambda city=city: _check_weather(city))

    add("Calculator one", lambda: _check_chat("帮我算一下 (128 + 32) / 4", ["calculator"], ["(128 + 32) / 4 = 40"]))
    add("Calculator two", lambda: _check_chat("请计算 18 * 7 - 4", ["calculator"], ["18 * 7 - 4 = 122"]))
    add("Calendar today", lambda: _check_chat("我今天有什么日程？", ["calendar"], ["日程"]))
    add("Calendar tomorrow", lambda: _check_chat("明天有什么日程？", ["calendar"], ["日程"]))
    add("Calendar day after tomorrow", lambda: _check_chat("后天有什么日程？", ["calendar"], ["日程"]))
    add("Calendar create event", _check_create_event)
    add("Knowledge product", lambda: _check_chat("这个 Agent 项目的产品定位是什么？", [], ["知识库依据", "个人智能助理"], require_citations=True))
    add("Knowledge prompt", lambda: _check_chat("Prompt 分层是怎么设计的？", [], ["Prompt", "知识库依据"], require_citations=True))
    add("Knowledge rag", lambda: _check_chat("RAG 在这个项目里怎么用？", [], ["RAG", "知识库依据"], require_citations=True))
    add("Knowledge competitor", lambda: _check_chat("竞品分析结论是什么？", [], ["竞品", "知识库依据"], require_citations=True))
    add("Multi tool", lambda: _check_chat("明天上海天气怎么样，我的日程安排是什么？", ["weather", "calendar"], ["上海", "日程"]))
    add("General chat", lambda: _check_chat("你喜欢什么颜色？", [], ["我理解你的问题是"], require_general_chat=True))
    add("Java client", _check_java_client)

    passed = sum(1 for case in cases if case.ok)
    failed = len(cases) - passed
    report = render_report(cases, passed, failed)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)
    return 0 if failed == 0 else 1


def _check_health() -> tuple[bool, str]:
    status, payload = request_json("GET", "/health")
    ok = status == 200 and isinstance(payload, dict) and payload.get("status") == "ok"
    return ok, f"status={status}, payload={payload}"


def _check_web_page() -> tuple[bool, str]:
    status, body = request_json("GET", "/chat")
    ok = status == 200 and isinstance(body, str) and "Journey Personal Agent" in body
    return ok, f"status={status}, has_page={ok}"


def _check_api() -> tuple[bool, str]:
    status, payload = request_json("GET", "/api")
    ok = status == 200 and isinstance(payload, dict) and "POST /chat - agent chat API" in payload.get("endpoints", [])
    return ok, f"status={status}, payload={payload}"


def _check_search() -> tuple[bool, str]:
    status, payload = request_json("GET", "/knowledge/search?" + urlencode({"q": "Agent 产品定位", "top_k": 3}))
    hits = payload.get("hits", []) if isinstance(payload, dict) else []
    ok = status == 200 and any(hit.get("id") == "product-positioning" for hit in hits)
    return ok, f"status={status}, top_hit={hits[0]['id'] if hits else 'none'}"


def _check_weather(city: str) -> tuple[bool, str]:
    data = _chat_json(f"{city}今天天气怎么样？")
    ok = "weather" in data.get("used_tools", []) and city in data.get("answer", "")
    return ok, f"city={city}, answer={data.get('answer')}"


def _check_chat(
    message: str,
    expected_tools: list[str],
    expected_contains: list[str],
    require_citations: bool = False,
    require_general_chat: bool = False,
) -> tuple[bool, str]:
    data = _chat_json(message)
    tools = data.get("used_tools", [])
    citations = data.get("citations", [])
    answer = data.get("answer", "")
    if expected_tools and not all(tool in tools for tool in expected_tools):
        return False, f"tools={tools}, expected={expected_tools}"
    if require_citations and not citations:
        return False, "citations missing"
    if require_general_chat and data.get("intent") != "general_chat":
        return False, f"intent={data.get('intent')}, answer={answer}"
    if expected_contains and not all(token in answer for token in expected_contains):
        return False, f"answer={answer}"
    return True, f"intent={data.get('intent')}, tools={tools}, citations={len(citations)}"


def _check_create_event() -> tuple[bool, str]:
    before_status, before_payload = request_json("GET", "/calendar/events")
    before_count = len(before_payload.get("events", [])) if isinstance(before_payload, dict) else 0
    data = _chat_json("帮我新增一个下午三点的会议")
    after_status, after_payload = request_json("GET", "/calendar/events")
    after_count = len(after_payload.get("events", [])) if isinstance(after_payload, dict) else 0
    ok = (
        before_status == 200
        and after_status == 200
        and "calendar" in data.get("used_tools", [])
        and after_count == before_count + 1
    )
    return ok, f"before={before_count}, after={after_count}, answer={data.get('answer')}"


def _check_java_client() -> tuple[bool, str]:
    java_dir = ROOT / "java-client"
    src = java_dir / "src" / "main" / "java" / "com" / "journey" / "client" / "JourneyAgentClient.java"
    subprocess.run(["javac", "-encoding", "UTF-8", "-d", "out", str(src)], cwd=java_dir, check=True)
    env = os.environ.copy()
    env["JOURNEY_AGENT_BASE_URL"] = BASE_URL
    result = subprocess.run(
        ["java", "-cp", "out", "com.journey.client.JourneyAgentClient", "上海今天天气怎么样？"],
        cwd=java_dir,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    output = result.stdout.strip()
    ok = '"weather"' in output and "上海" in output
    return ok, output


def _chat_json(message: str) -> dict:
    _, payload = request_json("POST", "/chat", {"message": message, "user_id": "functional-test"})
    if not isinstance(payload, dict):
        raise ValueError("Expected JSON payload from /chat")
    return payload


def render_report(cases: list[CaseResult], passed: int, failed: int) -> str:
    lines = [
        "# Functional Test Report",
        "",
        f"- Base URL: `{BASE_URL}`",
        f"- Timestamp: {datetime.now().isoformat(timespec='seconds')}",
        f"- Total cases: {len(cases)}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
        "",
        "## Results",
    ]
    for case in cases:
        status = "PASS" if case.ok else "FAIL"
        lines.append(f"- [{status}] {case.name}: {case.detail}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

