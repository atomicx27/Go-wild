import json
import os

REGISTRY_FILE = os.path.join(os.path.dirname(__file__), "registry.json")

def load_registry():
    """Loads the tool registry from the JSON file."""
    if not os.path.exists(REGISTRY_FILE):
        return {}

    try:
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("[Registry Error] Could not decode registry.json. Returning empty registry.")
        return {}

def save_registry(registry_data):
    """Saves the tool registry to the JSON file."""
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry_data, f, indent=4)

def add_tool(name, description, filepath, usage_example):
    """Adds a new tool to the registry."""
    registry = load_registry()
    registry[name] = {
        "description": description,
        "filepath": filepath,
        "usage_example": usage_example
    }
    save_registry(registry)
    print(f"[Registry] Added new tool: {name}")

def get_tool(name):
    """Retrieves a tool's details by name."""
    registry = load_registry()
    return registry.get(name)

def get_all_tools():
    """Returns all tools in the registry."""
    return load_registry()

def format_registry_for_llm():
    """Formats the registry into a string suitable for an LLM prompt."""
    registry = load_registry()
    if not registry:
        return "No tools currently exist in the registry."

    formatted = "Available Tools:\n"
    for name, details in registry.items():
        formatted += f"- {name}:\n"
        formatted += f"  Description: {details['description']}\n"
        formatted += f"  Filepath: {details['filepath']}\n"
        formatted += f"  Usage Example: {details['usage_example']}\n"

    return formatted

if __name__ == "__main__":
    print("Testing Registry...")
    add_tool("test_tool", "A tool for testing.", "tools/test_tool.py", "python tools/test_tool.py arg1")
    print(format_registry_for_llm())
