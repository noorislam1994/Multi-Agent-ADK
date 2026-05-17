# School Multi-Agent System with Google ADK

This project implements the GDG AI Dev Camp school A2A assignment.

## What Is Included

- Root Agent: `school_coordinator_agent`
- Subject sub-agents:
  - `english_teacher_agent`
  - `maths_teacher_agent`
  - `science_teacher_agent`
  - `history_teacher_agent`
- Bonus sub-agents:
  - `geography_teacher_agent`
  - `computer_science_teacher_agent`
- Bonus tools:
  - Safe calculator tool for Maths
  - Local school knowledge-search tool
- Bonus memory:
  - The custom demo UI stores recent chat history in `school_memory.json`

## Project Structure

```text
school_agent/
  agent.py          # Google ADK root agent and sub-agents
  tools.py          # Calculator and knowledge-search tools
  demo_engine.py    # Lightweight UI runtime
static/
  index.html        # Chat UI
  styles.css
  app.js
app.py              # Local web server for the custom UI
requirements.txt
```

## Setup

Create or repair a Python virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set your Gemini API key:

```powershell
$env:GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
$env:GOOGLE_GENAI_MODEL="gemini-2.5-flash"
```

You can also copy `school_agent/.env.example` to `school_agent/.env` for ADK CLI usage.

## Run With ADK

```powershell
adk web
```

Then choose `school_agent` in the ADK web UI.

CLI option:

```powershell
adk run school_agent
```

## Run The Custom UI

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:8080
```

The custom UI uses the same school coordinator idea, routes questions to subject teacher agents, uses calculator/search tools, and keeps memory. If `GOOGLE_API_KEY` is missing, it still runs in offline fallback mode for demonstration.

