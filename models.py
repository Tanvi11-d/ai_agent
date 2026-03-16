from database import engine
from sqlalchemy.orm import mapped_column,Mapped,DeclarativeBase
from sqlalchemy import String,JSON

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__="user"

    user_id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String,nullable=False)
    notes:Mapped[list]=mapped_column(JSON,default=list)
    tasks:Mapped[list]=mapped_column(JSON,default=list)
    message:Mapped[list]=mapped_column(JSON,default=list)
    
    def __repr__(self):
        return f"<user_id:{self.user_id} Name:{self.name} Notes:{self.notes} Message:{self.message}>"
    
def create_table():
    Base.metadata.create_all(engine)
