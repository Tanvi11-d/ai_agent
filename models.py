from database import engine
from sqlalchemy.orm import mapped_column,Mapped,DeclarativeBase,relationship
from sqlalchemy import String,Integer,ForeignKey
from sqlalchemy.ext.mutable import MutableList

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__="user"

    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String,nullable=False)
    session_ref:Mapped[MutableList['Session']]=relationship('Session',back_populates="user_ref",cascade="all, delete")

    def __repr__(self):
        return f"<user_id:{self.id} Name:{self.name}>"
    
class Session(Base):
    __tablename__="sessions"

    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey('user.id'))
    user_ref:Mapped[MutableList[User]]=relationship('User',back_populates="session_ref")
    message_ref:Mapped[MutableList['MessageHistory']]=relationship('MessageHistory',back_populates="sessions_ref")
    note_ref:Mapped[MutableList['Notes']]=relationship('Notes',back_populates="note_session_ref")
    task_ref:Mapped[MutableList['Tasks']]=relationship('Tasks',back_populates="task_session_ref")

class MessageHistory(Base):
    __tablename__="messagehistory"

    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    message:Mapped[str]=mapped_column(String)
    session_id:Mapped[int]=mapped_column(ForeignKey('sessions.id'))
    sessions_ref:Mapped[MutableList['Session']]=relationship('Session',back_populates="message_ref")

class Notes(Base):
    __tablename__="notes"

    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    notes:Mapped[str]=mapped_column(String)
    session_id:Mapped[int]=mapped_column(ForeignKey('sessions.id'))
    note_session_ref:Mapped[MutableList['Session']]=relationship('Session',back_populates="note_ref")    

class Tasks(Base):
    __tablename__="tasks"

    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    tasks:Mapped[str]=mapped_column(String)
    status:Mapped[str]=mapped_column(String)
    session_id:Mapped[int]=mapped_column(ForeignKey('sessions.id'))
    task_session_ref:Mapped[MutableList['Session']]=relationship('Session',back_populates="task_ref")

def create_table():
    Base.metadata.create_all(engine)



