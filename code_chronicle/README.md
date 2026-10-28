# Code Chronicle

Code Chronicle is a retro-styled "commit history visualizer" that turns your git log into a pixel-art style interactive timeline.
It automatically pulls the git log of the repository, uses Ollama to generate a fun, RPG-style "lore" description for each commit based on its message and changed files, and displays it in a web UI.

## Features
- Reads local git repository commit history.
- Uses local Ollama instance to generate "lore" for commits.
- Retro pixel-art style web UI.
- FastAPI backend serving the timeline data.
