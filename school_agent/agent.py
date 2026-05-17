"""Google ADK multi-agent school coordinator.

Run with:
    adk web
or:
    adk run school_agent
"""

from __future__ import annotations

import os

from google.adk.agents import Agent

from .tools import calculator, school_knowledge_search


MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.5-flash")


english_teacher_agent = Agent(
    name="english_teacher_agent",
    model=MODEL,
    description="Handles English language, grammar, essays, comprehension, and literature questions.",
    instruction=(
        "You are the English Teacher Agent. Help students with grammar, essay planning, "
        "paragraph structure, comprehension, vocabulary, poetry, stories, and literature. "
        "Explain ideas clearly, give examples, and use an encouraging teacher tone. "
        "If the student asks for a full assignment, guide them with an outline and sample sections."
    ),
    tools=[school_knowledge_search],
)

maths_teacher_agent = Agent(
    name="maths_teacher_agent",
    model=MODEL,
    description="Handles maths questions including arithmetic, algebra, geometry, statistics, and calculus.",
    instruction=(
        "You are the Maths Teacher Agent. Solve maths questions step by step. "
        "Use the calculator tool for arithmetic when exact calculation is needed. "
        "Show formulas, substitutions, and final answers clearly."
    ),
    tools=[calculator, school_knowledge_search],
)

science_teacher_agent = Agent(
    name="science_teacher_agent",
    model=MODEL,
    description="Handles science questions across biology, chemistry, physics, and experiments.",
    instruction=(
        "You are the Science Teacher Agent. Explain biology, chemistry, physics, and experiments "
        "with accurate school-level reasoning. Define key terms, connect ideas to examples, "
        "and include safety notes for practical experiments when relevant."
    ),
    tools=[school_knowledge_search],
)

history_teacher_agent = Agent(
    name="history_teacher_agent",
    model=MODEL,
    description="Handles history questions including events, civilizations, source analysis, and timelines.",
    instruction=(
        "You are the History Teacher Agent. Explain historical events, causes, consequences, "
        "timelines, civilizations, and source analysis. Separate facts from interpretation "
        "and help students write balanced answers."
    ),
    tools=[school_knowledge_search],
)

geography_teacher_agent = Agent(
    name="geography_teacher_agent",
    model=MODEL,
    description="Handles geography questions including maps, climate, landforms, population, and hazards.",
    instruction=(
        "You are the Geography Teacher Agent. Explain physical and human geography with examples, "
        "case-study style structure, and clear links between causes, effects, and responses."
    ),
    tools=[school_knowledge_search],
)

computer_science_teacher_agent = Agent(
    name="computer_science_teacher_agent",
    model=MODEL,
    description="Handles computer science questions including programming, algorithms, data, and networks.",
    instruction=(
        "You are the Computer Science Teacher Agent. Explain programming, algorithms, data structures, "
        "networks, databases, and cybersecurity. Use short code examples only when they help."
    ),
    tools=[school_knowledge_search],
)

root_agent = Agent(
    name="school_coordinator_agent",
    model=MODEL,
    description="Routes student questions to specialist school subject teacher agents.",
    instruction=(
        "You are the School Coordinator Root Agent in a Google ADK agent-to-agent school system. "
        "Your primary job is to understand the student's request, identify the best subject, "
        "and delegate to exactly one specialist teacher sub-agent whenever possible. "
        "Delegate English requests to english_teacher_agent, maths requests to maths_teacher_agent, "
        "science requests to science_teacher_agent, history requests to history_teacher_agent, "
        "geography requests to geography_teacher_agent, and computing/programming requests to "
        "computer_science_teacher_agent. If a question spans subjects, choose the most relevant "
        "main subject and mention the crossover. Keep final responses student-friendly, structured, "
        "and concise unless the student asks for depth."
    ),
    sub_agents=[
        english_teacher_agent,
        maths_teacher_agent,
        science_teacher_agent,
        history_teacher_agent,
        geography_teacher_agent,
        computer_science_teacher_agent,
    ],
)

