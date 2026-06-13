from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Deck(Base):
    __tablename__ = 'decks'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    cards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")

class Flashcard(Base):
    __tablename__ = 'flashcards'
    id = Column(Integer, primary_key=True)
    deck_id = Column(Integer, ForeignKey('decks.id'), nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)

    # Simple Leitner System
    box = Column(Integer, default=1)  # 1 to 5
    next_review = Column(DateTime, default=datetime.utcnow)

    deck = relationship("Deck", back_populates="cards")

# Initialize DB in data directory
data_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(data_dir, exist_ok=True)
DB_PATH = os.path.join(data_dir, 'flashcards.db')

engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
