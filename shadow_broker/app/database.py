import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Bounty(Base):
    __tablename__ = 'bounties'

    id = Column(Integer, primary_key=True)
    filepath = Column(String(255), nullable=False)
    comment_type = Column(String(50), nullable=False) # TODO or FIXME
    description = Column(Text, nullable=False)
    original_code = Column(Text, nullable=False)
    proposed_fix = Column(Text, nullable=True)
    status = Column(String(50), default='OPEN') # OPEN, CLAIMED, COMPLETED

# Use absolute path for sqlite db in /app to ensure it resolves correctly
DB_URL = "sqlite:////app/shadow_broker/shadow_broker.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
