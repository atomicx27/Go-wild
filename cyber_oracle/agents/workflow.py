import asyncio
import json
import re
from agents.llm import ask_ollama

async def run_oracle_workflow(query: str, update_queue: asyncio.Queue):
    """
    Executes the multi-agent pipeline:
    1. The Fixer: Breaks down the query.
    2. The Netrunners: Researches sub-topics concurrently.
    3. The Synthesizer: Compiles the final dossier.
    """

    await update_queue.put({"status": "analyzing", "message": "Initiating connection... consulting The Fixer."})

    # 1. The Fixer
    fixer_sys = "You are 'The Fixer', a master data planner. Break down the user's query into 2 to 3 distinct sub-topics for deep research. Output ONLY a valid JSON list of strings representing the sub-topics, nothing else."
    fixer_msg = [{"role": "system", "content": fixer_sys}, {"role": "user", "content": f"Query: {query}\n\nBreak down into sub-topics:"}]

    fixer_response = await ask_ollama(fixer_msg, temperature=0.3)

    # Attempt to parse JSON from Fixer
    sub_topics = []
    try:
        # Simple extraction in case it wraps it in markdown blocks
        match = re.search(r'\[.*\]', fixer_response, re.DOTALL)
        if match:
             sub_topics = json.loads(match.group(0))
        else:
             sub_topics = json.loads(fixer_response)

        if not isinstance(sub_topics, list):
             raise ValueError("Not a list")
    except Exception as e:
        print(f"Failed to parse Fixer JSON: {fixer_response}. Using default fallback.")
        sub_topics = [f"{query} - Origins", f"{query} - Core Mechanisms", f"{query} - Future Implications"]

    await update_queue.put({"status": "researching", "message": f"Fixer identified sub-topics: {', '.join(sub_topics)}."})
    await update_queue.put({"status": "researching", "message": "Deploying Netrunner agents to the datastreams..."})

    # 2. The Netrunners (Concurrent)
    async def research_topic(topic):
        netrunner_sys = "You are a 'Netrunner', a deep-dive research agent. Provide a concise but highly detailed and factual 2-paragraph summary on the given topic."
        netrunner_msg = [{"role": "system", "content": netrunner_sys}, {"role": "user", "content": f"Research topic: {topic}"}]
        res = await ask_ollama(netrunner_msg, temperature=0.5)
        return {"topic": topic, "content": res}

    tasks = [research_topic(t) for t in sub_topics]
    research_results = await asyncio.gather(*tasks)

    await update_queue.put({"status": "synthesizing", "message": "Netrunners returned. Uploading data to The Synthesizer..."})

    # 3. The Synthesizer
    synth_sys = "You are 'The Synthesizer'. Compile the provided research notes into a cohesive, highly engaging, cyberpunk-themed markdown dossier. Use headings, bullet points, and dramatic formatting."

    compiled_notes = "\n\n".join([f"## {r['topic']}\n{r['content']}" for r in research_results])
    synth_prompt = f"Original Query: {query}\n\nResearch Notes:\n{compiled_notes}\n\nSynthesize this into the final dossier."

    synth_msg = [{"role": "system", "content": synth_sys}, {"role": "user", "content": synth_prompt}]

    final_dossier = await ask_ollama(synth_msg, temperature=0.7)

    await update_queue.put({"status": "complete", "message": "Dossier complete. Closing connection.", "dossier": final_dossier})
