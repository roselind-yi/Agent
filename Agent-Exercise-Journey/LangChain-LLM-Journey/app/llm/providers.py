from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from app.core.config import Settings


TOOL_RESULT_LABEL = "\u5de5\u5177\u7ed3\u679c\uff1a"
KNOWLEDGE_LABEL = "\u77e5\u8bc6\u5e93\u4f9d\u636e\uff1a"
CONCLUSION_LABEL = "\u7ed3\u8bba\uff1a"
SCHEDULE_MARKER = "\u7684\u65e5\u7a0b\uff1a"


class LLMProvider(Protocol):
    def generate(self, system: str, user: str, context: str = "") -> str:
        ...


@dataclass
class MockLLMProvider:
    """Deterministic provider for offline demos and tests."""

    def generate(self, system: str, user: str, context: str = "") -> str:
        context = context.strip()
        if not context:
            return (
                f"\u6211\u7406\u89e3\u4f60\u7684\u95ee\u9898\u662f\uff1a{user.strip()}\u3002"
                "\u5f53\u524d\u6ca1\u6709\u68c0\u7d22\u5230\u989d\u5916\u8d44\u6599\uff0c"
                "\u6211\u4f1a\u6309\u901a\u7528\u52a9\u7406\u65b9\u5f0f\u7ed9\u51fa\u5efa\u8bae\u3002"
            )

        lines = [line.strip() for line in context.splitlines() if line.strip()]
        tool_lines: list[str] = []
        if SCHEDULE_MARKER in context:
            tool_lines.append(context.split("\n\n[", 1)[0].replace("\n", "\uff1b"))
        else:
            tool_lines = [
                line
                for line in lines
                if " = " in line
                or "\u00b0C" in line
                or line.startswith(("\u5df2\u521b\u5efa\u65e5\u7a0b", "\u6682\u65e0\u65e5\u7a0b"))
            ]
        doc_lines = [line for line in lines if line.startswith("[")]

        answer_parts: list[str] = []
        if tool_lines:
            answer_parts.append(TOOL_RESULT_LABEL + "\uff1b".join(tool_lines))
        if doc_lines:
            titles = [line.split("]", 1)[0].lstrip("[") for line in doc_lines[:3]]
            answer_parts.append(KNOWLEDGE_LABEL + "\u3001".join(titles))
            answer_parts.append(self._summarize_documents(doc_lines))
        return "\n".join(answer_parts)

    @staticmethod
    def _summarize_documents(doc_lines: list[str]) -> str:
        merged = " ".join(doc_lines)
        if "\u4ea7\u54c1\u8fb9\u754c" in merged or "\u4ea7\u54c1\u5b9a\u4f4d" in merged:
            return (
                CONCLUSION_LABEL
                + "\u9879\u76ee\u5b9a\u4f4d\u662f\u4e2a\u4eba\u667a\u80fd\u52a9\u7406\uff0c"
                "\u91cd\u70b9\u9a8c\u8bc1\u77e5\u8bc6\u5e93\u95ee\u7b54\u3001\u65e5\u7a0b\u7ba1\u7406"
                "\u548c\u751f\u6d3b\u67e5\u8be2\u7684\u95ed\u73af\u3002"
            )
        if "Prompt" in merged:
            return (
                CONCLUSION_LABEL
                + "\u4eae\u70b9\u662f\u628a Prompt \u62c6\u6210\u89d2\u8272\u3001\u89c4\u5212\u3001"
                "\u5de5\u5177\u9009\u62e9\u3001\u751f\u6210\u548c\u53cd\u601d\u5c42\uff0c\u4fbf\u4e8e\u6301\u7eed\u8fed\u4ee3\u3002"
            )
        if "RAG" in merged or "ChromaDB" in merged:
            return (
                CONCLUSION_LABEL
                + "RAG \u8d1f\u8d23\u628a\u79c1\u6709\u77e5\u8bc6\u53ec\u56de\u7ed9\u6a21\u578b\uff0c"
                "ChromaDB \u53ef\u4f5c\u4e3a\u751f\u4ea7\u5411\u91cf\u5e93\uff0c\u672c\u5730\u5b9e\u73b0"
                "\u4fdd\u8bc1\u53ef\u79bb\u7ebf\u6f14\u793a\u3002"
            )
        if "\u5de5\u5177" in merged:
            return (
                CONCLUSION_LABEL
                + "Agent \u901a\u8fc7\u5de5\u5177\u8def\u7531\u628a\u81ea\u7136\u8bed\u8a00"
                "\u8f6c\u4e3a\u8ba1\u7b97\u3001\u65e5\u7a0b\u3001\u5929\u6c14\u7b49\u53ef\u6267\u884c\u80fd\u529b\u3002"
            )
        return CONCLUSION_LABEL + "\u5df2\u6839\u636e\u77e5\u8bc6\u5e93\u6750\u6599\u7ec4\u7ec7\u56de\u7b54\uff0c\u5e76\u4fdd\u7559\u5f15\u7528\u65b9\u4fbf\u8ffd\u6eaf\u3002"


@dataclass
class OpenAICompatibleProvider:
    settings: Settings

    def generate(self, system: str, user: str, context: str = "") -> str:
        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI-compatible provider.")
        payload = {
            "model": self.settings.openai_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": f"{user}\n\nContext:\n{context}"},
            ],
            "temperature": 0.2,
        }
        request = urllib.request.Request(
            url=f"{self.settings.openai_base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]


@dataclass
class OllamaProvider:
    settings: Settings

    def generate(self, system: str, user: str, context: str = "") -> str:
        payload = {
            "model": self.settings.ollama_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": f"{user}\n\nContext:\n{context}"},
            ],
            "stream": False,
        }
        request = urllib.request.Request(
            url=f"{self.settings.ollama_base_url.rstrip('/')}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body.get("message", {}).get("content", "")


def build_llm(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider in {"openai", "openai-compatible"}:
        return OpenAICompatibleProvider(settings)
    if provider == "ollama":
        return OllamaProvider(settings)
    return MockLLMProvider()
