import os

INBOX_DIR = "mind_weaver/inbox"

def create_samples():
    os.makedirs(INBOX_DIR, exist_ok=True)

    samples = {
        "sample1_code.txt": """
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
""",
        "sample2_journal.txt": """
Today was a really productive day. I managed to fix that annoying bug in the authentication flow.
However, I still need to update the README to reflect the new changes.

TODO: Update the documentation for the auth API endpoints.
""",
        "sample3_concept_ai.txt": """
Artificial General Intelligence (AGI) refers to a machine's ability to understand, learn, and apply knowledge across a wide range of tasks at a level equal to or beyond human capabilities.
It contrasts with Narrow AI, which is designed to perform specific tasks.
""",
        "sample4_concept_machine_learning.txt": """
Machine Learning is a subset of artificial intelligence that involves training algorithms on data so they can make predictions or decisions without being explicitly programmed.
It is a key stepping stone towards achieving AGI.
"""
    }

    for filename, content in samples.items():
        filepath = os.path.join(INBOX_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"Created sample: {filepath}")

if __name__ == "__main__":
    create_samples()
