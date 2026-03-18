from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DB_URL")
engine=create_engine(url=DATABASE_URL,echo=True)
Sessionlocal=sessionmaker(bind=engine,expire_on_commit=False)
