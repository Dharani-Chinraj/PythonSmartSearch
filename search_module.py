# search_module.py
import requests

def get_search_results(query: str, max_results: int = 6, api_key: str = None) -> list[dict]:
    """
    Fetches search results from SerpApi (Google Search).
    Forces IPv4 to avoid DNS resolution issues on some networks.
    """
    results = []

    if not api_key:
        return [{
            "title": "No Search API Key",
            "snippet": "SerpApi key not found. Check your .env file.",
            "url": "#"
        }]

    try:
        # Force IPv4 by using IP address directly
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": max_results,
        }

        session = requests.Session()
        session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))

        response = session.get(
            "https://serpapi.com/search",
            params=params,
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        data = response.json()

        # Check for API errors
        if "error" in data:
            return [{
                "title": "SerpApi Error",
                "snippet": f"API returned error: {data['error']}",
                "url": "#"
            }]

        organic_results = data.get("organic_results", [])

        for item in organic_results[:max_results]:
            results.append({
                "title":   item.get("title", "No title"),
                "snippet": item.get("snippet", "No description available."),
                "url":     item.get("link", "#")
            })

        if not results:
            results = [{
                "title": "No Results",
                "snippet": "No results found for this query.",
                "url": "#"
            }]

    except requests.exceptions.ConnectionError:
        results = [{
            "title": "Connection Error",
            "snippet": "Cannot reach SerpApi. Try switching to mobile hotspot.",
            "url": "#"
        }]
    except requests.exceptions.Timeout:
        results = [{
            "title": "Timeout Error",
            "snippet": "SerpApi took too long. Try again in a few seconds.",
            "url": "#"
        }]
    except Exception as e:
        results = [{
            "title": "Search Error",
            "snippet": f"Could not fetch results: {str(e)}",
            "url": "#"
        }]

    return results