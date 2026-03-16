from sqlalchemy.orm  import Session
from utils import *
from models import create_table,User
from main import *
from fastapi import HTTPException

create_table()

def create_user(db:Session,user:Message,name:str):
    try:
        data=User(name=name,notes=user.notes,tasks=user.tasks,message=user.message)
        db.add(data)
        db.commit()
        db.refresh(data)
        return data
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"error in create_user {e}" ) 
            
def get_result(db:Session,user_id):
    try:
        result = db.query(User).filter(User.user_id == user_id).first() 
        return result
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"error in get_result {e}")