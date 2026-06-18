import re

def apply_diff(filepath: str, original_content: str, llm_response: str) -> bool:
    """Parses a git merge diff from the LLM response and applies it to the file."""

    # Extract the diff block using regex
    pattern = r'<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE'
    match = re.search(pattern, llm_response, re.DOTALL)

    if not match:
        print("❌ Could not find valid SEARCH/REPLACE block in LLM response.")
        print(f"LLM Response:\n{llm_response}")
        return False

    search_block = match.group(1)
    replace_block = match.group(2)

    if search_block not in original_content:
        print("❌ Search block does not exactly match original content.")
        print("Search block:")
        print(repr(search_block))
        return False

    new_content = original_content.replace(search_block, replace_block)

    with open(filepath, "w") as f:
        f.write(new_content)

    return True
