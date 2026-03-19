from dotenv import load_dotenv
import os
import requests
import logging
from pydantic_ai import Agent,RunContext
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from pydantic import Field
from dataclasses import dataclass
from models import Notes,Tasks
from sqlalchemy.orm import Session
import logfire


load_dotenv()

#load api_keys
api_key=os.getenv("Groq_api_key")
weather_api=os.getenv("weather_api")

logfire.configure()
logfire.instrument_pydantic_ai()

logger=logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')
log=logging.getLogger(logger)

@dataclass
class DBResponse:
    db: Session
    session_id : int = Field(description="chat session ID")


# llm model
model=GroqModel(
    "openai/gpt-oss-safeguard-20b",
    provider=GroqProvider(api_key=api_key))

prompt = f"""
You are a helpful AI assistant that manages tasks, notes, and weather queries.

Follow these rules strictly:

GENERAL BEHAVIOR:
- Be concise and direct.
- Do not explain your reasoning.
- Do not add extra text beyond the final answer.
- Do not mention which tool you used.
- Do not answer general knowledge questions.

TOOLS USAGE RULES:

1. WEATHER:
- If the user asks about weather, call the `get_weathers` tool.
- Return only the tool response.

2. NOTES:
- To show notes → call `show_notes`.
- Return only the final answer in numbered format.
- To delete notes → call `remove_notes`.

3. TASK MANAGEMENT:
- If user adds multiple tasks → add them one by one.

- To view tasks → call `view_task`
  → Return output exactly as received (no formatting changes).

- To complete/update task:
  a. If index is provided → use it directly.
  b. If NO index:
     → Match task using keywords from user input
     → Then call `complete_task` with correct index

  Examples:
  - "I bought AC"
  - "task buy tv is done"
  - "I completed AC"

- Convert text numbers into numeric:
  Example:
  - "task one" → 1
  - "task two" → 2

4. DELETE TASK:
- If user asks to remove/delete task → call `remove_task`
- Convert text numbers into numeric index if needed

5. COMBINED REQUEST:
- If user asks to show both tasks and notes:
  → Return final answer including tool names clearly

IMPORTANT:
- Always prioritize tool usage when applicable
- Always match tasks intelligently if index is missing
- Never hallucinate tasks or notes
"""

# prompt = f"""
#     - You are a helpful AI assistant.
#     - you are follow the below rules.

#     Rules:
#     1. if user ask weather then you are call get_weathers tool and return current weather data.
#     2. if you are showing notes then call show_notes and Return Only the all final answer with number format.
#     3. if user add multiple task or note then add one by one.
#     4. When the user asks to show tasks, call the view_task tool and return the tool output exactly as received with no extra text and format changes.
#     5. If the user asks to complete or update a task:
#         a. If user provides index number then call complete_task tool with index.
#         b. If user does NOT provide index and uses natural language then match task using keywords and call complete_task tool with correct index. Example:-
#             - "I bought AC"
#             - "task buy tv is done"
#             - "I completed AC"
#     6. If the user asks to remove or delete a notes then call remove_notes tool.
#     7. If the user asks to remove or delete a tasks then call remove_task tool.
#     8. Do not give extra information.
#     9. Do not explain reasoning.
#     10. Do not show which tool you used.
#     11. Do not give answer of general knowledge.
#     12. if user asks showing both task and notes,then return final answer with tool name.
#     13. If the user asks to complete or update a task,convert text number into numeric number.
#     14. if user asks to remove or delete notes and tasks,convert text number into numeric number.
#     15. Always try to match task using keywords when index is not provided.

# """
agent=Agent(
    model=model,
    deps_type=DBResponse,
    retries=60,
    system_prompt=prompt
)

# weather tool
@agent.tool
def get_weathers(ctx:RunContext[DBResponse],query:str):
    """fatched current weather data"""
    try:
        url=f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={weather_api}&units=metric"
        response = requests.get(url)
        data = response.json()
        log.info("Weather fatched!!")
        return f"Current weather is {data}"
    
    except:
        log.error("Weather not fatched!!")
        return "Unable to fatched weather" 

#Create Notes  
@agent.tool
def save_note(ctx:RunContext[DBResponse], query:str):
    """Save the all Notes"""    
    try:
        db=ctx.deps.db
        session_id=ctx.deps.session_id

        note_list=[n.strip() for n in query.split(",")] 
        # ctx.deps.notes.extend(note_list)

        for n in note_list:
            db.add(Notes(session_id=session_id,notes=n))
        log.info("Notes add")
        db.commit()
        return "Note saved"
    except:
        log.error("Notes not saved!!")
        return "Notes not saved"
      
