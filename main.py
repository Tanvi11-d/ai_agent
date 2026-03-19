from fastapi import FastAPI,HTTPException,Depends
from sqlalchemy.orm import Session 
from database import Sessionlocal
from models import create_table, User,MessageHistory,Session as dbsession
from utils import *
from pydantic_ai.messages import ModelRequest, ModelResponse,UserPromptPart,TextPart,SystemPromptPart
import json

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
        if user_id<=0:
            return{"result":" Invalid User ID"}
        
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
        if session_id<=0:
            return {"result":" Invalid Session ID"}
        
        session = db.query(dbsession).filter(dbsession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        history = db.query(MessageHistory).filter(MessageHistory.session_id==session_id).all()


        message_history = []
        message_history.append(ModelRequest(parts=[SystemPromptPart(content=prompt)]))

        for h in history:
            message_history.append(ModelRequest(
                    parts=[
                        UserPromptPart(content=h.query)
                    ]
                )
            )

            message_history.append(ModelResponse(
                    parts=[TextPart(content=h.message)]
                )
            )

        print("message_history_____ :-",message_history)
        deps = DBResponse(db, session_id=session_id)

        response =await agent.run(
            query,
            deps=deps,
            message_history=message_history)
        
        # with open('response_formar.txt', "w+") as f:
        #     f.write(str(response.all_messages()))
        #     f.write("\n\n\n")
            # f.write("Message History JSON:-\n\n")
            # f.write(json.dump(response.all_messages_json))        

        
        print("message_history__",message_history)
        chat = MessageHistory(
            session_id=session_id,
            query=query,
            message=response.output)

        print("message__",response.output)

        db.add(chat)
        db.commit()
        db.refresh(chat)
        return {"result":response.output}
        
    except Exception as e:
        print("error_",e)
        log.error("session not created")
        raise HTTPException(status_code=500,detail=f"error in get_session {e}")



@app.get("/usersessions")
async def get_user_sessions(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        sessions = db.query(dbsession).filter(dbsession.user_id == user_id).all()

        result=[]
        for session in sessions:
            chats = db.query(MessageHistory).filter(MessageHistory.session_id == session.id).all()

            chat_list = []
            for chat in chats:
                chat_list.append({"query": chat.query,"response": chat.message})
            result.append({"session_id": session.id,"chats": chat_list})

        return {"user_id": user_id,"sessions": result}

    except Exception as e:
        log.error(f"Error fetching user sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    