#!/bin/bash
set -e

echo "Updating packages and installing zstd..."
sudo apt-get update && sudo apt-get install -y zstd

echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh -o install_ollama.sh
bash install_ollama.sh

echo "Starting Ollama server..."
ollama serve > ollama.log 2>&1 &

echo "Waiting for Ollama to initialize..."
sleep 15

echo "Pulling model qwen2.5:0.5b..."
ollama pull qwen2.5:0.5b

echo "Installing Python dependencies..."
pip install -r nexus_sorter/requirements.txt

echo "Setup complete."
