from __future__ import annotations

import ast
import operator
import re
from dataclasses import dataclass


OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


@dataclass(frozen=True)
class ToolResult:
    name: str
    content: str


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return float(OPS[type(node.op)](_eval(node.left), _eval(node.right)))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return float(OPS[type(node.op)](_eval(node.operand)))
    raise ValueError("Only numeric expressions are supported.")


class CalculatorTool:
    name = "calculator"
    description = "Evaluate safe arithmetic expressions."

    def run(self, query: str) -> ToolResult:
        expression = self._extract_expression(query)
        tree = ast.parse(expression, mode="eval")
        value = _eval(tree)
        display_value = int(value) if value.is_integer() else round(value, 6)
        return ToolResult(self.name, f"{expression} = {display_value}")

    @staticmethod
    def _extract_expression(query: str) -> str:
        normalized = (
            query.replace("\u52a0", "+")
            .replace("\u51cf", "-")
            .replace("\u4e58\u4ee5", "*")
            .replace("\u4e58", "*")
            .replace("\u9664\u4ee5", "/")
            .replace("\u9664", "/")
            .replace("\uff08", "(")
            .replace("\uff09", ")")
        )
        matches = re.findall(r"[0-9\.\+\-\*/%\(\)\s]+", normalized)
        expression = max((match.strip() for match in matches), key=len, default="")
        if not expression:
            raise ValueError("No arithmetic expression found.")
        return expression

