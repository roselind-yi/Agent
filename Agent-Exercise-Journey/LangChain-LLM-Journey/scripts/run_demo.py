from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.agent.engine import JourneyAgent  # noqa: E402


def main() -> None:
    agent = JourneyAgent()
    questions = [
        "这个 Agent 项目的产品定位是什么？",
        "帮我算一下 (128 + 32) / 4",
        "明天有什么日程？",
        "上海今天天气怎么样？",
        "结合 RAG 和工具调用，说明你的项目亮点。",
    ]
    for question in questions:
        response = agent.answer(question)
        print("=" * 80)
        print("Q:", question)
        print("Intent:", response.intent)
        print("Tools:", ", ".join(response.used_tools) or "none")
        print(response.answer)


if __name__ == "__main__":
    main()

