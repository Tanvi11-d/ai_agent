from dotenv import load_dotenv
import os
import requests
import logging
from pydantic_ai import Agent,RunContext
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from pydantic import BaseModel,Field
from fastapi import HTTPException
# import logfire

load_dotenv()

#load api_keys
api_key=os.getenv("Groq_api_key")
weather_api=os.getenv("weather_api")

# logfire.configure()
# logfire.instrument_pydantic_ai()


logger=logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')
log=logging.getLogger(logger)

class Task(BaseModel):
    task:str
    status:str="Pending"

class Message(BaseModel):
    notes:list[str]=Field(default_factory=list)
    tasks:list[Task]=Field(default_factory=list)
    message:list[str]=Field(default_factory=list)

    class Config:
        from_attributes=True

class Result(BaseModel):
    result:str

# memory=Message()


# llm model
model=GroqModel(
    "llama-3.3-70b-versatile",
    provider=GroqProvider(api_key=api_key))

prompt=f"""
    - You are a helpful AI assistant.
    - you are follow the below rules.

    Rules:
    1. if user ask weather details then you are call get_weathers tool and return all current weather data.
    2. if user ask add notes,you are call save_note tool,respond "Note saved".
    3. if you are showing notes then call show_notes and  Return Only the all final answer with number format.
    4. if user add multiple task or note then add one by one.
    5. When the user asks to show tasks, call the view_task tool and return the tool output exactly as received with no extra text and format changes.
    6. If the user asks to complete or update a task, identify the index number and call the complete_task tool.
    7. Do not give extra information.
    8. Do not explain reasoning.
    9. Do not show which tool you used.
    10.Do not give answer except notes,weather and task.
    11.if user asks showing both task and notes,then return final answer with tool name.
    12.If the user asks to complete or update a task,convert text number into numeric number.
    13.if user asks to remove or delete notes and tasks,convert text number into numeric number.
    """
agent=Agent(
    model=model,
    deps_type=Message,
    system_prompt=prompt
)

# weather tool
@agent.tool
def get_weathers(ctx:RunContext,query:str):
    """fatched current weather data"""
    try:

        url=f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={weather_api}&units=metric"
        response = requests.get(url)
        data = response.json()
        log.info("Weather fatched!!")
        return data
    
    except:
        log.error("Weather not fatched!!")
        return "Unable to fatched weather" 

 

#Create Notes  
@agent.tool
def save_note(ctx:RunContext[Message],query:str):
    """Save the all Notes"""    
    try:

        note_list=[t.strip() for t in query.split(",")] 
        ctx.deps.notes.extend(note_list)
        log.info("Notes add")
        return "Note saved"
    except:
        log.error("Notes not saved!!")
        return "Notes not saved"
      
# Show Notes      
@agent.tool
def show_notes(ctx:RunContext[Message]):
    """show the Notes"""
    try:
        # if not ctx.deps.notes:
        #     return "Notes not found"
        log.info("Notes show")
        return "\n".join(f"{i+1}.{n}" for i,n in enumerate(ctx.deps.notes))
    
    except:
        log.error("Notes not show")
        return "Notes not found"
    
# Delete Notes   
@agent.tool
def remove_notes(ctx:RunContext[Message],index:int):
    """remove notes by index"""
    try:
        # if not ctx.deps.notes:
        #     return "Notes not found"
        ctx.deps.notes.pop(index-1)
        log.info("Notes deleted")
        return "Notes deleted"
    except:
        log.error("Notes not delete")
        return "Notes not deleted"
    
# Create Tasks 
@agent.tool
def add_task(ctx:RunContext[Message],query:str):
    """add all task"""
    try:
        task_list=[t.strip() for t in query.split(",")] 
        for t in task_list:
            ctx.deps.tasks.append(Task(task=t))
        log.info("Task add")
        return "Task added"
    except:
        log.error("Task not added!!")
        return "Tasks not added"

# Show Tasks
@agent.tool
def view_task(ctx:RunContext[Message]):
    """view all tasks"""
    try:
        # if not ctx.deps.tasks:
        #     return "Tasks not found"
        

        result=" "
        for i,t in enumerate(ctx.deps.tasks,start=1):
            result += f"{i}.{t.task} ({t.status})\n"
        
        log.info("Tasks show")
        return result
    except:
        log.error("tasks not show")
        return "Tasks not found"

# Update Tasks
@agent.tool       
def complete_task(ctx:RunContext[Message],index:int):
    """update the task complete"""
    try:
        if index<1 or index >len(ctx.deps.tasks):
            return "Invalid task index"
        
        ctx.deps.tasks[index-1].status = "Completed"
        log.info("task updated")
        return "Task marked as completed."
    except:
        log.error("task not updated")
        return "Tasks not updated"

# Delete Tasks
@agent.tool
def remove_task(ctx:RunContext[Message],index:int):
    """remove tasks by index"""
    try:
        # if not ctx.deps.tasks:
        #     return "Tasks not found"
        log.info("Task deleted")
        ctx.deps.tasks.pop(index-1)
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

