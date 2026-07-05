# 🔎 Smart Search AI

A custom AI-powered search engine that combines live web search (DuckDuckGo)
with LLM reasoning (Groq / Llama 3.1) to answer questions with cited sources —
similar to how Perplexity works.

## Features
- Live web search (no API key needed for search)
- AI-synthesized answers grounded in real search results
- Inline numbered citations with clickable source links
- Multi-turn conversation memory (follow-up questions work)

## Tech Stack
- Python
- Streamlit (UI + deployment)
- DuckDuckGo Search (`ddgs`) — free, no key
- Groq API (Llama 3.1 8B Instant) — free tier

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
You'll need a free Groq API key from https://console.groq.com

## Live Demo
[Add your deployed Streamlit link here after deployment]
