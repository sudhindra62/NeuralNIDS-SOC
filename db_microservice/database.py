import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AttackLog(Base):
    __tablename__ = "attack_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, index=True)
    src_ip = Column(String, index=True)
    dst_ip = Column(String)
    dst_port = Column(String)
    proto = Column(String)
    service = Column(String)
    label = Column(String, index=True)
    confidence = Column(Float)
    duration = Column(Float)
    sbytes = Column(Integer)
    dbytes = Column(Integer)
    state = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)
