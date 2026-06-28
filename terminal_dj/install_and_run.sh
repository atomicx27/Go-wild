#!/bin/bash
pip install -r requirements.txt
ollama pull qwen2.5:0.5b
python3 main.py "$@"
