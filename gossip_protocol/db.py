from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone

Base = declarative_base()

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    persona = Column(Text)
    memories = relationship('Memory', back_populates='agent')

class Memory(Base):
    __tablename__ = 'memories'
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    content = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    agent = relationship('Agent', back_populates='memories')

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    agent1_id = Column(Integer, ForeignKey('agents.id'))
    agent2_id = Column(Integer, ForeignKey('agents.id'))
    transcript = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    agent1 = relationship('Agent', foreign_keys=[agent1_id])
    agent2 = relationship('Agent', foreign_keys=[agent2_id])

engine = create_engine('sqlite:///gossip.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
