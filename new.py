from dotenv import load_dotenv
import os
import requests
import logging
from pydantic_ai import Agent, RunContext, ModelSettings
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from fastapi import HTTPException
from langsmith import traceable

load_dotenv()

# API keys
api_key = os.getenv("Groq_api_key")
weather_api = os.getenv("weather_api")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

log = logging.getLogger(__name__)

# LLM Model
model = GroqModel(
    "openai/gpt-oss-120b",
    provider=GroqProvider(api_key=api_key),
    settings=ModelSettings(temperature=0.1)
)

prompt = """
You are a helpful AI assistant.

Rules:
1. If user asks weather, call get_weathers.
2. If user adds notes, call save_note.
3. If user asks to show notes, call show_notes.
4. If user adds tasks, call add_task.
5. If user asks to show tasks, call view_task.
6. If user asks to complete task, call complete_task.
7. Do not give extra explanation.
"""

agent = Agent(
    model=model,
    system_prompt=prompt
)

# WEATHER TOOL
@agent.tool
def get_weathers(ctx: RunContext, query: str):
    """Fetch current weather"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={weather_api}&units=metric"
        response = requests.get(url)
        data = response.json()

        log.info("Weather fetched")
        return data

    except Exception:
        log.error("Weather fetch failed")
        return "Unable to fetch weather"


# NOTES TOOL
@agent.tool
def save_note(ctx: RunContext, query: str):
    """Save notes in context memory"""

    if "notes" not in ctx.state:
        ctx.state["notes"] = []

    notes = ctx.state["notes"]

    note_list = [t.strip() for t in query.split(",")]

    for note in note_list:
        notes.append(note)

    log.info("Note saved")

    return "Note saved"


@agent.tool
def show_notes(ctx: RunContext):
    """Show notes"""

    notes = ctx.state.get("notes", [])

    if not notes:
        return "Notes not found"

    result = ""
    for i, note in enumerate(notes, start=1):
        result += f"{i}. {note}\n"

    log.info("Notes shown")

    return result


# TASK TOOLS
@agent.tool
def add_task(ctx: RunContext, query: str):
    """Add task"""

    if "tasks" not in ctx.state:
        ctx.state["tasks"] = []

    tasks = ctx.state["tasks"]

    task_list = [t.strip() for t in query.split(",")]

    for task in task_list:
        tasks.append({
            "task": task,
            "status": "Pending"
        })

    log.info("Task added")

    return "Task added"


@agent.tool
def view_task(ctx: RunContext):
    """View tasks"""

    tasks = ctx.state.get("tasks", [])

    if not tasks:
        return "Tasks not found"

    result = ""

    for i, t in enumerate(tasks, start=1):
        result += f"{i}. {t['task']} ({t['status']})\n"

    log.info("Tasks shown")

    return result


@agent.tool
def complete_task(ctx: RunContext, index: int):
    """Complete task"""

    tasks = ctx.state.get("tasks", [])

    if index < 1 or index > len(tasks):
        return "Invalid task index"

    tasks[index - 1]["status"] = "Completed"

    log.info("Task updated")

    return "Task marked as completed."


# CALL AGENT
@traceable(name="call_agent")
def call_agent(query: str):
    try:
        response = agent.run_sync(query)
        return response

    except Exception as e:
        log.error("Agent error")
        raise HTTPException(status_code=500, detail=str(e))