"""
Smart Search AI — Full Version
Features:
- Web Search + AI Answer with Citations
- Related Questions (Perplexity-style)
- Answer Language Selector
- URL Summarizer
- Research Report Generator
- API keys from .env / Streamlit secrets
"""

import os
from urllib.parse import urlparse
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from search_module import get_search_results
from llm_module import (
    get_ai_answer,
    build_search_query,
    get_related_questions,
    summarize_url,
    generate_report
)

# ---- Load API keys ----
load_dotenv()

try:
    groq_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    serp_key = st.secrets.get("SERPAPI_KEY", os.getenv("SERPAPI_KEY"))
except Exception:
    groq_key = os.getenv("GROQ_API_KEY")
    serp_key = os.getenv("SERPAPI_KEY")

# ---- Page config ----
st.set_page_config(
    page_title="Smart Search AI",
    page_icon="🔎",
    layout="centered"
)

# ---- Custom CSS ----
st.markdown("""
    <style>
        .main { background-color: #0f1117; }
        .stButton>button {
            border-radius: 8px;
            font-size: 14px;
        }
        .stExpander {
            border-radius: 8px;
        }
        .reportview-container {
            margin-top: -2em;
        }

        /* ---- Perplexity-style source cards ---- */
        .source-grid {
            display: flex;
            gap: 10px;
            overflow-x: auto;
            padding: 6px 2px 14px 2px;
            scrollbar-width: thin;
        }
        .source-card {
            flex: 0 0 auto;
            width: 190px;
            background: #1a1c24;
            border: 1px solid #2a2d38;
            border-radius: 12px;
            padding: 12px 14px;
            text-decoration: none;
            display: block;
            transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
        }
        .source-card:hover {
            transform: translateY(-3px);
            border-color: #6c63ff;
            box-shadow: 0 4px 14px rgba(108, 99, 255, 0.25);
        }
        .source-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            font-size: 11px;
            font-weight: 600;
            background: #6c63ff;
            color: white;
            border-radius: 5px;
            margin-bottom: 8px;
        }
        .source-title {
            font-size: 13px;
            font-weight: 600;
            color: #e6e6e6;
            line-height: 1.35;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            margin-bottom: 6px;
        }
        .source-domain {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: #8b8fa3;
        }
        .source-domain img {
            width: 14px;
            height: 14px;
            border-radius: 3px;
        }
    </style>
""", unsafe_allow_html=True)


def render_sources(results, key_prefix=""):
    """Renders search result sources as horizontally scrollable Perplexity-style cards.

    Uses an isolated iframe (components.html) instead of st.markdown, because
    st.markdown's HTML sanitizer can inconsistently render long strings with
    nested tags (e.g. <img> inside <a>), causing later cards to show as raw text.
    """
    if not results:
        return

    cards_html = ""
    for i, s in enumerate(results, 1):
        url = s.get("url", "#")
        title = s.get("title", "No title").replace('"', "&quot;")
        try:
            domain = urlparse(url).netloc.replace("www.", "") if url != "#" else "unknown"
        except Exception:
            domain = "unknown"

        favicon = f"https://www.google.com/s2/favicons?domain={domain}&sz=32" if domain != "unknown" else ""
        favicon_tag = f'<img src="{favicon}" />' if favicon else ""

        cards_html += (
            f'<a class="source-card" href="{url}" target="_blank" rel="noopener noreferrer">'
            f'<div class="source-badge">{i}</div>'
            f'<div class="source-title">{title}</div>'
            f'<div class="source-domain">{favicon_tag}<span>{domain}</span></div>'
            f'</a>'
        )

    full_html = f"""
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            background: transparent;
            font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
        }}
        .source-grid {{
            display: flex;
            gap: 10px;
            overflow-x: auto;
            padding: 6px 2px 14px 2px;
            scrollbar-width: thin;
        }}
        .source-card {{
            flex: 0 0 auto;
            width: 190px;
            background: #1a1c24;
            border: 1px solid #2a2d38;
            border-radius: 12px;
            padding: 12px 14px;
            text-decoration: none;
            display: block;
            box-sizing: border-box;
            transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
        }}
        .source-card:hover {{
            transform: translateY(-3px);
            border-color: #6c63ff;
            box-shadow: 0 4px 14px rgba(108, 99, 255, 0.25);
        }}
        .source-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            font-size: 11px;
            font-weight: 600;
            background: #6c63ff;
            color: white;
            border-radius: 5px;
            margin-bottom: 8px;
        }}
        .source-title {{
            font-size: 13px;
            font-weight: 600;
            color: #e6e6e6;
            line-height: 1.35;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            margin-bottom: 6px;
        }}
        .source-domain {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: #8b8fa3;
        }}
        .source-domain img {{
            width: 14px;
            height: 14px;
            border-radius: 3px;
        }}
    </style>
    </head>
    <body>
        <div class="source-grid">{cards_html}</div>
    </body>
    </html>
    """

    st.markdown("**📚 Sources**")
    components.html(full_html, height=155, scrolling=False)


# ---- Header ----
st.title("🔎 Smart Search AI")
st.caption("Ask anything — AI searches the web and gives you cited, grounded answers.")

# ---- Session state ----
if "messages" not in st.session_state:
    st.session_state.messages = []
if "display_history" not in st.session_state:
    st.session_state.display_history = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# ---- Sidebar ----
