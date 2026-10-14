from pydantic_ai import Agent, RunContext, ModelSettings
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
import logfire
from fastapi import FastAPI

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
logfire_token = os.getenv("LOGFIRE_TOKEN")

app = FastAPI()

logfire.configure()
logfire.instrument_pydantic_ai()

class UserQuery(BaseModel):
    query: str = Field(description="Ask question")

class Add(BaseModel):
    result: int

model = GroqModel(
    "openai/gpt-oss-120b",
    provider=GroqProvider(api_key=api_key),
    settings=ModelSettings(temperature=0.1)
)


agent = Agent(
    model=model,
    output_type=str,
    retries=5,
    tools=[duckduckgo_search_tool()],
    system_prompt="""
You are a helpful assistant.

Rules:
- If the question is math related, call the addition tool.
- If the question is internat search, use DuckDuckGo search.
- Always give concise answers (one sentence).
"""
)


@agent.tool
def addition(ctx: RunContext, a: int, b: int) -> int:
    """Return sum of values"""
    return a + b

def result_query(query: str):
    run = agent.run_sync(query)
    return run.output



