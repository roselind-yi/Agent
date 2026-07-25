from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.agent.engine import JourneyAgent  # noqa: E402
from app.rag.vector_store import LocalVectorStore  # noqa: E402
from app.tools.calculator import CalculatorTool  # noqa: E402


class AgentTestCase(unittest.TestCase):
    def test_calculator_tool(self) -> None:
        result = CalculatorTool().run("帮我算一下 (128 + 32) / 4")
        self.assertEqual(result.content, "(128 + 32) / 4 = 40")

    def test_rag_search_finds_product_doc(self) -> None:
        store = LocalVectorStore.from_json(ROOT / "data" / "knowledge.json")
        hits = store.search("Agent 产品定位")
        self.assertTrue(hits)
        self.assertEqual(hits[0].document.id, "product-positioning")

    def test_agent_uses_weather_tool(self) -> None:
        response = JourneyAgent().answer("上海今天天气怎么样？")
        self.assertIn("weather", response.used_tools)
        self.assertIn("上海", response.answer)

    def test_agent_returns_trace(self) -> None:
        response = JourneyAgent().answer("结合 RAG 和工具调用说明项目亮点")
        self.assertGreaterEqual(len(response.trace), 3)
        self.assertTrue(response.citations)


if __name__ == "__main__":
    unittest.main()

