import os
from pathlib import Path

INBOX_DIR = Path("nexus_sorter/inbox")
INBOX_DIR.mkdir(parents=True, exist_ok=True)

files = {
    "random_python_script.py": '''def do_nothing():
    pass
    # I should write something here
    print("test")
    x = 1
    y = 2
    z = x + y
''',
    "weird_data.csv": '''id,name,age,favorite_color
1,John Doe,30,blue
2,Jane Smith,,green
3,Bob,,red
4,Alice,25,
''',
    "notes.txt": '''Remember to buy milk.
Also call mom.
Fix that bug in the production code that is causing memory leaks.
Or maybe play video games instead.
''',
    "todo.md": '''# To Do
- [ ] Fix bug
- [ ] Write tests
- [ ] Refactor
- [ ] Deploy
'''
}

for filename, content in files.items():
    with open(INBOX_DIR / filename, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Created {len(files)} files in {INBOX_DIR}")
