from pydantic_ai import Agent,RunContext
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from dotenv import load_dotenv
import os
from pydantic import BaseModel,Field
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool



load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")

class TaskType(BaseModel):
    task: str = Field(description="math or search")
    query: str


class MathResult(BaseModel):
    result: int


model=GroqModel("moonshotai/kimi-k2-instruct-0905",
    provider=GroqProvider(api_key=api_key))

math_agent = Agent(
    model=model,
    output_type=MathResult,retries=10,
    system_prompt="Solve math problems."
)

@math_agent.tool
def add(ctx: RunContext[MathResult], a: int, b: int) -> int:
    """Return sum of two numbers"""
    return a + b



search_agent = Agent(
    model=model,
    tools=[duckduckgo_search_tool()],retries=10,
    system_prompt="Search internet and return concise answer."
)


planner_agent = Agent(
    model=model,
    output_type=TaskType,retries=10,
    system_prompt="""
Decide the task type:
- math → for calculations
- search → for general knowledge
"""
)



def run_multi_agent(user_query: str):

    plan = planner_agent.run_sync(user_query)

    if plan.output.task == "math":
        result = math_agent.run_sync(user_query)
        return result.output

    elif plan.output.task == "search":
        result = search_agent.run_sync(user_query)
        return result.output

    else:
        return "Task not supported"



print(run_multi_agent("add 10 and 20"))
print(run_multi_agent("what is color of sky"))
print(run_multi_agent("who is prime minister of india"))