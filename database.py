from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


password=os.getenv("password")
DATABASE_URL = f"postgresql+psycopg2://postgres:{password}@localhost:8000/ai_assistant"

engine=create_engine(DATABASE_URL,echo=True)
Sessionlocal=sessionmaker(bind=engine,expire_on_commit=False)
