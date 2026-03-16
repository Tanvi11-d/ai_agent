from fastapi import FastAPI,HTTPException,Depends
from utils import agent
from sqlalchemy.orm import Session
from database import Sessionlocal
from models import create_table,User
from utils import *

app=FastAPI()

create_table()


@app.get("/")
def msg():
    return {"message":"fastapi is working..."}

def get_db():
    db=Sessionlocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/session/")
def create_session(name:str,user:Message,query:str,db:Session=Depends(get_db)):
    try:
        data=User(name=name,notes=user.notes,tasks=user.tasks,message=user.message)
        print("data__",data)
        db.add(data)
        db.commit()
        db.refresh(data)


        memory=Message(
            notes=data.notes,
            tasks=data.tasks,
            message=data.message
        )

        memory.message.append(query)
        response=agent.run_sync(query,deps=memory,output_type=Result)
        return response.output
    
        # response=call_agent(query)
        # return response(db)
    
    except Exception as e:
        print("error_",e)
        raise HTTPException(status_code=404,detail=f"error in create_session {e}")
    

# @app.post("/ask_query/")
# def get_user(user_id:int,query:str,db:Session=Depends(get_db)):
#     try:
       
    #     data=crud.get_result(user_id,db)
    #     memory=Message(
    #         notes=data.notes,
    #         tasks=data.tasks,
    #         message=data.message
    #     )
    #     memory.message.append(query)
    #     response=agent.run_sync(query,deps=memory,output_type=Result)
    #     return response.output
    # except Exception as e:
    #     print("error_",e)
    #     raise HTTPException(status_code=404,detail=str(e))
    
@app.get("get_result")
def get_result(user_id:int,db:Session=Depends(get_db)):
    try:
        result = db.query(User).filter(User.user_id == user_id).first() 
        return result
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