with st.sidebar:
    st.subheader("⚙️ Settings")

    # Language Selector
    language = st.selectbox(
        "🌍 Answer Language",
        [
            "English", "Tamil", "Hindi", "Telugu",
            "Malayalam", "Kannada", "French",
            "Spanish", "German", "Arabic", "Chinese"
        ]
    )

    # Number of sources
    num_results = st.slider("📄 Number of sources", 3, 10, 6)

    st.markdown("---")

    # Mode selector
    mode = st.radio(
        "🧭 Mode",
        ["💬 Search & Answer", "🔗 URL Summarizer", "📄 Research Report"]
    )

    st.markdown("---")

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.session_state.display_history = []
        st.session_state.pending_query = None
        st.rerun()

    st.markdown("---")
    st.caption("Built with Groq + SerpApi + Streamlit")

# ============================================================
# MODE 1 — URL Summarizer
# ============================================================
if mode == "🔗 URL Summarizer":
    st.subheader("🔗 URL Summarizer")
    st.write("Paste any URL and get an AI-generated summary instantly.")

    url_input = st.text_input(
        "Enter URL",
        placeholder="https://example.com/article"
    )

    if st.button("📖 Summarize URL"):
        if not url_input.strip():
            st.warning("Please enter a URL.")
        elif not groq_key:
            st.error("❌ Groq API key missing. Check your .env file.")
        else:
            with st.spinner("🔍 Fetching and reading page..."):
                summary = summarize_url(url_input.strip(), api_key=groq_key)
            st.markdown("### 📋 Summary")
            st.write(summary)
            st.success("✅ Done!")

# ============================================================
# MODE 2 — Research Report Generator
# ============================================================
elif mode == "📄 Research Report":
    st.subheader("📄 Research Report Generator")
    st.write("Enter any topic → get a full structured research report with citations.")

    topic_input = st.text_input(
        "Research Topic",
        placeholder="e.g. Impact of AI on healthcare in 2025"
    )

    if st.button("📊 Generate Report"):
        if not topic_input.strip():
            st.warning("Please enter a research topic.")
        elif not groq_key or not serp_key:
            st.error("❌ API keys missing. Check your .env file.")
        else:
            with st.spinner("🔍 Searching for information..."):
                results = get_search_results(
                    topic_input.strip(),
                    max_results=8,
                    api_key=serp_key
                )

            with st.spinner("📝 Writing research report — this takes ~20 seconds..."):
                report = generate_report(
                    topic=topic_input.strip(),
                    search_results=results,
                    api_key=groq_key
                )

            st.markdown(report)

            st.markdown("---")

            # Download as TXT
            st.download_button(
                label="⬇️ Download Report as .txt",
                data=report,
                file_name=f"report_{topic_input[:30].replace(' ', '_')}.txt",
                mime="text/plain"
            )

            # Show sources used
            render_sources(results, key_prefix="report")

# ============================================================
# MODE 3 — Search & Answer (Main mode)
# ============================================================
else:
    # ---- Display past conversation ----
    for t_idx, turn in enumerate(st.session_state.display_history):
        with st.chat_message("user"):
            st.write(turn["query"])
        with st.chat_message("assistant"):
            st.write(turn["answer"])
            if turn.get("sources"):
                render_sources(turn["sources"], key_prefix=f"hist_{t_idx}")
            if turn.get("related"):
                st.markdown("**🔍 People also ask:**")
                for rq in turn["related"]:
                    st.markdown(f"- {rq}")

    # ---- Determine query source ----
    # Priority: pending (related question click) > text input
    if st.session_state.pending_query:
        query = st.session_state.pending_query
        st.session_state.pending_query = None
    else:
        query = st.chat_input("💬 Ask a question...")

    # ---- Process query ----
    if query:
        if not groq_key or not serp_key:
            st.error("❌ API keys missing. Check your .env file.")
        else:
            with st.chat_message("user"):
                st.write(query)

            with st.chat_message("assistant"):

                # Step 1 — Rewrite follow-up into standalone search query
                with st.spinner("🔍 Searching the web..."):
                    search_query = build_search_query(
                        query,
                        st.session_state.messages,
                        groq_key
                    )
                    results = get_search_results(
                        search_query,
                        max_results=num_results,
                        api_key=serp_key
                    )

                # Step 2 — Get AI answer in selected language
                with st.spinner(f"🧠 Thinking in {language}..."):
                    answer = get_ai_answer(
                        query=query,
                        search_results=results,
                        chat_history=st.session_state.messages,
                        api_key=groq_key,
                        language=language
                    )

                # Step 3 — Get related questions
                with st.spinner("💡 Finding related questions..."):
                    related = get_related_questions(
                        query=query,
                        answer=answer,
                        api_key=groq_key
                    )

                # ---- Display answer ----
                st.write(answer)

                # ---- Display sources ----
                if results:
                    render_sources(results, key_prefix="live")
                else:
                    st.warning("⚠️ No search results found for this query.")

                # ---- Display related questions as clickable buttons ----
                if related:
                    st.markdown("**🔍 People also ask:**")
                    cols = st.columns(len(related))
                    for idx, rq in enumerate(related):
                        with cols[idx]:
                            if st.button(
                                rq,
                                key=f"rq_{idx}_{rq[:20]}",
                                use_container_width=True
                            ):
                                st.session_state.pending_query = rq
                                st.rerun()

            # ---- Update conversation memory ----
            st.session_state.messages.append(
                {"role": "user", "content": query}
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
            st.session_state.display_history.append({
                "query": query,
                "answer": answer,
                "sources": results,
                "related": related
            })
            