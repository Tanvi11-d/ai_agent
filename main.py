from fastapi import FastAPI,HTTPException,Depends
from sqlalchemy.orm import Session 
from database import Sessionlocal
from models import create_table, User,MessageHistory,Session as dbsession
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
        raise HTTPException(status_code=500,detail=str(e))
    
@app.post("/session/")
async def get_session(user_id:int,db:Session=Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        session_data=dbsession(user_id=user_id)
        db.add(session_data)
        db.commit()
        db.refresh(session_data)
        return session_data
        
    except Exception as e:
        print("error_",e)
        log.error("session not created")
        raise HTTPException(status_code=500,detail=f"error in get_session {e}")
  
@app.post("/chat/")
async def get_message(session_id:int,query:str,db:Session=Depends(get_db)):
    try:
       
        
        session = db.query(dbsession).filter(dbsession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        history = db.query(MessageHistory).filter_by(session_id=session_id).all()

        message_history = []
        for h in history:
            message_history.append(h.message)

        deps = DBResponse(db, session_id= session_id)

        response =await agent.run(
            query,
            deps=deps,
            message_history=message_history   
        )

        chat = MessageHistory(
            session_id=session_id,
            message=response.output
        )

        db.add(chat)
        db.commit()

        return {"result":response.output}

    except Exception as e:
        print("error_",e)
        log.error("session not created")
        raise HTTPException(status_code=500,detail=f"error in get_session {e}")
