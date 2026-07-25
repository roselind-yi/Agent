from __future__ import annotations

from dataclasses import dataclass, field

from app.core.config import Settings, settings
from app.core.schemas import AgentResponse, TraceStep
from app.llm.providers import LLMProvider, build_llm
from app.rag.vector_store import LocalVectorStore
from app.tools.calculator import CalculatorTool
from app.tools.calendar import CalendarTool
from app.tools.weather import WeatherTool


SYSTEM_PROMPT = (
    "\u4f60\u662f\u4e00\u4e2a\u9762\u5411\u4e2a\u4eba\u7528\u6237\u7684\u667a\u80fd\u52a9\u7406 Agent\u3002"
    "\u4f60\u9700\u8981\u5148\u5224\u65ad\u610f\u56fe\uff0c\u518d\u51b3\u5b9a\u662f\u5426\u68c0\u7d22"
    "\u77e5\u8bc6\u5e93\u6216\u8c03\u7528\u5de5\u5177\uff0c\u6700\u540e\u7ed9\u51fa\u7b80\u6d01\u3001"
    "\u53ef\u4fe1\u3001\u53ef\u6267\u884c\u7684\u4e2d\u6587\u56de\u7b54\u3002"
)


@dataclass
class JourneyAgent:
    settings: Settings = settings
    llm: LLMProvider = field(default_factory=lambda: build_llm(settings))
    retriever: LocalVectorStore = field(init=False)
    calculator: CalculatorTool = field(default_factory=CalculatorTool)
    calendar: CalendarTool = field(default_factory=CalendarTool)
    weather: WeatherTool = field(default_factory=WeatherTool)

    def __post_init__(self) -> None:
        self.retriever = LocalVectorStore.from_json(self.settings.knowledge_path)

    def answer(self, message: str, user_id: str = "demo-user") -> AgentResponse:
        intent = self._classify(message)
        trace: list[TraceStep] = [TraceStep("classify_intent", message, intent)]
        used_tools: list[str] = []
        citations: list[dict[str, object]] = []
        context_parts: list[str] = []

        if intent in {"calculator", "multi_tool"} and self._looks_like_math(message):
            result = self.calculator.run(message)
            used_tools.append(result.name)
            context_parts.append(result.content)
            trace.append(TraceStep(result.name, message, result.content))

        if intent in {"calendar", "multi_tool"} and self._looks_like_calendar(message):
            result = self.calendar.run(message)
            used_tools.append(result.name)
            context_parts.append(result.content)
            trace.append(TraceStep(result.name, message, result.content))

        if intent in {"weather", "multi_tool"} and self._looks_like_weather(message):
            result = self.weather.run(message)
            used_tools.append(result.name)
            context_parts.append(result.content)
            trace.append(TraceStep(result.name, message, result.content))

        should_retrieve = intent == "knowledge" or self._looks_like_knowledge(message)
        if should_retrieve:
            hits = self.retriever.search(message, top_k=3)
            if hits:
                retrieved = "\n".join(f"[{hit.document.title}] {hit.document.content}" for hit in hits)
                context_parts.append(retrieved)
                citations = [
                    {
                        "id": hit.document.id,
                        "title": hit.document.title,
                        "score": round(hit.score, 4),
                        "tags": hit.document.tags,
                    }
                    for hit in hits
                ]
                trace.append(TraceStep("rag_retrieval", message, f"retrieved {len(hits)} documents"))

        if not used_tools and not citations and intent == "general_chat":
            intent = "general_chat"

        context = "\n\n".join(context_parts)
        answer = self._compose_answer(message, intent, context)
        trace.append(TraceStep("generate_answer", context[:200], answer[:240]))
        return AgentResponse(
            answer=answer,
            intent=intent,
            used_tools=used_tools,
            citations=citations,
            trace=trace,
        )

    def _compose_answer(self, message: str, intent: str, context: str) -> str:
        if context:
            generated = self.llm.generate(SYSTEM_PROMPT, message, context)
            return f"{generated}\n\n\u672c\u6b21\u8bc6\u522b\u610f\u56fe\uff1a{intent}\u3002"
        return self.llm.generate(SYSTEM_PROMPT, message)

    def _classify(self, message: str) -> str:
        signals = {
            "calculator": self._looks_like_math(message),
            "calendar": self._looks_like_calendar(message),
            "weather": self._looks_like_weather(message),
            "knowledge": self._looks_like_knowledge(message),
        }
        positive = [name for name, matched in signals.items() if matched]
        if len(positive) > 1:
            return "multi_tool"
        return positive[0] if positive else "general_chat"

    @staticmethod
    def _looks_like_math(message: str) -> bool:
        lowered = message.lower()
        has_operator = any(symbol in message for symbol in ["+", "-", "*", "/", "\u4e58", "\u9664", "\u52a0", "\u51cf"])
        has_digit = any(char.isdigit() for char in message)
        return (has_operator and has_digit) or any(word in lowered for word in ["calculate", "calculator"])

    @staticmethod
    def _looks_like_calendar(message: str) -> bool:
        lowered = message.lower()
        return any(word in lowered for word in ["calendar", "schedule", "meeting"]) or any(
            word in message for word in ["\u65e5\u7a0b", "\u4f1a\u8bae", "\u5b89\u6392", "\u65e5\u5386"]
        )

    @staticmethod
    def _looks_like_weather(message: str) -> bool:
        lowered = message.lower()
        return "weather" in lowered or "\u5929\u6c14" in message

    @staticmethod
    def _looks_like_knowledge(message: str) -> bool:
        return any(
            word in message
            for word in ["\u77e5\u8bc6\u5e93", "RAG", "Agent", "Prompt", "\u4ea7\u54c1", "\u7ade\u54c1", "LangChain"]
        )
