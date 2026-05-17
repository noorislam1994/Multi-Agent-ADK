"""Tools shared by the School Agent ADK sub-agents."""

from __future__ import annotations

import ast
import operator
from typing import Any


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_math(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval_math(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_math(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left = _eval_math(node.left)
        right = _eval_math(node.right)
        return _OPS[type(node.op)](left, right)
    raise ValueError("Only numeric expressions using +, -, *, /, //, %, and ** are allowed.")


def calculator(expression: str) -> dict[str, Any]:
    """Safely calculate a numeric maths expression."""

    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_math(tree)
    except Exception as exc:
        return {
            "status": "error",
            "expression": expression,
            "error": str(exc),
        }

    return {
        "status": "success",
        "expression": expression,
        "result": int(result) if result.is_integer() else result,
    }


_KNOWLEDGE_BASE = {
    "english": (
        "English support covers grammar, comprehension, essay structure, summaries, "
        "creative writing, vocabulary, and literature analysis."
    ),
    "maths": (
        "Maths support covers arithmetic, algebra, geometry, trigonometry, statistics, "
        "calculus basics, and step-by-step problem solving."
    ),
    "science": (
        "Science support covers biology, chemistry, physics, experiments, variables, "
        "forces, energy, cells, ecosystems, atoms, and reactions."
    ),
    "history": (
        "History support covers timelines, causes and consequences, source analysis, "
        "civilizations, revolutions, empires, independence movements, and historical writing."
    ),
    "geography": (
        "Geography support covers maps, climate, landforms, population, development, "
        "natural hazards, ecosystems, and human-environment interaction."
    ),
    "computer_science": (
        "Computer Science support covers algorithms, programming, data structures, "
        "networks, databases, cybersecurity, and computational thinking."
    ),
}


def school_knowledge_search(topic: str) -> dict[str, str]:
    """Search a small built-in school knowledge base by subject or topic keyword."""

    query = topic.lower().replace(" ", "_")
    matches = {
        subject: note
        for subject, note in _KNOWLEDGE_BASE.items()
        if query in subject or any(part in note.lower() for part in topic.lower().split())
    }
    if not matches:
        matches = {"general": "No exact local note matched. Ask a subject teacher for a tailored answer."}
    return {"status": "success", "query": topic, "matches": matches}

