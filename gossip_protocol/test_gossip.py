import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Base, get_db, Agent, Memory, Conversation
from api import app

# Use a memory database for testing
from sqlalchemy.pool import StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Add dummy data
    a1 = Agent(name="Test1", persona="P1")
    a2 = Agent(name="Test2", persona="P2")
    db.add(a1)
    db.add(a2)
    db.commit()

    m1 = Memory(agent_id=a1.id, content="M1")
    db.add(m1)

    c1 = Conversation(agent1_id=a1.id, agent2_id=a2.id, transcript="Hello")
    db.add(c1)
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)

def test_read_agents(test_db):
    response = client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test1"

def test_read_memories(test_db):
    response = client.get("/api/agents/1/memories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["content"] == "M1"

def test_read_conversations(test_db):
    response = client.get("/api/conversations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["transcript"] == "Hello"
