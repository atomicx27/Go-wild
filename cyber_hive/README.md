# Cyber Hive

Cyber Hive is an autonomous agent workflow engine powered by a local Ollama instance. It continuously monitors an inbox for raw ideas, requests, or problem descriptions. Once a text file is detected, the Hive Mind agent spins up to process the request using Ollama, generating insights, code, or detailed responses, which are then written to the outbox. Failed or unprocessable items are shuttled to the rejected pile.

It features a cyberpunk-themed, dark mode web interface with real-time SSE (Server-Sent Events) log streaming so you can watch the Hive Mind think and act in real-time as a glowing terminal feed.
