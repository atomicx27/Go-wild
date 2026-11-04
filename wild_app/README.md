# 🕵️ Wild App - Autonomous Web Researcher

This is an autonomous web researcher application built with Streamlit, Langchain, and DuckDuckGo Search. It uses a local Ollama model (`qwen2.5:1.5b`) to synthesize search results into a comprehensive report.

## Setup

1. Make sure you have Ollama installed and running with the `qwen2.5:1.5b` model available.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To start the Streamlit application, navigate to this directory and run:

```bash
streamlit run app.py
```

The application will be accessible via your web browser (typically at `http://localhost:8501`).
