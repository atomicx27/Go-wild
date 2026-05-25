import pytest
import os
import shutil
from pathlib import Path
from system_architect.core import Architect

class MockArchitect(Architect):
    def _query_ollama(self, prompt):
        return """```json
{
  "dirs": ["app", "app/utils"],
  "files": [
    {"path": "app/main.py", "content": "print('hello from main')"},
    {"path": "app/utils/helper.py", "content": "def help(): pass"}
  ]
}
```"""

def test_architect_scaffolding(tmp_path):
    # Setup
    test_outdir = tmp_path / "blueprints"
    architect = MockArchitect(output_dir=str(test_outdir))

    # Execute
    base_path = architect.run("Test project", "test_auto_project")

    # Verify
    assert base_path.exists()
    assert (base_path / "app").is_dir()
    assert (base_path / "app" / "utils").is_dir()

    main_file = base_path / "app" / "main.py"
    helper_file = base_path / "app" / "utils" / "helper.py"

    assert main_file.is_file()
    assert helper_file.is_file()

    with open(main_file, "r") as f:
        assert f.read() == "print('hello from main')"

def test_path_traversal_prevention(tmp_path):
    # Setup
    test_outdir = tmp_path / "blueprints"

    class EvilMockArchitect(Architect):
        def _query_ollama(self, prompt):
            return """```json
{
  "dirs": ["../../evil_dir"],
  "files": [
    {"path": "../evil.py", "content": "print('evil')"}
  ]
}
```"""

    architect = EvilMockArchitect(output_dir=str(test_outdir))

    # Execute
    base_path = architect.run("Test project", "test_auto_project")

    # Verify traversal failed
    assert not (test_outdir / "evil_dir").exists()
    assert not (test_outdir / "evil.py").exists()
    assert not (tmp_path / "evil_dir").exists()
    assert not (tmp_path / "evil.py").exists()

def test_extract_json():
    architect = Architect()

    # Test valid json wrapped in markdown
    text1 = "```json\n{\"dirs\": [\"a\"], \"files\": []}\n```"
    assert architect._extract_json(text1) == {"dirs": ["a"], "files": []}

    # Test valid json without markdown
    text2 = "{\"dirs\": [\"a\"], \"files\": []}"
    assert architect._extract_json(text2) == {"dirs": ["a"], "files": []}

    # Test json with extra conversational text
    text3 = "Here is the blueprint:\n```\n{\"dirs\": [\"a\"], \"files\": []}\n```\nHave fun!"
    assert architect._extract_json(text3) == {"dirs": ["a"], "files": []}
