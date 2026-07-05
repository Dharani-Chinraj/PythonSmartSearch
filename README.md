# 🔎 Smart Search AI

A Perplexity-style AI search engine that searches the live web and gives you cited, grounded answers — built with Streamlit, SerpApi, and Groq (Llama 3.1).

## ✨ Features

- **Web Search + AI Answer with Citations** — every answer is grounded in real-time web search results, not just model memory
- **Perplexity-style Source Cards** — numbered, clickable cards with favicon + domain for every source
- **Related Questions** — auto-generated follow-up questions you can click to keep exploring
- **Multi-language Answers** — get responses in English, Tamil, Hindi, Telugu, Malayalam, Kannada, French, Spanish, German, Arabic, or Chinese
- **URL Summarizer** — paste any link and get an instant AI summary
- **Research Report Generator** — enter a topic and get a full structured, cited report, downloadable as `.txt`
- **Conversation Memory** — follow-up questions are rewritten into standalone search queries using chat history

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Web Search**: SerpApi
- **AI / LLM**: Groq API (Llama 3.1)
- **Language**: Python

## 📂 Project Structure

```
├── app.py              # Main Streamlit app
├── search_module.py    # SerpApi search integration
├── llm_module.py        # Groq/Llama 3.1 answer generation, related questions, summarizer, report generator
├── requirements.txt      # Python dependencies
└── .env                 # API keys (not committed)
```

## 🔑 Setup

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API keys
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key
SERPAPI_KEY=your_serpapi_key
```

Get keys from:
- [Groq Console](https://console.groq.com)
- [SerpApi](https://serpapi.com)

### 4. Run the app
```bash
streamlit run app.py
```

## ☁️ Deployment (Streamlit Community Cloud)

1. Push this repo to GitHub (make sure `.env` is in `.gitignore` — never commit real keys)
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub repo
3. Set the main file path to `app.py`
  4. Deploy — the app will auto-redeploy every time you push changes to GitHub

## 📸 Modes

- **💬 Search & Answer** — ask anything, get a cited, grounded answer with sources and related questions
- **🔗 URL Summarizer** — paste a link, get a summary
- **📄 Research Report** — enter a topic, get a full structured report

## 📄 License

MIT — feel free to fork and build on this.

---

Built by Dharani Chinraj — [Portfolio](https://dharaniportfoliodata.lovable.app) · [LinkedIn](https://linkedin.com/in/dharani-chinraj)