# Show Notes      
@agent.tool
def show_notes(ctx:RunContext[DBResponse]):
    """show the Notes"""
    try:
        db = ctx.deps.db
        session_id = ctx.deps.session_id

        notes = db.query(Notes).filter_by(session_id=session_id).all()

        if not notes:
            return "Notes not added"
        log.info("Notes show")

        return "\n".join(f"{i+1}. {n.notes}" for i, n in enumerate(notes))
            
    except:
        log.error("Notes not show")
        return "Notes not found"
    
# Delete Notes   
@agent.tool
def remove_notes(ctx:RunContext[DBResponse], index:int):
    """remove notes by index"""
    try:
        # if not ctx.deps.notes:
        #     return "Notes not found"

        db=ctx.deps.db
        session_id=ctx.deps.session_id
        delete_notes=db.query(Notes).filter_by(session_id=session_id).all()

        if index<1 or index >len(delete_notes):
            return "Invalid task index"
        
        db.delete(delete_notes[index-1])
        db.commit()
        # ctx.deps.notes.pop(index-1)
        log.info("Notes deleted")
        return "Notes deleted"
    except:
        log.error("Notes not delete")
        return "Notes not deleted"
    
# Create Tasks 
@agent.tool
def add_task(ctx:RunContext[DBResponse],query:str):
    """add all task"""
    try:
        db=ctx.deps.db
        session_id=ctx.deps.session_id

        task_list=[t.strip() for t in query.split(",")] 
        # for t in task_list:
        #     ctx.deps.tasks.append({"task":t,"status":"Pending"})
        for t in task_list:
           db.add(Tasks(session_id=session_id,tasks=t,status="Pending"))

        db.commit()
        log.info("Task add")
        return "Task added"
    except:
        log.error("Task not added!!")
        return "Tasks not added"

# Show Tasks
@agent.tool
def view_task(ctx:RunContext[DBResponse]):
    """view all tasks"""
    try:
        # if not ctx.deps.tasks:
        #     return "Tasks not found"
        
        db=ctx.deps.db
        session_id=ctx.deps.session_id
        tasks=db.query(Tasks).filter_by(session_id=session_id).all()

        if not tasks:
            return "Tasks not added"
        
        result=" "
        for i,t in enumerate(tasks,start=1):
            result += f"{i}. {t.tasks} ({t.status})\n"
        
        log.info("Tasks show")
        return result
    except:
        log.error("tasks not show")
        return "Tasks not found"

# Update Tasks
@agent.tool       
def complete_task(ctx:RunContext[DBResponse], index:int):
    """update the task complete"""
    try:
        db=ctx.deps.db
        session_id=ctx.deps.session_id
        update=db.query(Tasks).filter_by(session_id=session_id).all()
        if index<1 or index >len(update):
            return "Invalid task index"
        
        update[index-1].status = "Completed"
        db.commit()
        log.info("task updated")
        return "Task marked as completed."
    except:
        log.error("task not updated")
        return "Tasks not updated"

# Delete Tasks
@agent.tool
def remove_task(ctx:RunContext[DBResponse],index:int):
    """remove tasks by index"""
    try:
        # if not ctx.deps.tasks:
        #     return "Tasks not found"
        db=ctx.deps.db
        session_id=ctx.deps.session_id
        delete_tasks=db.query(Tasks).filter_by(session_id=session_id).all()
        if index<1 or index >len(delete_tasks):
            return "Invalid task index"
        db.delete(delete_tasks[index-1])
        db.commit()
        log.info("Task deleted")
        # ctx.deps.tasks.pop(index-1)
    except:
        log.error("Tasks not deleted")
        return "Tasks deleted"
    
# def call_agent(query:str):
#     try:
#         memory.message.append(query)
#         response=agent.run_sync(query,deps=memory,output_type=Result)
#         # response=agent.run_sync(query,deps=Message,output_type=Result)

#         # print("all_message__",response.all_messages())
#         return response.output
#     except Exception as e:
#         logging.error("Sorry, I am facing an issue. Please try again.")
#         raise HTTPException(status_code=500,detail=str(e))

