from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from app.tools.calculator import ToolResult


WEATHER_FIXTURES = {
    "北京": "北京：晴，28°C，东北风 2 级，适合通勤。",
    "上海": "上海：多云，31°C，湿度偏高，建议带伞。",
    "杭州": "杭州：阵雨，29°C，下午降水概率较高。",
    "深圳": "深圳：雷阵雨，30°C，出门注意短时强降雨。",
    "广州": "广州：多云转雷阵雨，32°C，体感较热。",
    "成都": "成都：阴，26°C，空气湿润，适合步行。",
    "南京": "南京：晴间多云，33°C，注意防晒。",
    "武汉": "武汉：晴，34°C，高温时段建议减少户外活动。",
    "西安": "西安：多云，30°C，早晚温差较明显。",
    "重庆": "重庆：阵雨，31°C，山城道路注意湿滑。",
    "天津": "天津：晴，29°C，东南风 3 级。",
    "苏州": "苏州：小雨，27°C，建议携带雨具。",
}

WEATHER_CODE_MAP = {
    0: "晴朗",
    1: "多云",
    2: "多云转晴",
    3: "阴天",
    45: "雾",
    48: "结雾",
    51: "小毛雨",
    53: "中等毛雨",
    55: "大毛雨",
    56: "轻度冻毛雨",
    57: "强冻毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    66: "轻度冻雨",
    67: "强冻雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    77: "雪粒",
    80: "小阵雨",
    81: "中阵雨",
    82: "大阵雨",
    85: "小阵雪",
    86: "大阵雪",
    95: "雷阵雨",
    96: "雷阵雨伴冰雹",
    99: "强雷阵雨伴冰雹",
}


@dataclass(frozen=True)
class WeatherSnapshot:
    location: str
    temperature: float | None = None
    apparent_temperature: float | None = None
    humidity: int | None = None
    wind_speed: float | None = None
    weather_code: int | None = None
    is_day: int | None = None
    time: str | None = None


class WeatherTool:
    name = "weather"
    description = "Get real-time weather from Open-Meteo, with local fallback."

    def run(self, query: str) -> ToolResult:
        location = self._extract_location(query)
        try:
            snapshot = self._fetch_live_weather(location)
            return ToolResult(self.name, self._format_snapshot(snapshot))
        except Exception:
            return ToolResult(self.name, self._fallback(location))

    def _fetch_live_weather(self, location: str) -> WeatherSnapshot:
        match = self._geocode(location)
        if not match:
            raise ValueError(f"Location not found: {location}")
        lat = match["latitude"]
        lon = match["longitude"]
        resolved_name = self._render_location(match)
        url = (
            "https://api.open-meteo.com/v1/forecast?"
            + urllib.parse.urlencode(
                {
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code,is_day",
                    "timezone": "auto",
                    "temperature_unit": "celsius",
                    "wind_speed_unit": "kmh",
                    "precipitation_unit": "mm",
                    "forecast_days": 1,
                }
            )
        )
        with urllib.request.urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        current = payload.get("current") or {}
        return WeatherSnapshot(
            location=resolved_name,
            temperature=current.get("temperature_2m"),
            apparent_temperature=current.get("apparent_temperature"),
            humidity=current.get("relative_humidity_2m"),
            wind_speed=current.get("wind_speed_10m"),
            weather_code=current.get("weather_code"),
            is_day=current.get("is_day"),
            time=current.get("time"),
        )

    def _geocode(self, location: str) -> dict[str, Any] | None:
        url = (
            "https://geocoding-api.open-meteo.com/v1/search?"
            + urllib.parse.urlencode({"name": location, "count": 1, "language": "zh", "format": "json"})
        )
        with urllib.request.urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        results = payload.get("results") or []
        return results[0] if results else None

    @staticmethod
    def _render_location(match: dict[str, Any]) -> str:
        country = match.get("country") or ""
        admin1 = match.get("admin1") or ""
        name = match.get("name") or ""
        parts = [part for part in [name, admin1, country] if part]
        return "、".join(parts)

    @staticmethod
    def _extract_location(query: str) -> str:
        for city in WEATHER_FIXTURES:
            if city in query:
                return city
        cleaned = query
        for token in [
            "今天",
            "明天",
            "后天",
            "今天天气怎么样",
            "天气怎么样",
            "天气",
            "怎么样",
            "请问",
            "帮我",
            "看一下",
            "weather",
        ]:
            cleaned = cleaned.replace(token, "")
        cleaned = re.sub(r"[?？，,。!！\s]", "", cleaned)
        cleaned = cleaned.replace("'", "").replace("’", "")
        return cleaned or query.strip()

    def _format_snapshot(self, snapshot: WeatherSnapshot) -> str:
        desc = (
            WEATHER_CODE_MAP.get(snapshot.weather_code, f"天气码 {snapshot.weather_code}")
            if snapshot.weather_code is not None
            else "未知天气"
        )
        parts = [f"{snapshot.location}：{desc}"]
        if snapshot.temperature is not None:
            parts.append(f"温度 {snapshot.temperature:.1f}°C")
        if snapshot.apparent_temperature is not None:
            parts.append(f"体感 {snapshot.apparent_temperature:.1f}°C")
        if snapshot.humidity is not None:
            parts.append(f"湿度 {snapshot.humidity}%")
        if snapshot.wind_speed is not None:
            parts.append(f"风速 {snapshot.wind_speed:.1f}km/h")
        if snapshot.time:
            parts.append(f"更新 {snapshot.time}")
        return "、".join(parts)

    def _fallback(self, location: str) -> str:
        for city, report in WEATHER_FIXTURES.items():
            if city in location:
                return report
        supported = "、".join(WEATHER_FIXTURES)
        return f"未指定城市，演示数据支持：{supported}。"

