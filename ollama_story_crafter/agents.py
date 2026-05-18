import json
from .client import OllamaClient

def director_agent(client: OllamaClient, prompt: str):
    print("[Director] Planning the story...")
    system_prompt = """
    You are an expert Story Director. Based on the user's prompt, create a compelling story outline.
    You must output your response STRICTLY as a JSON object with the following schema:
    {
        "title": "A catchy title for the story",
        "synopsis": "A brief summary of the entire plot",
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Title of chapter 1",
                "description": "Detailed description of what happens in this chapter. Include character motivations and key events."
            },
            ...
        ]
    }
    Generate between 3 to 5 chapters. Do not include any markdown formatting like ```json in the output.
    """

    response = client.generate(prompt=prompt, system=system_prompt, format="json")
    try:
        outline = json.loads(response)
        return outline
    except json.JSONDecodeError:
        print("[Director] Failed to decode JSON from Ollama. Returning fallback.")
        return json.loads(client._mock_response("director", "json"))

def writer_agent(client: OllamaClient, synopsis: str, chapter_info: dict, previous_chapters_summary: str = ""):
    print(f"[Writer] Drafting Chapter {chapter_info['chapter_number']}: {chapter_info['title']}...")
    system_prompt = """
    You are an expert Creative Writer. Your task is to write a single chapter of a story based on the provided synopsis and chapter description.
    Make the story engaging, with good pacing, descriptive language, and dialogue if appropriate.
    Write ONLY the story content for this chapter. Do not include the chapter title, as it will be added later. Do not add any introductory or concluding remarks.
    """

    prompt_context = f"Story Synopsis: {synopsis}\n"
    if previous_chapters_summary:
        prompt_context += f"Summary of Previous Chapters: {previous_chapters_summary}\n"
    prompt_context += f"Current Chapter Description: {chapter_info['description']}\n\nWrite the chapter now:"

    return client.generate(prompt=prompt_context, system=system_prompt)

def editor_agent(client: OllamaClient, chapter_content: str):
    print("[Editor] Reviewing and refining chapter...")
    system_prompt = """
    You are an expert Story Editor. Review the provided chapter text.
    Your goals are to fix any grammatical errors, improve the flow and pacing, and enhance the descriptive language.
    Return ONLY the edited chapter text. Do not add any comments, notes, or markdown formatting like ```text.
    """

    return client.generate(prompt=chapter_content, system=system_prompt)

def summarizer_agent(client: OllamaClient, chapter_content: str):
    print("[Summarizer] Summarizing chapter for context...")
    system_prompt = """
    You are a summarization assistant. Summarize the provided chapter in 2-3 sentences.
    This summary will be used to give context to the writer for the next chapter.
    Return ONLY the summary.
    """
    return client.generate(prompt=chapter_content, system=system_prompt)
