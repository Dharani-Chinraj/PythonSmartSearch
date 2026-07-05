"""
llm_module.py
Groq LLM calls:
1. get_ai_answer          — main answer with citations + language support
2. build_search_query     — rewrites follow-up questions
3. get_related_questions  — generates Perplexity-style related questions
4. summarize_url          — summarizes any URL content
5. generate_report        — generates full research report
"""

import os
from groq import Groq


def build_context_block(search_results: list) -> str:
    """Turns search results into a numbered context block for the LLM prompt."""
    if not search_results:
        return "No search results were found."
    lines = []
    for i, r in enumerate(search_results, 1):
        lines.append(
            f"[{i}] {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}\n"
        )
    return "\n".join(lines)


def build_search_query(query: str, chat_history: list, api_key: str) -> str:
    """
    Rewrites a follow-up question into a standalone search query
    using recent chat history for context.
    """
    if not chat_history:
        return query

    client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))

    history_text = ""
    for msg in chat_history[-4:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content'][:200]}\n"

    rewrite_prompt = [
        {
            "role": "system",
            "content": (
                "You are a search query optimizer. Given a conversation history "
                "and a follow-up question, rewrite the follow-up as a clear, "
                "standalone Google search query. Return ONLY the search query, "
                "nothing else. No explanation, no quotes, just the query."
            )
        },
        {
            "role": "user",
            "content": (
                f"Conversation so far:\n{history_text}\n"
                f"Follow-up question: {query}\n\n"
                f"Rewrite as standalone search query:"
            )
        }
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=rewrite_prompt,
            temperature=0.1,
            max_tokens=50,
        )
        rewritten = response.choices[0].message.content.strip()
        return rewritten if rewritten else query
    except Exception:
        return query


def get_ai_answer(
    query: str,
    search_results: list,
    chat_history: list = None,
    api_key: str = None,
    language: str = "English"
) -> str:
    """
    Synthesizes an answer from search results using Groq LLM.
    Supports multiple languages via language parameter.
    Returns answer with [1], [2] citation markers.
    """
    client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
    context_block = build_context_block(search_results)

    system_prompt = (
        f"You are a helpful research assistant. Answer the user's question using ONLY "
        f"the numbered search results provided as context. Cite sources inline using "
        f"[1], [2], etc. matching the numbered results. If the context does not contain "
        f"enough information to answer confidently, say so honestly. "
        f"Keep answers clear and concise. "
        f"IMPORTANT: You must respond in {language} language only."
    )

    messages = [{"role": "system", "content": system_prompt}]

    if chat_history:
        messages.extend(chat_history[-6:])

    user_message = (
        f"Search results:\n{context_block}\n\n"
        f"Question: {query}\n\n"
        f"Answer in {language} using the search results above, with [n] citations."
    )
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.3,
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error getting AI response: {e}"


def get_related_questions(
    query: str,
    answer: str,
    api_key: str = None
) -> list[str]:
    """
    Generates 3 Perplexity-style related follow-up questions
    based on the current query and answer.
    """
    client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))

    prompt = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that suggests follow-up questions. "
                "Given a user's question and an AI answer, generate exactly 3 "
                "short, relevant follow-up questions the user might want to ask next. "
                "Return ONLY the 3 questions, one per line, no numbering, no extra text."
            )
        },
        {
            "role": "user",
            "content": (
                f"User asked: {query}\n\n"
                f"AI answered: {answer[:500]}\n\n"
                f"Generate 3 follow-up questions:"
            )
        }
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=prompt,
            temperature=0.5,
            max_tokens=150,
        )
        raw = response.choices[0].message.content.strip()
        questions = [q.strip() for q in raw.split("\n") if q.strip()]
        return questions[:3]
    except Exception:
        return []


def summarize_url(url: str, api_key: str = None) -> str:
    """
    Fetches content from a URL and summarizes it using Groq LLM.
    Uses requests + BeautifulSoup to extract page text.
    """
    import requests
    try:
        from bs4 import BeautifulSoup
    except Exception:
        return (
            "⚠️ Could not import BeautifulSoup (bs4). "
            "Install it with: pip install beautifulsoup4"
        )

    client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))

    # Step 1 — Fetch page content
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        # Limit to first 3000 chars to stay within token limits
        text = text[:3000]

        if not text.strip():
            return "⚠️ Could not extract readable content from this URL."

    except Exception as e:
        return f"⚠️ Could not fetch URL: {str(e)}"

    # Step 2 — Summarize with Groq
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that summarizes web pages. "
                        "Given raw webpage text, provide a clear, structured summary "
                        "with: 1) Main topic, 2) Key points (bullet list), "
                        "3) Important conclusions. Be concise."
                    )
                },
                {
                    "role": "user",
                    "content": f"Summarize this webpage content:\n\n{text}"
                }
            ],
            temperature=0.3,
            max_tokens=600,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error summarizing: {str(e)}"


def generate_report(topic: str, search_results: list, api_key: str = None) -> str:
    """
    Generates a full structured research report on a topic
    using search results as grounding context.
    """
    client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
    context_block = build_context_block(search_results)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert research analyst. Generate a comprehensive, "
                        "well-structured research report using the provided search results. "
                        "Format the report with these sections:\n"
                        "# [Topic] — Research Report\n"
                        "## Executive Summary\n"
                        "## Key Findings\n"
                        "## Detailed Analysis\n"
                        "## Conclusion\n"
                        "## Sources\n"
                        "Use [1], [2] citation markers throughout. "
                        "Be thorough but clear."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Topic: {topic}\n\n"
                        f"Search Results:\n{context_block}\n\n"
                        f"Generate a full research report:"
                    )
                }
            ],
            temperature=0.4,
            max_tokens=1500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error generating report: {str(e)}"