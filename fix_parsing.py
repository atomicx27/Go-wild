import re

def fix_queries(queries_text):
    # Try splitting by comma first if it exists
    if ',' in queries_text:
        return [q.strip() for q in queries_text.split(",") if q.strip()][:3]
    else:
        # Fallback to splitting by newlines and stripping numbers (e.g. "1. Query")
        lines = [line.strip() for line in queries_text.split('\n') if line.strip()]
        queries = []
        for line in lines:
            # remove leading numbers and dots
            clean_line = re.sub(r'^\d+\.\s*', '', line).strip()
            # remove quotes
            clean_line = clean_line.strip('"').strip("'")
            if clean_line:
                queries.append(clean_line)
        return queries[:3]

text = "1. Quantum Computing overview\n2. History of Quantum Computing\n3. Future of Quantum Computing"
print(fix_queries(text))
