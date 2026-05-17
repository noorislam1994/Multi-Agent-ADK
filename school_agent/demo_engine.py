"""Runtime engine for the lightweight browser demo.

The official ADK entry point is ``school_agent.agent:root_agent``. This module
keeps the custom UI dependency-free by using the Gemini REST API directly while
mirroring the same coordinator, subject routing, memory, and tools.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .tools import calculator, school_knowledge_search


SUBJECTS = {
    "english": {
        "agent": "English Teacher Agent",
        "keywords": ["english", "grammar", "essay", "poem", "poetry", "novel", "story", "literature", "summary", "comprehension", "vocabulary"],
        "style": "Focus on language, structure, examples, and writing improvement.",
    },
    "maths": {
        "agent": "Maths Teacher Agent",
        "keywords": ["math", "maths", "algebra", "geometry", "calculate", "equation", "fraction", "percentage", "probability", "statistics", "trigonometry", "calculus"],
        "style": "Solve step by step and show working clearly.",
    },
    "science": {
        "agent": "Science Teacher Agent",
        "keywords": ["science", "biology", "chemistry", "physics", "experiment", "cell", "force", "energy", "atom", "reaction", "ecosystem", "photosynthesis"],
        "style": "Explain concepts with school-level accuracy and examples.",
    },
    "history": {
        "agent": "History Teacher Agent",
        "keywords": ["history", "war", "civilization", "empire", "revolution", "ancient", "timeline", "source", "independence", "colonial", "medieval"],
        "style": "Explain causes, events, consequences, and useful timelines.",
    },
    "geography": {
        "agent": "Geography Teacher Agent",
        "keywords": ["geography", "climate", "map", "river", "earthquake", "volcano", "population", "migration", "erosion", "weather", "plate"],
        "style": "Connect physical and human geography with case-study thinking.",
    },
    "computer_science": {
        "agent": "Computer Science Teacher Agent",
        "keywords": ["computer", "program", "python", "algorithm", "code", "database", "network", "cyber", "binary", "data structure", "javascript"],
        "style": "Use clear computational thinking and concise examples.",
    },
}


MEMORY_FILE = Path("school_memory.json")


@dataclass
class ChatMemory:
    messages: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def load(cls) -> "ChatMemory":
        if not MEMORY_FILE.exists():
            return cls()
        try:
            data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()
        return cls(messages=data.get("messages", [])[-40:])

    def save(self) -> None:
        MEMORY_FILE.write_text(json.dumps({"messages": self.messages[-80:]}, indent=2), encoding="utf-8")

    def add(self, role: str, content: str, **metadata: Any) -> None:
        self.messages.append(
            {
                "role": role,
                "content": content,
                "timestamp": int(time.time()),
                **metadata,
            }
        )
        self.save()

    def recent_context(self) -> str:
        recent = self.messages[-8:]
        return "\n".join(f"{item['role']}: {item['content']}" for item in recent)


def route_subject(message: str) -> tuple[str, dict[str, Any]]:
    text = message.lower()
    scores: dict[str, int] = {}
    for subject, config in SUBJECTS.items():
        scores[subject] = sum(1 for keyword in config["keywords"] if keyword in text)

    subject = max(scores, key=scores.get)
    if scores[subject] == 0:
        subject = "english" if len(message.split()) > 16 else "science"
    return subject, SUBJECTS[subject]


def maybe_calculate(message: str) -> dict[str, Any] | None:
    if not re.search(r"\d", message):
        return None
    if not re.search(r"[+\-*/%]|\bcalculate\b|\bsolve\b|\bwhat is\b", message.lower()):
        return None

    expression = message
    expression = re.sub(r"(?i)(calculate|solve|what is|find|please|=|\?)", " ", expression)
    expression = re.sub(r"[^0-9+\-*/().% ]", " ", expression).replace("%", "/100")
    expression = re.sub(r"\s+", " ", expression).strip()
    if not expression:
        return None
    return calculator(expression)


def _gemini_generate(prompt: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    model = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.5-flash")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.35, "maxOutputTokens": 900},
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        data = json.loads(response.read().decode("utf-8"))

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini returned no candidate response.")
    parts = candidates[0].get("content", {}).get("parts", [])
    return "\n".join(part.get("text", "") for part in parts).strip()


def _offline_response(subject: str, config: dict[str, Any], message: str, tool_result: dict[str, Any] | None) -> str:
    lines = [
        f"{config['agent']} received this through the School Coordinator.",
        "",
    ]
    if tool_result and tool_result.get("status") == "success":
        lines.append(f"Calculator result: {tool_result['expression']} = {tool_result['result']}")
        lines.append("")
    lines.extend(
        [
            "I can answer fully once `GOOGLE_API_KEY` is set. For now, here is a structured classroom response:",
            f"Subject: {subject.replace('_', ' ').title()}",
            f"Question: {message}",
            "Approach: identify the key idea, explain it in simple steps, then finish with a short example or check.",
        ]
    )
    return "\n".join(lines)


def answer_student(message: str) -> dict[str, Any]:
    memory = ChatMemory.load()
    subject, config = route_subject(message)
    tool_result = maybe_calculate(message) if subject == "maths" else None
    knowledge = school_knowledge_search(subject)

    prompt = f"""
You are running a School Multi-Agent System built for a GDG AI Dev Camp assignment.
Root Agent: School Coordinator.
Selected Sub-Agent: {config['agent']}.
Subject routing reason: the question matched {subject}.
Teacher style: {config['style']}

Recent memory:
{memory.recent_context() or 'No previous messages.'}

Tool results:
Calculator: {json.dumps(tool_result) if tool_result else 'not used'}
Knowledge search: {json.dumps(knowledge)}

Student question:
{message}

Answer as the selected teacher agent. Keep it helpful, structured, and student-friendly.
If the answer includes calculation, show the steps and final answer.
"""

    used_model = bool(os.getenv("GOOGLE_API_KEY"))
    try:
        response = _gemini_generate(prompt) if used_model else _offline_response(subject, config, message, tool_result)
    except (RuntimeError, urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        used_model = False
        response = _offline_response(subject, config, message, tool_result)
        response += f"\n\nRuntime note: Gemini call was not completed ({exc})."

    memory.add("student", message, subject=subject)
    memory.add("assistant", response, subject=subject, agent=config["agent"])

    return {
        "agent": config["agent"],
        "subject": subject,
        "response": response,
        "usedModel": used_model,
        "toolResult": tool_result,
        "memoryCount": len(memory.messages),
    }


def memory_snapshot() -> dict[str, Any]:
    memory = ChatMemory.load()
    return {"messages": memory.messages[-20:], "count": len(memory.messages)}

