import time
import random
from sqlalchemy.orm import Session
from db import SessionLocal, init_db, Agent, Memory, Conversation
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

def setup_agents(db: Session):
    init_db()
    initial_agents = [
        {"name": "Alice", "persona": "A paranoid hacker who trusts no one."},
        {"name": "Bob", "persona": "An overly optimistic salesman."},
        {"name": "Charlie", "persona": "A gossipy barista who hears everything."}
    ]
    for agent_data in initial_agents:
        if not db.query(Agent).filter_by(name=agent_data["name"]).first():
            agent = Agent(name=agent_data["name"], persona=agent_data["persona"])
            db.add(agent)
            db.commit()
            db.refresh(agent)
            mem = Memory(agent_id=agent.id, content=f"I am {agent.name}.")
            db.add(mem)
            db.commit()

def generate_conversation(agent1: Agent, agent2: Agent, llm) -> str:
    # A simple back-and-forth conversation
    mem1 = " ".join([m.content for m in agent1.memories[-3:]]) # recent memories
    mem2 = " ".join([m.content for m in agent2.memories[-3:]])

    sys_msg1 = f"You are {agent1.name}. Persona: {agent1.persona}. Recent memories: {mem1}. Have a very short, 2 sentence conversation with {agent2.name}."
    sys_msg2 = f"You are {agent2.name}. Persona: {agent2.persona}. Recent memories: {mem2}. Respond to {agent1.name} in 2 sentences."

    # Agent 1 starts
    msg1 = llm.invoke([SystemMessage(content=sys_msg1), HumanMessage(content=f"Hello {agent2.name}!")])
    # Agent 2 responds
    msg2 = llm.invoke([SystemMessage(content=sys_msg2), HumanMessage(content=msg1.content)])

    transcript = f"{agent1.name}: {msg1.content}\n{agent2.name}: {msg2.content}"
    return transcript

def extract_memory(agent: Agent, transcript: str, llm) -> str:
    prompt = f"Given this conversation: {transcript}\nWhat is one new, concise piece of information (max 1 sentence) that {agent.name} learned? If nothing new, reply 'Nothing'."
    response = llm.invoke(prompt)
    return response.content.strip()

def run_simulation_step():
    db = SessionLocal()
    llm = ChatOllama(model="llama3.2:1b")

    setup_agents(db)
    agents = db.query(Agent).all()
    if len(agents) < 2:
        return

    a1, a2 = random.sample(agents, 2)

    print(f"--- Chat: {a1.name} & {a2.name} ---")
    transcript = generate_conversation(a1, a2, llm)
    print(transcript)

    conv = Conversation(agent1_id=a1.id, agent2_id=a2.id, transcript=transcript)
    db.add(conv)
    db.commit()

    # Extract new memories
    new_mem1 = extract_memory(a1, transcript, llm)
    if new_mem1.lower() != 'nothing' and new_mem1:
        db.add(Memory(agent_id=a1.id, content=new_mem1))

    new_mem2 = extract_memory(a2, transcript, llm)
    if new_mem2.lower() != 'nothing' and new_mem2:
        db.add(Memory(agent_id=a2.id, content=new_mem2))

    db.commit()
    db.close()

if __name__ == "__main__":
    while True:
        try:
            run_simulation_step()
            time.sleep(10) # 10 seconds between interactions
        except Exception as e:
            print(f"Error in simulation: {e}")
            time.sleep(5)
