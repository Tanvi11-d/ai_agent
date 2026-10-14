from fastapi import FastAPI,HTTPException
from main import result_query

app=FastAPI()

@app.post("/ask")
def ask(query: str):
    try:
        result = result_query(query)
        return {"response": result}
    except HTTPException as e:
        print("error_",e)
        raise HTTPException(status_code=500,detail=str(e))