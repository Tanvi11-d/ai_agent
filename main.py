from fastapi import FastAPI,HTTPException,Depends
from utils import agent
from sqlalchemy.orm import Session
from database import Sessionlocal
from models import create_table, User,MessageHistory,Sessions
from utils import *

app=FastAPI()

create_table()

notes=[]
tasks=[]
message=[]

@app.get("/")
def msg():
    return {"message":"fastapi is working..."}

def get_db():
    db=Sessionlocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/user/")
async def create_user(name:str,db:Session=Depends(get_db)):
    try:
        user=User(name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
        log.info("user created")
        return user
    
    except Exception as e:
        log.error("user not created")
        raise HTTPException (status_code=500,detail=str(e))
        
@app.post("/session/")
async def get_session(user_id:int,query:str,db:Session=Depends(get_db)):
    try:
        user=db.query(User).filter(User.user_id==user_id).first()
        session_data=Sessions(notes=notes,tasks=tasks,user_id=user.user_id)
        db.add(session_data)
        db.commit()
        db.refresh(session_data)

        response = await agent.run(query,output_type=Result,message_history=SessionResponse)
        print("response_agent",response)

        # chat=MessageHistory(notes=data.notes,task=data.tasks,sessionid=Sessions.session_id)
        # db.add(chat)
        # db.commit()
        # db.refresh()

            
    except Exception as e:
        print("error_",e)
        log.error("session not created")
        raise HTTPException(status_code=500,detail=f"error in get_session {e}")

@app.post("/sessions/")
async def get_query(name:str,query:str,db:Session=Depends(get_db)):
    try:
        data = db.query(User).filter(User.name == name).first() 
        print("result",data)

        if not data:
            data=User(name=name,notes=notes,tasks=tasks,message=message)
            print("data__",data)
            db.add(data)
            db.commit()
            db.refresh(data)

        
        memory=Message(
            notes=data.notes,
            tasks=data.tasks,
            message=data.message
        )

        print("memory",memory)
        
        memory.message.append(query)



        response = await agent.run(query,deps=memory,output_type=Result)
        print("response_agent",response)
        
        #update data
        data.notes=memory.notes
        data.tasks=memory.tasks
        data.message=memory.message
        db.commit()

        # memory.message.append(response.output)
        return response.output
     
    except Exception as e:
        print("error_",e)
        raise HTTPException(status_code=500,detail=f"error in create_session {e}")
    
    
@app.get("/get_result/")
def get_result(user_id:int,db:Session=Depends(get_db)):
    try:

        result = db.query(User).filter(User.user_id == user_id).first() 
        return {"user_id":result.user_id,"name":result.name,"notes":result.notes,"tasks":result.tasks}
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
