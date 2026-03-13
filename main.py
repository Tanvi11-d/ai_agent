from fastapi import FastAPI,HTTPException
from utils import call_agent

app=FastAPI()

@app.get("/")
def msg():
    return {"message":"fastapi is working..."}

@app.post("/ask_query/")
def get_query(query:str):
    try:
        response=call_agent(query)
        return response
    
    except Exception as e:
        raise HTTPException(status_code=404,detail=str(e))

