from database import engine
from sqlalchemy.orm import mapped_column,Mapped,DeclarativeBase,relationship
from sqlalchemy import String,JSON,Integer,ForeignKey
from sqlalchemy.ext.mutable import MutableList
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__="user"

    user_id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String,nullable=False)
    session_ref:Mapped[MutableList['Sessions']]=relationship('Sessions',back_populates="user_ref")

    def __repr__(self):
        return f"<user_id:{self.user_id} Name:{self.name}>"
    
class Sessions(Base):
    __tablename__="session"

    session_id:Mapped[int]=mapped_column(Integer,primary_key=True)
    notes:Mapped[list]=mapped_column(JSON,default=list)
    tasks:Mapped[list]=mapped_column(JSON,default=list)
    userid:Mapped[int]=mapped_column(ForeignKey('user.user_id'))
    user_ref:Mapped[MutableList[User]]=relationship('User',back_populates="session_ref")
    message_ref:Mapped[MutableList['MessageHistory']]=relationship('MessageHistory',back_populates="session_ref")


class MessageHistory(Base):
    __tablename__="messagehistory"

    message_id:Mapped[int]=mapped_column(Integer,primary_key=True)
    notes:Mapped[list]=mapped_column(JSON,default=list)
    tasks:Mapped[list]=mapped_column(JSON,default=list)
    # message:Mapped[list]=mapped_column(JSON,default=list)
    sessionid:Mapped[int]=mapped_column(ForeignKey('session.session_id'))
    session_ref:Mapped[MutableList['Sessions']]=relationship('Sessions',back_populates="message_ref")

    
    
def create_table():
    Base.metadata.create_all(engine)
